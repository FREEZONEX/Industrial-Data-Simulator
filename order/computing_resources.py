from flask import Flask, request, jsonify
import psycopg2
import json
import redis
import json
import threading

import sys 
sys.path.insert(0, sys.path[0]+"/../")
from instances import simulation_instance
from celery_tasks import run_simulation, celery
from celery.result import AsyncResult

class ServiceOrderAPI:
    def __init__(self, db_config, config, mqtt_publisher):  # 数据库配置，轮训时间配置
        self.db_config = db_config
        self.config = config
        self.mqtt_publisher = mqtt_publisher
        self.latest_task_id = None
        self.r = redis.Redis(host="localhost", port=6379, db=2, decode_responses=True)
        self.app = Flask(__name__)
        self._create_table()
        self._register_routes()

    def _push_config(self):
        config = {
            "crah_101": {
                "return_air_temp": simulation_instance.crah_101.return_air_temp,
                "supply_air_temp": simulation_instance.crah_101.supply_air_temp,
                "fan_speed": simulation_instance.crah_101.fan_speed,
                "chilled_water_valve_position": simulation_instance.crah_101.chilled_water_valve_position
            },
            "chiller_201": {
                "chilled_water_leaving_temp": simulation_instance.chiller_201.chilled_water_leaving_temp,
                "chilled_water_entering_temp": simulation_instance.chiller_201.chilled_water_entering_temp,
                "compressor_load": simulation_instance.chiller_201.compressor_load,
                "total_power_consumption": simulation_instance.chiller_201.total_power_consumption
            },
            "ct_301": {
                "fan_speed": simulation_instance.ct_301.fan_speed,
                "tower_basin_temp": simulation_instance.ct_301.tower_basin_temp,
                "entering_water_temp": simulation_instance.ct_301.entering_water_temp
            },
            "cdwp_301": {},
            "chwp_201": {},
            "power_aggregator": {
                "total": simulation_instance.power_aggregator.total
            }
        }
        self.r.lpush("simulation_config", json.dumps(config))
    
    def subscribe_config(self):
        def _listener():
            pubsub = self.r.pubsub()
            pubsub.subscribe("simulation_step")
            for message in pubsub.listen():
                if message['type'] != 'message':
                    continue
                try:
                    data = json.loads(message['data'])                    
                    # --- 更新 CRAH ---
                    for k, v in data.get("crah_101", {}).items():
                        simulation_instance.crah_101.update_value(v, k)
                    
                    # --- 更新 Chiller ---
                    for k, v in data.get("chiller_201", {}).items():
                        simulation_instance.chiller_201.update_value(v, k)
                    
                    # --- 更新 CoolingTower ---
                    for k, v in data.get("ct_301", {}).items():
                        simulation_instance.ct_301.update_value(v, k)
                    
                    # --- 更新 Power Aggregator ---
                    for k, v in data.get("power_aggregator", {}).items():
                        simulation_instance.power_aggregator.update_value(v, k)
                except Exception as e:
                    print("Subscribe update fail:", e)

        t = threading.Thread(target=_listener, daemon=True)
        t.start()

    def _create_table(self):
        CREATE_TABLE_SQL = """
        CREATE EXTENSION IF NOT EXISTS "pgcrypto";
        CREATE TABLE IF NOT EXISTS service_orders (
            order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            customer_id VARCHAR(100) NOT NULL,
            requested_resources JSONB,
            duration_months INT,
            status VARCHAR(20) NOT NULL DEFAULT 'Processing',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            activated_at TIMESTAMP WITH TIME ZONE
        );
        """
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute(CREATE_TABLE_SQL)
                    print("Table 'service_orders' created or already exists.")
        except Exception as e:
            print(f"Failed to create table: {e}")

    def _register_routes(self):
        @self.app.route("/api/v1/orders", methods=["POST"])
        def create_order():
            return self.create_order(request.json)

        @self.app.route("/api/v1/orders", methods=["GET"])
        def list_order():
            return self.list_order(request.args)
        
        @self.app.route("/api/v1/config", methods=["POST"])
        def update_config():
            return self.update_config(request.json)
        
        @self.app.route("/api/v1/mqtt", methods=["POST"])
        def update_mqtt():
            return self.update_mqtt(request.json)

    def create_order(self, data):
        customer_id = data.get("customer_id")
        requested_resources = data.get("requested_resources", {})
        duration_months = data.get("duration_months", 1)

        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO service_orders (customer_id, requested_resources, duration_months)
                        VALUES (%s, %s, %s)
                        RETURNING order_id
                    """, (customer_id, json.dumps(requested_resources), duration_months))
                    order_id = cur.fetchone()[0]
                    simulation_instance.power_allocate(requested_resources)
                    print(simulation_instance.power_aggregator.compute_total_it_load())
                    if self.latest_task_id:
                        previous_task = AsyncResult(self.latest_task_id, app=celery)
                        # 只有当任务还在执行中才 revoke
                        if previous_task.state not in ('SUCCESS', 'FAILURE', 'REVOKED'):
                            previous_task.revoke(terminate=True)
                    
                    self._push_config()
                    task = run_simulation.delay()
                    self.latest_task_id = task.id

            # 仿真开始后更新订单状态
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                            UPDATE service_orders
                            SET updated_at = CURRENT_TIMESTAMP,
                                activated_at = CURRENT_TIMESTAMP,
                                status = 'Active'
                            WHERE order_id = %s
                        """, (order_id,))
                    
            return jsonify({
                "order_id": str(order_id),
                "status": "processing",
                "message": "Order received and is being processed."
            }), 200
        except Exception as e:
            return jsonify({"status": "fail", "error": str(e)}), 500

    def list_order(self, args):
        customer_id = args.get("customer_id")
        status = args.get("status")
        query = '''
            SELECT order_id, customer_id, requested_resources, duration_months, status, created_at, activated_at
            FROM service_orders
        '''
        filters = []
        params = []

        if customer_id:
            filters.append("customer_id = %s")
            params.append(customer_id)
        if status:
            filters.append("status = %s")
            params.append(status)

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY created_at DESC"

        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    rows = cur.fetchall()
                    result = []
                    for row in rows:
                        result.append({
                            "order_id": str(row[0]),
                            "customer_id": row[1],
                            "requested_resources": row[2],
                            "duration_months": row[3],
                            "status": row[4],
                            "created_at": row[5].isoformat() if row[5] else None,
                            "activated_at": row[6].isoformat() if row[6] else None
                        })
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"status": "fail", "error": str(e)}), 500
        
    def update_config(self, data):
        response = {}
        if "SERVER_UPDATE_INTERNAL" in data:
            self.config["SERVER_UPDATE_INTERNAL"] = float(data["SERVER_UPDATE_INTERNAL"])
            response["SERVER_UPDATE_INTERNAL"] = self.config["SERVER_UPDATE_INTERNAL"]
        if "RANDOM_UPDATE_INTERVAL" in data:
            self.config["RANDOM_UPDATE_INTERVAL"] = float(data["RANDOM_UPDATE_INTERVAL"])
            response["RANDOM_UPDATE_INTERVAL"] = self.config["RANDOM_UPDATE_INTERVAL"]

        return jsonify({"status": "ok", "updated": response}), 200

    def update_mqtt(self, data):
        broker = data.get("broker")
        port = data.get("port", 1883)
        if not broker:
            return jsonify({"error": "broker is required"}), 400
        
        try:
            self.mqtt_publisher.disconnect()
            self.mqtt_publisher.update_broker(broker, port)
            self.mqtt_publisher._reconnect()
            return jsonify({"message": f"MQTT broker updated to {broker}:{port}"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def run(self, host="0.0.0.0", port=5000, debug=True):
        self.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'dbname': 'mydatabase',
        'user': 'myuser',
        'password': 'mypassword'
    }
    config = {
    "SERVER_UPDATE_INTERNAL": 5.0,
    "RANDOM_UPDATE_INTERVAL": 10.0
    }

    api = ServiceOrderAPI(db_config, config)

    api.run()
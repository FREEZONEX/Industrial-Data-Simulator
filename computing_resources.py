from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime
import paho.mqtt.client as mqtt
from simulation import simulation

def simul():
    pass

db_config = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'mydatabase',
    'user': 'myuser',
    'password': 'mypassword'
}

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

# 连接数据库并执行
try:
    conn = psycopg2.connect(**db_config)
    with conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            print("Table 'service_orders' created or already exists.")
finally:
    conn.close()

app = Flask(__name__)

# 创建订单
@app.route("/api/v1/orders", methods=["POST"])
def create_order():
    data = request.json
    customer_id = data.get("customer_id")
    requested_resources = data.get("requested_resources", {})
    duration_months = data.get("duration_months", 1)

    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO service_orders (customer_id, requested_resources, duration_months)
                    VALUES (%s, %s, %s)
                    RETURNING order_id
                """, (customer_id, requested_resources, duration_months))
                order_id = cur.fetchone()[0]

                simul()  # 执行仿真

                cur.execute("""
                    UPDATE service_orders
                    SET updated_at = CURRENT_TIMESTAMP,
                        activated_at = CURRENT_TIMESTAMP,
                        status = 'Active'
                    WHERE order_id = %s
                """, (order_id,))

            return jsonify({"order_id": str(order_id), "status": "processing", "message": "Order received and is being processed."}), 201
                
    except Exception as e:
        # conn.rollback()
        return jsonify({"status": "fail", "error": str(e)}), 500

# 查询订单
@app.route("/api/v1/orders", methods=["GET"])
def list_order():
    customer_id = request.args.get("custermoer_id")
    status = request.args.get("status")
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
        with psycopg2.connect(**db_config) as conn:
            with conn.sursor as cur:
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
    
if __name__ == "__main__":
    app.run(debug=True)

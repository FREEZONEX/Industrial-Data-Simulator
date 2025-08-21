import psycopg2
from datetime import date
from devices import Runtime
import asyncio

class WorkOrderMonitor:
    def __init__(self, threshold=20, interval=1):
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'mydatabase',
            'user': 'myuser',
            'password': 'mypassword'
        }
        
        self.attributes = ['ct301', 'cdwp301', 'chiller201', 'racks', 'chwp201', 'crah101']

        self.threshold = threshold
        self.interval = interval
        self.run_time = Runtime()
        self.conn = None

    def connect_db(self):
        self.conn = psycopg2.connect(**self.db_config)

    def create_table(self):
        CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS work_orders (
            work_order_id SERIAL PRIMARY KEY,
            asset_id VARCHAR(50) NOT NULL,
            task_description TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'Scheduled',
            priority VARCHAR(10) DEFAULT 'Medium',
            scheduled_date DATE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            completed_by VARCHAR(100)
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            self.conn.commit()
        print("Table 'work_orders' is ready.")

    def insert_work_order(self, asset_id, current_value):
        with self.conn.cursor() as cur:
            task_description = f"Scheduled maintenance: {asset_id} reached runtime {current_value}"
            cur.execute("""
                INSERT INTO work_orders (asset_id, task_description, status, priority, scheduled_date, completed_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (asset_id, task_description, 'Scheduled', 'High', date.today(), "system"))
            self.conn.commit()
        print(f"Created work order for {asset_id}, runtime={current_value}")

    async def monitor_attribute(self, attr):
        while True:
            self.run_time.add_value(1, attr)
            current_value = self.run_time.get_value(attr)
            if current_value >= self.threshold:
                self.insert_work_order(attr, current_value)
                self.run_time.set_value(0, attr)
                
            await asyncio.sleep(self.interval)

    async def run(self):
        self.connect_db()
        self.create_table()

        # 为每个属性创建独立任务
        tasks = [asyncio.create_task(self.monitor_attribute(attr)) for attr in self.attributes]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    monitor = WorkOrderMonitor(threshold=5, interval=1)
    asyncio.run(monitor.run())

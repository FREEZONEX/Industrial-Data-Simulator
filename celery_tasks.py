from celery import Celery
from instances import simulation_instance

celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",   # Redis broker
    backend="redis://localhost:6379/1"   # Redis result backend
)

@celery.task(bind=True)
def run_simulation(self):
    try:
        # 执行最新的订单
        simulation_instance.simulate()
    except Exception as e:
        print("Simulation task error:", e)

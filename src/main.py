import asyncio
import time
from sensor_objects import SENSOR_SYSTEM
from sensor_tasks import TASK_MANAGER

sensor_system = SENSOR_SYSTEM()
task_manager = TASK_MANAGER(sensor_system)


async def main():
    print('starting')
    await task_manager.begin()


if(__name__ == "__main__"):
    sensor_system.start_sensors()
    task_manager.loop.run_until_complete(main())
    
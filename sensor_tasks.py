import asyncio
import time
from sensor_objects import SENSOR_QUADRANT






async def read_sensor_data(sensor_quad: SENSOR_QUADRANT):
    #read data

    await asyncio.sleep(sensor_quad.sleep_ms)




class task_manager:
    front_driver_side_task = None
    front_passenger_side_task = None
    rear_driver_side_task = None
    rear_passenger_side_task = None

import asyncio
import time
from sensor_objects import SENSOR_QUADRANT, SENSOR_SYSTEM


async def read_sensor_data(sensor_quad: SENSOR_QUADRANT):
    #read data
    print('Reading from I2C: ' + repr(sensor_quad.side.i2c_id))
    print('Reading from I2C: ' + repr(sensor_quad.center.i2c_id))
    sensor_quad.update_sleep_factor()
    await asyncio.sleep(sensor_quad.sleep_ms * sensor_quad.sleep_factor)




class TASK_MANAGER:
    front_driver_side_task = asyncio.Task
    front_passenger_side_task = asyncio.Task
    rear_driver_side_task = asyncio.Task
    rear_passenger_side_task = asyncio.Task
    _sensor_system: SENSOR_SYSTEM

    loop = None

    def __init__(self, sensor_system: SENSOR_SYSTEM):
        self._sensor_system = sensor_system
        self.loop = asyncio.get_event_loop()
        # Create Tasks for 4 Sides
        self.front_driver_side_task = self.loop.create_task(read_sensor_data(self._sensor_system.get_quadrant('front_driver')), name='front_driver_task')
        self.front_passenger_side_task = self.loop.create_task(read_sensor_data(self._sensor_system.get_quadrant('front_passenger')), name='front_passenger_task')
        self.rear_driver_side_task = self.loop.create_task(read_sensor_data(self._sensor_system.get_quadrant('rear_driver')), name='rear_driver_task')
        self.rear_passenger_side_task = self.loop.create_task(read_sensor_data(self._sensor_system.get_quadrant('rear_passenger')), name='rear_passenger_task')


    async def begin(self):
        await self.front_driver_side_task
        await self.front_passenger_side_task
        await self.rear_driver_side_task
        await self.rear_passenger_side_task

        return
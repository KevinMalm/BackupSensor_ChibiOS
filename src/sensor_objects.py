import smbus
from src.VL53L0X_api import VL53L0X_Sensor

class GPIO_PIN:
    _PIN: int
    def __init__(self, pin):
        self._PIN = pin

class MUX:
    GPIO_pins = []
    
    def __init__(self, pins: []):
        self.GPIO_pins = pins

    def set_MUX(index: int):
        return 

class SENSOR_QUADRANT:
    side: VL53L0X_Sensor
    center: VL53L0X_Sensor
    mux: MUX
    sleep_ms = 0.02
    sleep_factor = 1

    def __init__(self, mux: MUX, address_offset, bus):
        self.mux = mux

        self.side = VL53L0X_Sensor(bus, updated_address=address_offset)
        self.center = VL53L0X_Sensor(bus, updated_address=(address_offset + 1))

        self.side.DataInit()
        self.center.DataInit()

    def start_sensors(self):
        self.center.start()
        self.side.start()
    def stop_sensors(self):
        self.center.stop()
        self.side.stop()

    def update_sleep_factor(self):
        min_distance = min(self.side.get_millimeter_distance(), self.center.get_millimeter_distance())
        if(min_distance > 500):
            self.sleep_factor = 1
            return
        if(min_distance > 300):
            self.sleep_factor = 0.75
            return
        if(min_distance > 150):
            self.sleep_factor = 0.5
            return
        self.sleep_factor = 0.25
        return

class SENSOR_SYSTEM:
    _system = {}
    i2c_bus_0 = None
    i2c_bus_1 = None

    def __init__(self):
        self.i2c_bus_0 = smbus.SMBus(0)
        self.i2c_bus_1 = smbus.SMBus(1)

        _front_mux = MUX([GPIO_PIN(15), GPIO_PIN(16), ])
        _rear_mux = MUX([GPIO_PIN(15), GPIO_PIN(16), ])

        self._system['front_driver'] = SENSOR_QUADRANT(_front_mux, 0x0, self.i2c_bus_0)
        self._system['front_passenger'] = SENSOR_QUADRANT(_front_mux, 0x2, self.i2c_bus_0)
        self._system['rear_driver'] = SENSOR_QUADRANT(_rear_mux, 0x4, self.i2c_bus_1)
        self._system['rear_passenger'] = SENSOR_QUADRANT(_rear_mux, 0x6, self.i2c_bus_1)

    def start_sensors(self):
        self._system['front_driver'].start_sensors()
        self._system['front_passenger'].start_sensors()
        self._system['rear_driver'].start_sensors()
        self._system['rear_passenger'].start_sensors()
        return
 
    def stop_sensors(self):
        self._system['front_driver'].stop_sensors()
        self._system['front_passenger'].stop_sensors()
        self._system['rear_driver'].stop_sensors()
        self._system['rear_passenger'].stop_sensors()
        return

    def get_quadrant(self, key):
        return self._system[key];

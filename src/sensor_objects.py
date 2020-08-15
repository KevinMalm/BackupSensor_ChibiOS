import smbus
from src.VL53L0X_api import VL53L0X_Sensor, MUX
from gpiozero import LED


class SENSOR_POINT:
    sensor: None
    mux: DUMMY_MUX
    label = 'Point'
    last_read = 0
    def __init__(self, _mux: DUMMY_MUX, set_address, bus, base_address = 0x20, _label = 'N/A'):
        self.mux = _mux
        self.label = _label
        self.side = VL53L0X_Sensor(bus, sensor_id = address_offset, mux = mux, updated_address = (base_address + address_offset))
        print('Data Init on Sensor: ' + self.label)

    def start_sensors(self):
        print('Starting Sensor: ' + self.label)
    def stop_sensors(self):
        print('Stopping Sensor: ' + self.label)
    def get_distance(self):
        self.last_read = None

class SENSOR_QUADRANT:
    side: VL53L0X_Sensor
    center: VL53L0X_Sensor
    mux: MUX
    sleep_ms = 0.02
    sleep_factor = 1
    label = 'N/A'

    def __init__(self, mux: MUX, address_offset, bus, base_address = 0x20, _label = 'N/A'):
        self.label = _label
        self.mux = mux

        self.side = VL53L0X_Sensor(bus, sensor_id = address_offset, mux = mux, updated_address = (base_address + address_offset))
        self.center = VL53L0X_Sensor(bus, sensor_id = address_offset, mux = mux, updated_address = (base_address + address_offset + 1))

        #self.side.DataInit()
        #self.center.DataInit()

    def get_distance(self):
        return [self.center.getDistance(), self.side.getDistance()]

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
        self.i2c_bus_0 = smbus.SMBus(1)
        #print('Opening Bus 0: ' + smbus.open(self.i2c_bus_0))
        #self.i2c_bus_1 = smbus.SMBus(1)
        #print('Opening Bus 1: ' + smbus.open(self.i2c_bus_1))

        _front_mux = MUX([20, 21])
        #_rear_mux = MUX([GPIO_PIN(15), GPIO_PIN(16), ])

        self._system['front_driver'] = SENSOR_QUADRANT(_front_mux, 0x0, self.i2c_bus_0)
        #self._system['front_point'] = DUMMY_SENSOR_POINT(_front_mux, 0x10, self.i2c_bus_0, _label= 'front_point')
        #self._system['front_passenger'] = SENSOR_QUADRANT(_front_mux, 0x2, self.i2c_bus_0)
        #self._system['rear_driver'] = SENSOR_QUADRANT(_rear_mux, 0x4, self.i2c_bus_1)
        #self._system['rear_point'] = DUMMY_SENSOR_POINT(_rear_mux, 0x20, self.i2c_bus_0, _label= 'rear_point')
        #self._system['rear_passenger'] = SENSOR_QUADRANT(_rear_mux, 0x6, self.i2c_bus_1)

    def start_sensors(self):
        self._system['front_driver'].start_sensors()
        self._system['front_point'].start_sensors()
        #self._system['front_passenger'].start_sensors()
        #self._system['rear_driver'].start_sensors()
        #self._system['rear_point'].start_sensors()
        #self._system['rear_passenger'].start_sensors()
        return
 
    def stop_sensors(self):
        self._system['front_driver'].stop_sensors()
        self._system['front_point'].stop_sensors()
        #self._system['front_passenger'].stop_sensors()
        #self._system['rear_driver'].stop_sensors()
        #self._system['rear_point'].stop_sensors()
        #self._system['rear_passenger'].stop_sensors()
        return

    def get_quadrant(self, key):
        return self._system[key];


    def unpack(self):
        self._system['front_driver'].get_distance()
        #self._system['front_point'].get_distance()
        #self._system['front_passenger'].get_distance()
        #self._system['rear_driver'].get_distance()
        #self._system['rear_point'].get_distance()
        #self._system['rear_passenger'].get_distance()
        return {
            'front_driver': self._system['front_driver'].last_read,
            'front_point':self._system['front_point'].last_read,
            'front_passenger':self._system['front_passenger'].last_read,

            'rear_driver':self._system['rear_driver'].last_read,
            'rear_point':self._system['rear_point'].last_read,
            'rear_passenger':self._system['rear_passenger'].last_read
        }


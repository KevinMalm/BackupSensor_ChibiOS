
class DUMMY_GPIO_PIN:
    _PIN: int
    def __init__(self, pin):
        self._PIN = pin

class DUMMY_MUX:
    GPIO_pins = []
    
    def __init__(self, pins: []):
        self.GPIO_pins = pins

    def set_MUX(index: int):
        return 

class DUMMY_SENSOR_POINT:
    sensor: None
    mux: DUMMY_MUX
    label = 'Point'
    last_read = 0
    def __init__(self, _mux: DUMMY_MUX, set_address, bus, _label = 'UnMarked'):
        self.mux = _mux
        self.label = _label

        #self.sensor =  VL53L0X_Sensor(bus, updated_address=set_address)
        print('Data Init on Sensor: ' + self.label)

    def start_sensors(self):
        print('Starting Sensor: ' + self.label)
    def stop_sensors(self):
        print('Stopping Sensor: ' + self.label)
    def get_distance(self):
        self.last_read = None
        
class DUMMY_SENSOR_QUADRANT:
    side: None #VL53L0X_Sensor
    center: None# VL53L0X_Sensor
    mux: DUMMY_MUX
    sleep_ms = 0.02
    sleep_factor = 1
    label = 'Quad'
    last_read = [0,0]

    def __init__(self, _mux: DUMMY_MUX, address_offset, bus, _label = 'UnMarked'):
        self.mux = _mux
        self.label = _label
        #self.side = VL53L0X_Sensor(bus, updated_address=address_offset)
        #self.center = VL53L0X_Sensor(bus, updated_address=(address_offset + 1))
        print('Data Init on CENTER and SIDE in Quadrant: ' + self.label)

    def start_sensors(self):
        print('Starting CENTER and SIDE in Quadrant: ' + self.label)
    def stop_sensors(self):
        print('Stopping CENTER and SIDE in Quadrant: ' + self.label)
    def get_distance(self):
        self.last_read = [self.last_read[0] + 800, self.last_read[1] + 400]
    def update_sleep_factor(self):
        return
    

class DUMMY_SENSOR_SYSTEM:
    _system = {}
    i2c_bus_0 = None
    i2c_bus_1 = None

    def __init__(self):
        #self.i2c_bus_0 = smbus.SMBus(0)
        #print('Opening Bus 0: ' + smbus.open(self.i2c_bus_0))
        #self.i2c_bus_1 = smbus.SMBus(1)
        #print('Opening Bus 1: ' + smbus.open(self.i2c_bus_1))

        _front_mux = DUMMY_MUX([DUMMY_GPIO_PIN(16), DUMMY_GPIO_PIN(17), DUMMY_GPIO_PIN(18) ])
        _rear_mux = DUMMY_MUX([DUMMY_GPIO_PIN(13), DUMMY_GPIO_PIN(14), DUMMY_GPIO_PIN(15) ])

        self._system['front_driver'] = DUMMY_SENSOR_QUADRANT(_front_mux, 0x0, self.i2c_bus_0, _label = 'front_driver')
        self._system['front_point'] = DUMMY_SENSOR_POINT(_front_mux, 0x10, self.i2c_bus_0, _label= 'front_point')
        self._system['front_passenger'] = DUMMY_SENSOR_QUADRANT(_front_mux, 0x2, self.i2c_bus_0, _label= 'front_passenger')
    
        self._system['rear_driver'] = DUMMY_SENSOR_QUADRANT(_rear_mux, 0x4, self.i2c_bus_1, _label = 'rear_driver')
        self._system['rear_point'] = DUMMY_SENSOR_POINT(_rear_mux, 0x20, self.i2c_bus_0, _label= 'rear_point')
        self._system['rear_passenger'] = DUMMY_SENSOR_QUADRANT(_rear_mux, 0x6, self.i2c_bus_1, _label = 'rear_passenger')

    def start_sensors(self):
        self._system['front_driver'].start_sensors()
        self._system['front_point'].start_sensors()
        self._system['front_passenger'].start_sensors()
        self._system['rear_driver'].start_sensors()
        self._system['rear_point'].start_sensors()
        self._system['rear_passenger'].start_sensors()
        return
 
    def stop_sensors(self):
        self._system['front_driver'].stop_sensors()
        self._system['front_point'].stop_sensors()
        self._system['front_passenger'].stop_sensors()
        self._system['rear_driver'].stop_sensors()
        self._system['rear_point'].stop_sensors()
        self._system['rear_passenger'].stop_sensors()
        return

    def read_quadrant(self, key):
        return self._system[key];

    def unpack(self):
        self._system['front_driver'].get_distance()
        self._system['front_point'].get_distance()
        self._system['front_passenger'].get_distance()
        self._system['rear_driver'].get_distance()
        self._system['rear_point'].get_distance()
        self._system['rear_passenger'].get_distance()
        return {
            'front_driver': self._system['front_driver'].last_read,
            'front_point':self._system['front_point'].last_read,
            'front_passenger':self._system['front_passenger'].last_read,

            'rear_driver':self._system['rear_driver'].last_read,
            'rear_point':self._system['rear_point'].last_read,
            'rear_passenger':self._system['rear_passenger'].last_read
        }



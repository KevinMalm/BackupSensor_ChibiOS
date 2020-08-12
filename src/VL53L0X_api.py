import smbus

mode_CONTINUOUS = "CONTINUOUS"
mode_SINGLE = "SINGLE"
precision_HIGH = "HIGH"
precision_LOW = "LOW"
VL53L0x_MAX_LOOP = 200

class VL53L0X_Sensor:
    address = 0x52
    i2c_bus = None
    mode =  mode_CONTINUOUS
    percision = 'HIGH'

    lastest_result = {}

    def __init__(self, i2c_bus, address = 0x52, updated_address = 0x52):
        self.address = address
        self.i2c_bus = i2c_bus

        self.DataInit()
        self.setDeviceAddress(updated_address)
        self.setMode(mode_CONTINUOUS, precision_LOW)
    
    def DataInit(self):
        if(self.i2c_bus == None):
            return None
        data = 0
        data = self.i2c_bus.write_byte_data(self.address, 0x88, 0x00)
        data = self.i2c_bus.write_byte_data(self.address, 0x80, 0x01)
        data = self.i2c_bus.write_byte_data(self.address, 0xFF, 0x01)
        data = self.i2c_bus.write_byte_data(self.address, 0x00, 0x00)
        data = self.i2c_bus.write_byte_data(self.address, 0x88, 0x00)
        data = self.i2c_bus.write_byte_data(self.address, 0x88, 0x00)
        data = self.i2c_bus.read_byte_data(self.address, 0x91)
        print('Retrieved Data from 0x91: ' + repr(data))
        data = self.i2c_bus.write_byte_data(self.address, 0x91, 0x3c)
        data = self.i2c_bus.write_byte_data(self.address, 0x00, 0x01)
        data = self.i2c_bus.write_byte_data(self.address, 0xFF, 0x00)
        data = self.i2c_bus.write_byte_data(self.address, 0x80, 0x00)

        return
    
    def start(self):
        data = 0
        data = self.i2c_bus.write_byte_data(self.address, 0x80, 0x01)
        data = self.i2c_bus.write_byte_data(self.address, 0xFF, 0x01)
        data = self.i2c_bus.write_byte_data(self.address, 0x00, 0x00)
        data = self.i2c_bus.write_byte_data(self.address, 0x91, 0x3c)
        data = self.i2c_bus.write_byte_data(self.address, 0x00, 0x01)
        data = self.i2c_bus.write_byte_data(self.address, 0xFF, 0x00)
        data = self.i2c_bus.write_byte_data(self.address, 0x80, 0x00)

        if(self.mode == mode_CONTINUOUS):
            data = self.i2c_bus.write_byte_data(self.address, 0x00, 0x01)
            byte = 0x01
            loopNB = 0

            while(((byte & 0x1) == 0x1) and (loopNB < VL53L0x_MAX_LOOP)):
                if(loopNB > 0):
                    byte = self.i2c_bus.read_byte(self.address, 0x00)
        elif(self.mode == mode_CONTINUOUS):
            self.i2c_bus.write_byte_data(self.address, 0x00, 0x02)
        else:
            print('Invalid Device Mode: ' + repr(self.mode))

        return

    def stop(self):
        data = self.i2c_bus.write_byte_data(self.address, 0x00, 0x00)
        data = self.i2c_bus.write_byte_data(self.address, 0xFF, 0x01)
        data = self.i2c_bus.write_byte_data(self.address, 0x00, 0x00)
        data = self.i2c_bus.write_byte_data(self.address, 0x91, 0x00)
        data = self.i2c_bus.write_byte_data(self.address, 0x00, 0x01)
        data = self.i2c_bus.write_byte_data(self.address, 0xFF, 0x00)

        return

    def read_data(self, reg, n):
        data = []
        for i in range(n):
            data.append(self.i2c_bus.read_byte_data(self.address, reg + i))
        return data
    
    def getDistance(self):
        distance = -1
        result = {}
        data = self.read_data(0x14, 12)

        result['ambientCount'] = ((data[6] & 0xFF) << 8) | ((data[7] & 0xFF))
        result['signalCount']  = ((data[8] & 0xFF) << 8) | ((data[9] & 0xFF))
        result['distance']     = ((data[10] & 0xFF) << 8) | ((data[11] & 0xFF))
        result['status']       = ((data[0] & 0x78) >> 3)

        self.lastest_result = result

        return result['distance']

    def setDeviceAddress(self, new_address):
        new_address &= 0x7F;
        data = 0
        data = self.i2c_bus.write_byte_data(self.address, 0x8a, new_address)
        self.address = new_address
        return 
    def setMode(self, mode, precision):
        self.sensor_mode = mode
        if(precision == precision_HIGH):
            data = self.i2c_bus.write_byte_data(self.address, 0x09, 0x0)
        else:
            data = self.i2c_bus.write_byte_data(self.address, 0x09, 0xFF)
        self.precision = precision
        return
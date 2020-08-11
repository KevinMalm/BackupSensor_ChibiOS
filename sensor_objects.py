

class SENSOR:
    i2c_id = 0x52


class SENSOR_QUADRANT:
    side: SENSOR
    center: SENSOR

    sleep_ms: int

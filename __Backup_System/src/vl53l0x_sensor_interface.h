#include "vl53l0x_api.h"
#include "ch.h"
#include "hal.h"
typedef struct {
    double last_reading;
    int id; // multiplex id 
    VL53L0X_RangingMeasurementData_t distance_rating; // directly coresponding to how many bars are drawn on the screen
    VL53L0X_Dev_t device;
} SENSOR;

typedef struct {
    int PAD;
    gpio_port_t PORT;
} GPIO_PIN;

typedef struct {
    GPIO_PIN _pin_a;
    GPIO_PIN _pin_b;
} MUX;

typedef struct {
    SENSOR side;
    SENSOR center;
    MUX mux;
    float refresh_rate;
} SENSOR_QUADRANT;

/*
typedef struct {
    SENSOR driver_right;
    SENSOR driver_center;
    SENSOR passenger_center;
    SENSOR passenger_left;
    MUX mux;
    float driver_side_refresh_factor;
    float passenger_side_refresh_factor;
} SENSOR_ARRAY;
*/


typedef struct {
    SENSOR_QUADRANT front_driver;
    SENSOR_QUADRANT front_passenger;
    SENSOR_QUADRANT rear_driver;
    SENSOR_QUADRANT rear_passenger;
} SENSOR_SYSTEM;

static VL53L0X_Error setupSensors(SENSOR_SYSTEM);
static VL53L0X_Error setup_sensor_array(SENSOR_QUADRANT);
static VL53L0X_Error individual_sensor(SENSOR, MUX);
static VL53L0X_Error setup_device_address(SENSOR_QUADRANT, int);
static VL53L0X_Error poll_device_values(SENSOR_QUADRANT);
static VL53L0X_Error poll_individual_measurement_value(SENSOR, MUX);

void setup_mux_GPIO(MUX);
void set_mux_GPIO(MUX, uint8_t);
float update_refresh_rate(uint16_t);

/*
    General Setup Call
    Handles: 
        I2C Address Setup
        MUX Setup
        VL53L0X Sensor Setup (via I2C)
*/
static VL53L0X_Error setup_sensors(SENSOR_SYSTEM system){
    VL53L0X_Error error_code = VL53L0X_ERROR_NONE;

    error_code = setup_device_address(system.front_driver, 0) | setup_device_address(system.front_passenger, 2) | setup_device_address(system.rear_driver, 0) | setup_device_address(system.rear_passenger, 2);

    if(error_code != VL53L0X_ERROR_NONE)
        return error_code;

    error_code = setup_sensor_array(system.front_driver) | setup_sensor_array(system.front_passenger) | setup_sensor_array(system.rear_driver) | setup_sensor_array(system.rear_passenger);

    return error_code;

}

/*
    Sets up I2C Address for all 4 Sensors 
    Codec: 
        Driver's Side       Far     {0}
        Driver's Side       Center  {1}
        Passengers's Side   Center  {2}
        Passengers's Side   Far     {3}

*/
static VL53L0X_Error setup_device_address(SENSOR_QUADRANT array, int id_offset) {
    uint8_t id = id_offset;
    VL53L0X_Error error_code = VL53L0X_ERROR_NONE;
    
    error_code |= VL53L0X_SetDeviceAddress(&array.side.device, id);
    array.side.id = id;
        id++;

    error_code |= VL53L0X_SetDeviceAddress(&array.center.device, id);
    array.center.id = id;
        
    return error_code;
}

/*
    Wrapper Function that sets up each Individual Sensor 
*/
static VL53L0X_Error setup_sensor_array(SENSOR_QUADRANT array) {
    VL53L0X_Error error_code = VL53L0X_ERROR_NONE;

    error_code = individual_sensor(array.side, array.mux);
        if(error_code) { return error_code; }
    error_code = individual_sensor(array.center, array.mux);
    
    return error_code;
}

/*
    Preforms Sensor Setup and Calibration for Init set up via I2C
*/
static VL53L0X_Error individual_sensor(SENSOR lcl_sensor, MUX mux){
    //Ensure MUX is connecting correct Sensor 
    set_mux_GPIO(mux, lcl_sensor.id);

    VL53L0X_Error error_code = VL53L0X_ERROR_NONE;
    uint8_t VHV_settings = 0;
    uint8_t phaseCal = 0;
    uint32_t ref_SpadCount = 0;
    uint8_t aperture_Spads = 0;


    error_code = VL53L0X_DataInit(&lcl_sensor.device);
        if(error_code) { return error_code; }
    error_code = VL53L0X_StaticInit(&lcl_sensor.device);
        if(error_code) { return error_code; }
    error_code = VL53L0X_PerformRefCalibration(&lcl_sensor.device, &VHV_settings, &phaseCal);
        if(error_code) { return error_code; }
    error_code = VL53L0X_PerformRefSpadManagement(&lcl_sensor.device, &ref_SpadCount, &aperture_Spads);
        if(error_code) { return error_code; }
    error_code = VL53L0X_SetDeviceMode(&lcl_sensor.device, VL53L0X_DEVICEMODE_CONTINUOUS_RANGING);
        if(error_code) { return error_code; }

    //Let's up High Speed Configuration
    error_code = VL53L0X_SetLimitCheckEnable(&lcl_sensor.device, VL53L0X_CHECKENABLE_SIGMA_FINAL_RANGE, 1);
        if(error_code) { return error_code; }

    error_code = VL53L0X_SetLimitCheckEnable(&lcl_sensor.device, VL53L0X_CHECKENABLE_SIGNAL_RATE_FINAL_RANGE, 1);
        if(error_code) { return error_code; }
    error_code = VL53L0X_SetLimitCheckValue(&lcl_sensor.device, VL53L0X_CHECKENABLE_SIGNAL_RATE_FINAL_RANGE, (FixPoint1616_t) (0.25 * 65536));
        if(error_code) { return error_code; }
    error_code = VL53L0X_SetLimitCheckValue(&lcl_sensor.device, VL53L0X_CHECKENABLE_SIGMA_FINAL_RANGE, (FixPoint1616_t) (32 * 65536));
        if(error_code) { return error_code; }
    error_code = VL53L0X_SetMeasurementTimingBudgetMicroSeconds(&lcl_sensor.device, 20000);
        if(error_code) { return error_code; }

    return error_code;
} 

/*
    Updates distance_rating values in individual SENSOR structs
*/
static VL53L0X_Error poll_device_values(SENSOR_QUADRANT array_in){
    VL53L0X_Error error = VL53L0X_ERROR_NONE;

    error |= poll_individual_measurement_value(array_in.side, array_in.mux);
    error |= poll_individual_measurement_value(array_in.center, array_in.mux);


    return error;
}
static VL53L0X_Error poll_individual_measurement_value(SENSOR in, MUX mux){
    VL53L0X_Error error = VL53L0X_ERROR_NONE;
    set_mux_GPIO(mux, in.id);
    error = VL53L0X_GetMeasurementDataReady(&in.device, &in.distance_rating);

    return error;
}


/*
    Initializes Pins in MUX struct to be Outputs and Resets them
*/
void setup_mux_GPIO(MUX mux){
    //Set MODER as Output
    palSetPadMode(&mux._pin_a.PORT, mux._pin_a.PAD, PAL_MODE_OUTPUT);
    palSetPadMode(&mux._pin_b.PORT, mux._pin_b.PAD, PAL_MODE_OUTPUT);
    //Ensure Pins are reset
    palClearPad(&mux._pin_a.PORT, mux._pin_a.PAD);
    palClearPad(&mux._pin_b.PORT, mux._pin_b.PAD);
    return;
}

/*
    Sets MUX output
*/
void set_mux_GPIO(MUX mux, uint8_t v){    
    uint8_t a = v & 0x1;
    uint8_t b = v & 0x2;
    if(a) { palSetPad(&mux._pin_a.PORT, mux._pin_a.PAD); } else { palClearPad(&mux._pin_a.PORT, mux._pin_a.PAD); }
    if(b) { palSetPad(&mux._pin_b.PORT, mux._pin_b.PAD); } else { palClearPad(&mux._pin_b.PORT, mux._pin_b.PAD); }
}


float update_refresh_rate(uint16_t distance) {
    if(distance > 914) // + 3 Feet Away
        return 1.0f; 
    if(distance > 600) // 2 - 3 Feet Away
        return 0.75f;
    if(distance > 457) // 1.5 - 2 Feet Away
        return 0.5f;
    return 0.25f; // CLOSE!
}
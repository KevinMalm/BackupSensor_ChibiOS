#include "vl53l0x_api.h"

typedef struct {
    double last_reading;
    int id; // multiplex id 
    int GPIO_PIN;
    int distance_rating; // directly coresponding to how many bars are drawn on the screen
    VL53L0X_Dev_t device;
} SENSOR;

typedef struct {
    SENSOR right;
    SENSOR center;
    SENSOR left;
} SENSOR_ARRAY;

static VL53L0X_Error setupSensors(SENSOR_ARRAY, SENSOR_ARRAY);
static VL53L0X_Error setup_sensor_array(SENSOR_ARRAY array);
static VL53L0X_Error individual_sensor(SENSOR);

static VL53L0X_Error setup_sensors(SENSOR_ARRAY front, SENSOR_ARRAY back){
    VL53L0X_Error error_code = VL53L0X_ERROR_NONE;
    error_code |= setup_sensor_array(front);
    error_code |= setup_sensor_array(front);

    return error_code;
}

static VL53L0X_Error setup_sensor_array(SENSOR_ARRAY array){
    VL53L0X_Error error_code = VL53L0X_ERROR_NONE;

    error_code = individual_sensor(array.right);
        if(error_code) { return error_code; }
    error_code = individual_sensor(array.center);
        if(error_code) { return error_code; }  
    error_code = individual_sensor(array.left);
        if(error_code) { return error_code; }
    
    return error_code;
}

static VL53L0X_Error individual_sensor(SENSOR lcl_sensor){
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
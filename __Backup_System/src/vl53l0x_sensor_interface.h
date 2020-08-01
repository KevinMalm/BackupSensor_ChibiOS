#include "vl53l0x_api.h"

typedef struct {
    double last_reading;
    int id; // multiplex id 
    int GPIO_PIN;
    int distance_rating; // directly coresponding to how many bars are drawn on the screen
    VL53L0X_Dev_t device;
} SENSOR;

typedef struct {
    short hex_address_offset;
    SENSOR right;
    SENSOR center;
    SENSOR left;
} SENSOR_ARRAY;

typedef struct {
    ONBOARD_LED_PAD PAD;
    ONBOARD_LED_PORT PORT;
} GPIO_PIN;


#define A_PAD 0
#define B_PAD 0
#define C_PAD 0
#define D_PAD 0
#define A_PORT 0
#define B_PORT 0
#define C_PORT 0
#define D_PORT 0

static VL53L0X_Error setupSensors(SENSOR_ARRAY, SENSOR_ARRAY);
static VL53L0X_Error setup_sensor_array(SENSOR_ARRAY);
static VL53L0X_Error individual_sensor(SENSOR);
static VL53L0X_Error setup_device_address(SENSOR_ARRAY);

void setup_multiplexer_board(void);
static short set_mutiplexer(short);




static VL53L0X_Error setup_sensors(SENSOR_ARRAY front, SENSOR_ARRAY rear){
    setup_multiplexer_board();

    // 1 -> 2 -> 3
    front.hex_address_offset = 0x00; // 000000(**) -> 0
    rear.hex_address_offset = 0x06; // 000001(**) -> 6

    VL53L0X_Error error_code = VL53L0X_ERROR_NONE;

    error_code = setup_device_address(front) | setup_device_address(rear);

    if(error_code != VL53L0X_ERROR_NONE)
        return error_code;

    error_code = setup_sensor_array(front) | setup_sensor_array(rear);

    return error_code;

}

static VL53L0X_Error setup_device_address(SENSOR_ARRAY array) {
    static uint8_t id = 0x0;
    VL53L0X_Error error_code = VL53L0X_ERROR_NONE;
    
    //set mulex to array.hex_address_offset | id
    array.right.id = id;
    set_mutiplexer(array.hex_address_offset | id);
    error_code |= VL53L0X_SetDeviceAddress(&array.right.device, array.hex_address_offset | id);
    id++;
    array.right.id = id;
    set_mutiplexer(array.hex_address_offset | id);
    error_code |= VL53L0X_SetDeviceAddress(&array.center.device, array.hex_address_offset | id);
    id++;
    array.right.id = id;
    set_mutiplexer(array.hex_address_offset | id);
    error_code |= VL53L0X_SetDeviceAddress(&array.left.device, array.hex_address_offset | id);
    return error_code;
}

static VL53L0X_Error setup_sensor_array(SENSOR_ARRAY array) {
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

void setup_multiplexer_board(){
// ------------------------------------
    palSetPadMode(A_PORT, A_PAD, PAL_MODE_OUTPUT);
    palSetPadMode(B_PORT, B_PAD, PAL_MODE_OUTPUT);
    palSetPadMode(C_PORT, C_PAD, PAL_MODE_OUTPUT);
    palSetPadMode(D_PORT, D_PAD, PAL_MODE_OUTPUT);
// ------------------------------------
    palClearPad(A_PORT, A_PAD);
    palClearPad(B_PORT, B_PAD);
    palClearPad(C_PORT, C_PAD);
    palClearPad(D_PORT, D_PAD);
// ------------------------------------
    return;
}


static short set_mutiplexer(short address) {
    if(address == -1){
        palClearPad(A_PORT, A_PAD);
        palClearPad(B_PORT, B_PAD);
        palClearPad(C_PORT, C_PAD);
        palClearPad(D_PORT, D_PAD); 
    }
    short a = address & (0x1);
    short b = address & (0x2);
    short c = address & (0x3);
    if(a) { palSetPad(A_PORT, A_PAD); } else { palClearPad(A_PORT, A_PAD); }
    if(b) { palSetPad(B_PORT, B_PAD); } else { palClearPad(B_PORT, B_PAD); }
    if(c) { palSetPad(C_PORT, C_PAD); } else { palClearPad(C_PORT, C_PAD); }
    if(d) { palSetPad(D_PORT, D_PAD); } else { palClearPad(D_PORT, D_PAD); }
    return address;
}

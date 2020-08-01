#include "hal.h"
#include "vl53l0x_api.h"


void blink(int n, int a, int b){
    for(int i = 0; i < n; i ++){
        if(a)
            palSetPad(GPIO16_PORT, GPIO16_PAD);
        if(b)
            palSetPad(GPIO12_PORT, GPIO12_PAD);
        halPolledDelay(500000);
        if(b)
            palClearPad(GPIO12_PORT, GPIO12_PAD);
        if(a)
            palClearPad(GPIO16_PORT, GPIO16_PAD);
        halPolledDelay(500000);
    }
    halPolledDelay(800000);
    return;
}


void check_error_vl53(VL53L0X_Error e){
    switch(e){
        case(VL53L0X_ERROR_NONE):
            blink(2,1,0);
            break;
        case(VL53L0X_ERROR_CALIBRATION_WARNING):
            blink(1,0,1);
            break;
        case(VL53L0X_ERROR_MIN_CLIPPED):
            blink(2,0,1);
            break;
        case(VL53L0X_ERROR_UNDEFINED):
            blink(3,0,1);
            break;
        case(VL53L0X_ERROR_INVALID_PARAMS):
            blink(4,0,1);
            break;
        case(VL53L0X_ERROR_NOT_SUPPORTED):
            blink(5,0,1);
            break;
        case(VL53L0X_ERROR_RANGE_ERROR):
            blink(1,1,1);
            break;
        case(VL53L0X_ERROR_TIME_OUT):
            blink(2,1,1);
            break;
        case(VL53L0X_ERROR_MODE_NOT_SUPPORTED):
            blink(3,1,1);
            break;
        case(VL53L0X_ERROR_BUFFER_TOO_SMALL):
            blink(4,1,1);
            break;
        case(VL53L0X_ERROR_GPIO_NOT_EXISTING):
            blink(5,1,1);
            break;
        case(VL53L0X_ERROR_GPIO_FUNCTIONALITY_NOT_SUPPORTED):
            blink(1,0,1);
            blink(1,1,1);
            break;
        case(VL53L0X_ERROR_INTERRUPT_NOT_CLEARED):
            blink(2,0,1);
            blink(2,1,1);
            break;
        case(VL53L0X_ERROR_CONTROL_INTERFACE):
            blink(3,0,1);
            blink(3,1,1);
            break;
        case(VL53L0X_ERROR_INVALID_COMMAND):
            blink(1,1,1);
            blink(1,0,1);
            blink(1,1,0);
            break;
         case(VL53L0X_ERROR_DIVISION_BY_ZERO):
            blink(1,1,1);
            blink(2,0,1);
            blink(1,1,0);
            break;
        case(VL53L0X_ERROR_REF_SPAD_INIT):
            blink(1,1,1);
            blink(3,0,1);
            blink(1,1,0);
            break;
        case(VL53L0X_ERROR_NOT_IMPLEMENTED):
            blink(1,1,1);
            blink(4,0,1);
            blink(1,1,0);
            break;
        default:
            blink(1,1,1);
            blink(1,0,1);
            blink(1,1,0);
            blink(1,1,1);
            break;
    }



    return;

}

void check_error(VL53L0X_Error e){
    if(e == -10010){
        palClearPad(GPIO12_PORT, GPIO12_PAD);
        palSetPad(GPIO16_PORT, GPIO16_PAD);
        return;
    }
    if(e){
        palSetPad(GPIO16_PORT, GPIO16_PAD);
        palClearPad(GPIO12_PORT, GPIO12_PAD);
        return;
    }
    palClearPad(GPIO16_PORT, GPIO16_PAD);
    palSetPad(GPIO12_PORT, GPIO12_PAD);
    return;
}
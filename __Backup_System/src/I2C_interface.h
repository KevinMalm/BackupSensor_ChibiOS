#include "vl53l0x_platform.h"
#include "i2c_lld.h"
#include "hal.h"

#define VL53L0X_MAX_I2C_XFER_SIZE   64 /* Maximum buffer size to be used in i2c */


static int I2C_setup(){
    I2CConfig i2cConfig = {
        1,
        100000,
        2,
    };
    i2cStart(&I2C1, &i2cConfig);
    return 1;
}


VL53L0X_Error VL53L0X_RdByte (VL53L0X_DEV  Dev, uint8_t  index, uint8_t *  data) {

    i2cAcquireBus(&I2C1);
    msg_t status = i2cMasterReceiveTimeout(&I2C1, Dev->I2cDevAddr, data, 1, MS2ST(1000));
    i2cReleaseBus(&I2C1);

    if(status == RDY_OK)
        return VL53L0X_ERROR_NONE;
	return (VL53L0X_Error)status;
}

VL53L0X_Error VL53L0X_WrByte (VL53L0X_DEV Dev, uint8_t index, uint8_t data)  {

    uint8_t request[2];
    request[0] = index;
    request[1] = data;

    i2cAcquireBus(&I2C1);
    msg_t status = i2cMasterTransmitTimeout(&I2C1, Dev->I2cDevAddr, request, 2, NULL, 0, MS2ST(2000)); //i2cMasterTransmitTimeout
    i2cReleaseBus(&I2C1);


    if(status == RDY_OK)
        return VL53L0X_ERROR_NONE;
	return (VL53L0X_Error)status;
}

VL53L0X_Error VL53L0X_PollingDelay (VL53L0X_DEV  Dev){
	return (VL53L0X_Error)-1;
}

VL53L0X_Error VL53L0X_WriteMulti (VL53L0X_DEV Dev, uint8_t index, uint8_t *pdata, uint32_t count){

    VL53L0X_Error error_code = VL53L0X_ERROR_NONE;
    if(count >= VL53L0X_MAX_I2C_XFER_SIZE) {
        error_code = VL53L0X_ERROR_INVALID_PARAMS;
    }
    for (size_t i = 0; i < count; i++) {
        /* code */
        uint8_t data_out = pdata[i];
        error_code = VL53L0X_WrByte(Dev, index, data_out);
        if(error_code != 0)
            return VL53L0X_ERROR_CONTROL_INTERFACE;
    }

    return VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_ReadMulti (VL53L0X_DEV Dev, uint8_t index, uint8_t *pdata, uint32_t count){
    VL53L0X_Error error_code = VL53L0X_ERROR_NONE;
    if(count >= VL53L0X_MAX_I2C_XFER_SIZE) {
        error_code = VL53L0X_ERROR_INVALID_PARAMS;
    }

    for (int i = 0; i < count; i++) {
        /* code */
        uint8_t data_in;
        error_code = VL53L0X_RdByte(Dev, index, &data_in);
        if(error_code != 0)
            return VL53L0X_ERROR_CONTROL_INTERFACE;
        pdata[i] = data_in;
    }
    

    return VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_WrWord (VL53L0X_DEV Dev, uint8_t index, uint16_t data){
    uint8_t request[3];
    request[0] = index;
    request[1] = (data >> 8); //top half
    request[2] = (data & 0xFF); //bottom half 

    i2cAcquireBus(&I2C1);
    msg_t status = i2cMasterTransmitTimeout(&I2C1, Dev->I2cDevAddr, request, 3, NULL, 0, MS2ST(1000));
    i2cReleaseBus(&I2C1);

    if(status == RDY_OK)
        return VL53L0X_ERROR_NONE;
	return (VL53L0X_Error)status;
}

VL53L0X_Error VL53L0X_WrDWord (VL53L0X_DEV Dev, uint8_t index, uint32_t data){
    uint8_t request[5];
    request[0] = index;
    request[1] = (data >> 24); //top quater
    request[2] = ((data >> 16) & 0xFF); //3rd quater 
    request[3] = ((data >> 8) & 0xFF); //2nd quater 
    request[4] = (data & 0xFF); //1st quater 

    i2cAcquireBus(&I2C1);
    msg_t status = i2cMasterTransmitTimeout(&I2C1, Dev->I2cDevAddr, request, 5, NULL, 0, MS2ST(1000));
    i2cReleaseBus(&I2C1);


    if(status == RDY_OK)
        return VL53L0X_ERROR_NONE;
	return (VL53L0X_Error)status;
}
VL53L0X_Error VL53L0X_RdWord (VL53L0X_DEV Dev, uint8_t index, uint16_t *data){
    i2cAcquireBus(&I2C1);
    msg_t status = i2cMasterReceiveTimeout(&I2C1, Dev->I2cDevAddr, data, 2, MS2ST(1000));
    i2cReleaseBus(&I2C1);
    
    if(status == RDY_OK){
        return VL53L0X_ERROR_NONE;
    }
	return (VL53L0X_Error)status;
}
VL53L0X_Error VL53L0X_RdDWord (VL53L0X_DEV Dev, uint8_t index, uint32_t *data){
    i2cAcquireBus(&I2C1);

    msg_t status = i2cMasterReceiveTimeout(&I2C1, Dev->I2cDevAddr, data, 4, MS2ST(1000));
    i2cReleaseBus(&I2C1);

    if(status == RDY_OK)
        return VL53L0X_ERROR_NONE;
	return (VL53L0X_Error)status;
}
VL53L0X_Error VL53L0X_UpdateByte (VL53L0X_DEV Dev, uint8_t index, uint8_t AndData, uint8_t OrData){
    uint8_t request[2];
    uint8_t data;
    request[0] = index;
    request[1] = data;

    i2cAcquireBus(&I2C1);

    msg_t status = i2cMasterReceiveTimeout(&I2C1, Dev->I2cDevAddr, data, 4, MS2ST(1000));
    
    i2cReleaseBus(&I2C1);

    if(status != RDY_OK)
        return VL53L0X_ERROR_CONTROL_INTERFACE;
    
    data = (data & AndData) | OrData;
    status = i2cMasterTransmitTimeout(&I2C1, Dev->I2cDevAddr, request, 2, NULL, 0, MS2ST(1000));

    if(status == RDY_OK)
        return VL53L0X_ERROR_NONE;
	return (VL53L0X_Error)status;
}
//i2cMasterReceiveTimeout
/*
    ChibiOS/RT - Copyright (C) 2006,2007,2008,2009,2010,
                 2011,2012 Giovanni Di Sirio.

    This file is part of ChibiOS/RT.

    ChibiOS/RT is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    ChibiOS/RT is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "ch.h"
#include "hal.h"
#include "test.h"
#include "shell.h"
#include "chprintf.h"
#include "src/I2C_interface.h"
#include "vl53l0x_api.h"
#include "src/vl53l0x_sensor_interface.h"
#include "src/error_check.h"

#define SHELL_WA_SIZE       THD_WA_SIZE(4096)

#ifdef EXTENDED_SHELL

#define TEST_WA_SIZE        THD_WA_SIZE(4096)

static void cmd_mem(BaseSequentialStream *chp, int argc, char *argv[]) {
  size_t n, size;

  UNUSED(argv);
  if (argc > 0) {
    chprintf(chp, "Usage: mem\r\n");
    return;
  }
  n = chHeapStatus(NULL, &size);
  chprintf(chp, "core free memory : %u bytes\r\n", chCoreStatus());
  chprintf(chp, "heap fragments   : %u\r\n", n);
  chprintf(chp, "heap free total  : %u bytes\r\n", size);
}

static void cmd_threads(BaseSequentialStream *chp, int argc, char *argv[]) {
  static const char *states[] = {THD_STATE_NAMES};
  Thread *tp;

  UNUSED(argv);
  if (argc > 0) {
    chprintf(chp, "Usage: threads\r\n");
    return;
  }
  chprintf(chp, "    addr    stack prio refs     state time    name\r\n");
  tp = chRegFirstThread();
  do {
    chprintf(chp, "%.8lx %.8lx %4lu %4lu %9s %-8lu %s\r\n",
            (uint32_t)tp, (uint32_t)tp->p_ctx.r13,
            (uint32_t)tp->p_prio, (uint32_t)(tp->p_refs - 1),
			 states[tp->p_state], (uint32_t)tp->p_time, tp->p_name);
    tp = chRegNextThread(tp);
  } while (tp != NULL);
}

static void cmd_test(BaseSequentialStream *chp, int argc, char *argv[]) {
  Thread *tp;

  UNUSED(argv);
  if (argc > 0) {
    chprintf(chp, "Usage: test\r\n");
    return;
  }
  tp = chThdCreateFromHeap(NULL, TEST_WA_SIZE, chThdGetPriority(),
                           TestThread, chp);
  if (tp == NULL) {
    chprintf(chp, "out of memory\r\n");
    return;
  }
  chThdWait(tp);
}

#endif // EXTENDED_SHELL

SENSOR_ARRAY front_array;
SENSOR_ARRAY rear_array;


static void cmd_reboot(BaseSequentialStream *chp, int argc, char *argv[]) {
  UNUSED(argv);
  if (argc > 0) {
    chprintf(chp, "Usage: reboot\r\n");
    return;
  }

  /* Watchdog will cause reset after 1 tick.*/
  watchdog_start(1);
}

static const ShellCommand commands[] = {
#ifdef EXTENDED_SHELL
  {"mem", cmd_mem},
  {"threads", cmd_threads},
  {"test", cmd_test},
#endif
  {"reboot", cmd_reboot},
  {NULL, NULL}
};

static const ShellConfig shell_config = {
  (BaseSequentialStream *)&SD1,
  commands
};



/******
 * 
 *  | ____________________
 *                        | (0xXXX)
 *               -----------------
 *  | --CLOCK-- |                 - 0x000 -> front right
 *  | --DATA--- |                 - 0x001 -> front center
 *              |                 - 0x010 -> front left
 *              |                 
 *              |                 - 0x100 -> rear right
 *              |                 - 0x101 -> rear center
 *              |                 - 0x110 -> rear left
 *              |                 
 *              |                 - 0x111 -> {all}                
 *               -----------------
 *
 ******/


static WORKING_AREA(waThread1, 128);
static WORKING_AREA(waThread2, 128);

static msg_t front_thread(void *p) {
  (void)p;
  chRegSetThreadName("front_");
  while (TRUE) {
    palClearPad(ONBOARD_LED_PORT, ONBOARD_LED_PAD);
    chThdSleepMilliseconds(2000);
    palSetPad(ONBOARD_LED_PORT, ONBOARD_LED_PAD);
    chThdSleepMilliseconds(20000);
  }
  return 0;
}
static msg_t rear_thread(void *p) {
  (void)p;
  VL53L0X_Error Status = VL53L0X_ERROR_NONE;
  VL53L0X_RangingMeasurementData_t  RangingMeasurementData;
  chRegSetThreadName("rear_");
  while (TRUE) {
    Status = VL53L0X_GetMeasurementDataReady(&front_array.center.device,
            		&RangingMeasurementData);
    if(RangingMeasurementData.RangeMilliMeter < 15){
          palClearPad(ONBOARD_LED_PORT, ONBOARD_LED_PAD);
    } else {
          palSetPad(ONBOARD_LED_PORT, ONBOARD_LED_PAD);
    }
    chThdSleepMilliseconds(20000);
  }
  return 0;
}

/* Application entry point */
int main(void) {

  halInit();
  chSysInit();

  /* Serial port initialization */
  sdStart(&SD1, NULL); 
  chprintf((BaseSequentialStream *)&SD1, "Main (SD1 started)\r\n");

  /* Shell initialization */
  shellInit();
  shellCreate(&shell_config, SHELL_WA_SIZE, NORMALPRIO + 1);

  /* Sensor and I2C initialization */
  I2C_setup();
  check_error_vl53(setup_sensors(front_array, rear_array));
  chThdWait(chThdSelf());

  check_error_vl53(start_measurements(front_array));
  check_error_vl53(start_measurements(rear_array));
  blink(10, 1, 1);
  check_error(VL53L0X_StartMeasurement(&front_array.center.device));
  blink(10, 1, 1);

  chThdCreateStatic(front_thread, sizeof(front_thread), NORMALPRIO, Threadi2c, NULL);

  /*
   * Events servicing loop.
   */
  while(1) {
    // never exit 
  }
  return 0;
}



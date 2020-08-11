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


/********** THREADS VARIABLES **********/
static WORKING_AREA(waThread_front_driver, 128);
static WORKING_AREA(waThread_front_passenger, 128);
static WORKING_AREA(waThread_rear_driver, 128);
static WORKING_AREA(waThread_rear_passenger, 128);

static WORKING_AREA(waThread_display, 128);


static msg_t Thread_Sensor(void *);
static msg_t Thread_Diplsay(void *);



int16_t min(int16_t, int16_t);

/********** VARIABLES **********/
SENSOR_SYSTEM system;
static int refresh_rate_ms = 200;
VL53L0X_Error system_failure_status = VL53L0X_ERROR_NONE;

int main(void) {
  halInit();
  chSysInit();

  /*
   * Serial port initialization.
   */
  sdStart(&SD1, NULL); 
  chprintf((BaseSequentialStream *)&SD1, "Main (SD1 started)\r\n");

  /*
   * Shell initialization.
   */
  shellInit();
  shellCreate(&shell_config, SHELL_WA_SIZE, NORMALPRIO + 1);
  

  /*
    Setup Sensor Structs
  */
  MUX front_mux;
  front_mux._pin_a.PAD = GPIO16_PAD;
  front_mux._pin_a.PORT = * GPIO16_PORT;
  front_mux._pin_a.PAD = GPIO17_PAD;
  front_mux._pin_a.PORT = * GPIO17_PORT;

  MUX rear_mux;
  front_mux._pin_a.PAD = GPIO14_PAD;
  front_mux._pin_a.PORT = * GPIO14_PORT;
  front_mux._pin_a.PAD = GPIO15_PAD;
  front_mux._pin_a.PORT = * GPIO15_PORT;


  system.front_driver.mux = front_mux; // Assign Mux Struct
  system.front_passenger.mux = front_mux; // Assign Mux Struct
  system.front_driver.refresh_rate = 1; // Set Default Refresh Rate Factor to 1
  system.front_passenger.refresh_rate = 1; 

  system.rear_driver.mux = front_mux; 
  system.rear_passenger.mux = front_mux; 
  system.rear_driver.refresh_rate = 1; 
  system.rear_passenger.refresh_rate = 1; 

  setup_sensors(system);

  /*
    Setup Threads
  */
  void * front_driver_sensor_args = &system.front_driver;
  void * front_passenger_sensor_args = &system.front_passenger;

  void * rear_driver_sensor_args = &system.rear_driver;
  void * rear_passenger_sensor_args = &system.rear_passenger;

  void * display_sensor_args = &system;

  chThdCreateStatic(waThread_front_driver, sizeof(waThread_front_driver), NORMALPRIO, Thread_Sensor, front_driver_sensor_args);
  chThdCreateStatic(waThread_front_passenger, sizeof(waThread_front_passenger), NORMALPRIO, Thread_Sensor, front_passenger_sensor_args);

  chThdCreateStatic(waThread_rear_driver, sizeof(waThread_rear_driver), NORMALPRIO, Thread_Sensor, rear_driver_sensor_args);
  chThdCreateStatic(waThread_rear_passenger, sizeof(waThread_rear_passenger), NORMALPRIO, Thread_Sensor, rear_driver_sensor_args);

  chThdCreateStatic(waThread_display, sizeof(waThread_display), NORMALPRIO, Thread_Diplsay, display_sensor_args);



  chThdWait(chThdSelf());

  return 0;
}


static msg_t Thread_Sensor(void *p) {
  (void)p;
  SENSOR_QUADRANT sensor_quad = *(SENSOR_QUADRANT *)p;
  chRegSetThreadName("sensor_read_in");
  while(1){
    // Read Distances
    system_failure_status = poll_device_values(sensor_quad);
    // Update Refresh Rate
    sensor_quad.refresh_rate = update_refresh_rate(min(sensor_quad.side.distance_rating.RangeMilliMeter, sensor_quad.center.distance_rating.RangeMilliMeter));
    int sleep_ms = (int)(refresh_rate_ms * sensor_quad.refresh_rate);
    chThdSleepMilliseconds(sleep_ms);
  }
  return 0;
}

static msg_t Thread_Diplsay(void *p) {
  SENSOR_SYSTEM sensory_system = *(SENSOR_SYSTEM *)p;
  chRegSetThreadName("display_update");
  while(1){
    /*
    ***********************
      DISPLAY UPDATE CODE 
    ***********************
    */
    chThdSleepMilliseconds(refresh_rate_ms * 2);
  }
  return 0;
}


int16_t min(int16_t a, int16_t b){
  if(a > b)
    return b;
  return a;
}

#include "ch.h"
#include "hal.h"
#include "test.h"
#include "shell.h"
#include "chprintf.h"

static msg_t ThreadFront(void *p) {
  (void)p;
  chRegSetThreadName("Front_Reading");
  while (TRUE) {
    palClearPad(ONBOARD_LED_PORT, ONBOARD_LED_PAD);
    chThdSleepMilliseconds(2000);
    palSetPad(ONBOARD_LED_PORT, ONBOARD_LED_PAD);
    chThdSleepMilliseconds(20000);
  }
  return 0;
}

static msg_t ThreadBack(void *p) {
  (void)p;
  chRegSetThreadName("Back_Reading");
  while (TRUE) {
    palClearPad(ONBOARD_LED_PORT, ONBOARD_LED_PAD);
    chThdSleepMilliseconds(2000);
    palSetPad(ONBOARD_LED_PORT, ONBOARD_LED_PAD);
    chThdSleepMilliseconds(20000);
  }
  return 0;
}


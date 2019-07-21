from pyHS100 import SmartBulb, SmartDeviceException
from threading import Thread, Event
import time
import logging


WARM_LIGHT = 2700
COLD_LIGHT = 6500

DAY_STATE = {
    "brightness": 100,
    "color_temp": COLD_LIGHT
}

NIGHT_STATE = {
    "brightness": 0,
    "color_temp": WARM_LIGHT
}

# {"name": "kids-sun-light"}

TRANSITION_RATIO = (50, 30, 20) # sum = 100!

# Default sunrise/sunset time
SUN_TRANSITION_PERIOD = 1 * 60 * 1000

_LOGGER = logging.getLogger(__name__)

_TRANSITION_THREAD = None


class SunriseThread(Thread):

    def __init__(self, bulb, period):
        Thread.__init__(self, name='Transition')
        self.__stop = Event()
        self.__bulb = bulb
        self.__period = period

    def stop(self):
        if not self.__stop.is_set():
            self.__stop.set()

    def run(self):
        light_state = {}

        # Phase 1
        if not self.__stop.is_set():
            phase1_period = int(self.__period * TRANSITION_RATIO[0] / 100)
            light_state.update({
                "brightness": TRANSITION_RATIO[0],
                "color_temp": WARM_LIGHT,
                "transition_period": phase1_period
            })

            self.__bulb.set_light_state(light_state)
            time.sleep(int(phase1_period / 1000) + 2)

        # Phase 2
        if not self.__stop.is_set():
            phase2_period = int(self.__period * TRANSITION_RATIO[1] / 100)
            light_state.update({
                "brightness": TRANSITION_RATIO[0] + TRANSITION_RATIO[1],
                "color_temp": COLD_LIGHT,
                "transition_period": phase2_period
            })

            self.__bulb.set_light_state(light_state)
            time.sleep(int(phase2_period / 1000) + 2)

        # Phase 3
        if not self.__stop.is_set():
            phase3_period = int(self.__period * TRANSITION_RATIO[2] / 100)
            light_state.update({
                "brightness": 100,
                "color_temp": COLD_LIGHT,
                "transition_period": phase3_period
            })

            self.__bulb.set_light_state(light_state)
            time.sleep(int(phase3_period / 1000) + 2)


class SunsetThread(Thread):

    def __init__(self, bulb, period):
        Thread.__init__(self, name='Transition')
        self.__stop = Event()
        self.__bulb = bulb
        self.__period = period

    def stop(self):
        if not self.__stop.is_set():
            self.__stop.set()

    def run(self):
        light_state = {}

        # Phase 1
        if not self.__stop.is_set():
            phase1_period = int(self.__period * TRANSITION_RATIO[0] / 100)
            light_state.update({
                "brightness": 100,
                "color_temp": WARM_LIGHT,
                "transition_period": phase1_period
            })

            self.__bulb.set_light_state(light_state)
            time.sleep(int(phase1_period / 1000) + 2)

        # Phase 2
        if not self.__stop.is_set():
            phase2_period = int(self.__period * TRANSITION_RATIO[1] / 100)
            light_state.update({
                "brightness": TRANSITION_RATIO[1],
                "color_temp": WARM_LIGHT,
                "transition_period": phase2_period
            })

            self.__bulb.set_light_state(light_state)
            time.sleep(int(phase2_period / 1000) + 2)

        # Phase 3
        if not self.__stop.is_set():
            phase3_period = int(self.__period * TRANSITION_RATIO[2] / 100)
            light_state.update({
                "brightness": 0,
                "color_temp": WARM_LIGHT,
                "transition_period": phase3_period
            })

            self.__bulb.set_light_state(light_state)
            time.sleep(int(phase3_period / 1000) + 2)

        if not self.__stop.is_set():
            self.__bulb.turn_off()


class TPBulb(SmartBulb):

    def __init__(self, host):
        if sum(TRANSITION_RATIO) > 100:
            raise ValueError("Transition period exceeds 100%")

        super().__init__(host=host)

    def turn_on(self):
        global _TRANSITION_THREAD
        if _TRANSITION_THREAD is not None:
            _TRANSITION_THREAD.stop()
            _TRANSITION_THREAD = None

        super().turn_on()

    def turn_off(self):
        global _TRANSITION_THREAD
        if _TRANSITION_THREAD is not None:
            _TRANSITION_THREAD.stop()
            _TRANSITION_THREAD = None

        self.set_light_state({
            "brightness": 0,
            "color_temp": WARM_LIGHT,
        })
        time.sleep(1)
        super().turn_off()

    def transition(self, color_temp=-1, brightness=-1, period=-1):
        global _TRANSITION_THREAD
        if _TRANSITION_THREAD is not None:
            _TRANSITION_THREAD.stop()
            _TRANSITION_THREAD = None

        light_state = self.get_light_state()
        if color_temp > 0:
            light_state["color_temp"] = color_temp

        if brightness >= 0:
            light_state["brightness"] = brightness

        if period >= 0:
            light_state["transition_period"] = period

        self.set_light_state(light_state)

    def sunrise(self, transition_period=-1):
        global _TRANSITION_THREAD
        if _TRANSITION_THREAD is not None:
            _TRANSITION_THREAD.stop()
            _TRANSITION_THREAD = None

        self.turn_on()

        light_state = {}
        light_state.update(NIGHT_STATE)
        self.set_light_state(light_state)
        time.sleep(1)

        if transition_period < 0:
            transition_period = SUN_TRANSITION_PERIOD

        _TRANSITION_THREAD = SunriseThread(self, transition_period)
        _TRANSITION_THREAD.start()

    def sunset(self, transition_period=-1):
        global _TRANSITION_THREAD
        if _TRANSITION_THREAD is not None:
            _TRANSITION_THREAD.stop()
            _TRANSITION_THREAD = None

        self.turn_on()

        light_state = {}
        light_state.update(DAY_STATE)
        self.set_light_state(light_state)
        time.sleep(1)

        if transition_period < 0:
            transition_period = SUN_TRANSITION_PERIOD

         _TRANSITION_THREAD = SunsetThread(self, transition_period)
         _TRANSITION_THREAD.start()

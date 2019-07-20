from pyHS100 import SmartBulb, SmartDeviceException
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

# % time for three transitions
# 1. brightness high temp
# 2. high to low temp
# 3. brightness
# !  Ensure sum add to 100%
TRANSITION_RATIO = (50, 30, 20)

# Default sunrise/sunset time
SUN_TRANSITION_PERIOD = 30000

_LOGGER = logging.getLogger(__name__)


class TPBulb(SmartBulb):

    def __init__(self, host):
        if sum(TRANSITION_RATIO) > 100:
            raise ValueError("Transition period exceeds 100%")

        super().__init__(host=host)

    def turn_on(self):
        super().turn_on()

    def turn_off(self):
        self.set_light_state({
            "brightness": 0,
            "color_temp": WARM_LIGHT,
        })
        time.sleep(1)
        super().turn_off()

    def transition(self, color_temp=-1, brightness=-1, period=-1):
        light_state = self.get_light_state()
        if color_temp > 0:
            light_state["color_temp"] = color_temp

        if brightness >= 0:
            light_state["brightness"] = brightness

        if period >= 0:
            light_state["transition_period"] = period

        self.set_light_state(light_state)

    def sunrise(self, transition_period=-1):
        self.turn_on()

        # Turn off light in case it's on
        light_state = {}
        light_state.update(NIGHT_STATE)
        self.set_light_state(light_state)
        time.sleep(1)

        if transition_period < 0:
            transition_period = SUN_TRANSITION_PERIOD

        # Phase 1
        phase1_period = int(transition_period * TRANSITION_RATIO[0] / 100)
        light_state.update({
            "brightness": TRANSITION_RATIO[0],
            "color_temp": WARM_LIGHT,
            "transition_period": phase1_period
        })

        self.set_light_state(light_state)
        time.sleep(int(phase1_period/1000) + 2)

        # Phase 2
        phase2_period = int(transition_period * TRANSITION_RATIO[1] / 100)
        light_state.update({
            "brightness": TRANSITION_RATIO[0] + TRANSITION_RATIO[1],
            "color_temp": COLD_LIGHT,
            "transition_period": phase2_period
        })

        self.set_light_state(light_state)
        time.sleep(int(phase2_period/1000) + 2)

        # Phase 3
        phase3_period = int(transition_period * TRANSITION_RATIO[2] / 100)
        light_state.update({
            "brightness": 100,
            "color_temp": COLD_LIGHT,
            "transition_period": phase3_period
        })

        self.set_light_state(light_state)
        time.sleep(int(phase3_period/1000) + 2)

    def sunset(self, transition_period=-1):

        pass


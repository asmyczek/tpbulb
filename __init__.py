from homeassistant.exceptions import NoEntitySpecifiedError
from .tpbulb import TPBulb
import logging

DOMAIN = 'tpbulb'
TPBULBS = 'tpbulbs'

ATTR_NAME = 'name'
ATTR_TRANSITION = 'transition'
ATTR_COLOR_TEMP = 'color_temp'
ATTR_BRIGHTNESS = 'brightness'

_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    conf = config.get(DOMAIN)

    hass.data[DOMAIN] = {}

    for entry in conf:
        name = entry['name']
        host = entry['host']

        _LOGGER.debug(
            "Initializing: %s %s", host, name
        )

        hass.data[DOMAIN][name] = TPBulb(host)

    class BulbConnection(object):

        def __init__(self, name):
            self.__bulb = hass.data[DOMAIN].get(name, None)

            if self.__bulb is None:
                raise NoEntitySpecifiedError(
                    'No bulb found for name {}'.format(name))

        def __enter__(self):
            return self.__bulb

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def turn_on(call):
        with BulbConnection(call.data.get(ATTR_NAME, None)) as bulb:
            bulb.turn_on()
    hass.services.register(DOMAIN, 'turn_on', turn_on)

    def turn_off(call):
        with BulbConnection(call.data.get(ATTR_NAME, None)) as bulb:
            bulb.turn_off()
    hass.services.register(DOMAIN, 'turn_off', turn_off)

    def transition(call):
        with BulbConnection(call.data.get(ATTR_NAME, None)) as bulb:
            bulb.transition(
                call.data.get(ATTR_COLOR_TEMP, -1),
                call.data.get(ATTR_BRIGHTNESS, -1),
                call.data.get(ATTR_TRANSITION, -1)
            )
    hass.services.register(DOMAIN, 'transition', transition)

    def sunrise(call):
        with BulbConnection(call.data.get(ATTR_NAME, None)) as bulb:
            bulb.sunrise(
                call.data.get(ATTR_TRANSITION, -1)
            )
    hass.services.register(DOMAIN, 'sunrise', sunrise)

    def sunset(call):
        with BulbConnection(call.data.get(ATTR_NAME, None)) as bulb:
            bulb.sunset(
                call.data.get(ATTR_TRANSITION, -1)
            )
    hass.services.register(DOMAIN, 'sunset', sunset)

    return True

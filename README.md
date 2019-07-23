TPBulb
======

Quick workaround that adds transitions support to my _TPLink LB120_ bulbs in _HomeAssistant_.
It does not create a separate entity, just adds a _tpbulb_ service that can be used in automations.
By not creating separate entities, you can use native _HomeAssistant_ _tplink_ component alongside
these services.

I still hope for native transitions support in _pyHS100_ and _tplink_ component.

Use at your own risk.


Installation
------------

Clone the repo to your _homeassistant/config/custom_components/_ directory and initialise it with
```
tpbulb:
  - name: <name you will reference the bulb in automations>
    host: <ip>
  - name: <bulb name>
    host: <ip>
```
in _configuration.yaml_.


Services
--------
* turn_on(
  * name - _bulb name as defined in configuration.yaml_
  
  )
* turn_off(
  * name - _bulb name as defined in configuration.yaml_

  )
  
* transition( 
  * name - _bulb name as defined in configuration.yaml_
  * color_temp - _to transition color_temp_
  * brightness - _to transition brightness_
  * transition_period - _in milliseconds_

  )
  
  Manual transition service, parameters are optional if you want to change _color_temp_ or _brightness_ only. 
  
* sunrise(
  * name - _bulb name as defined in configuration.yaml_
  * transition_period - _in milliseconds, default 30 minutes_

  )
  
  Simulates sunrise in three stages over a default time period of 30 minutes.
  
* sundown(
  * name - _bulb name as defined in configuration.yaml_
  * transition_period - _in milliseconds, default 30 minutes_

  )
  
  Simulates sundown in two stages over a default time period of 30 minutes.
  
* day(
  * name - _bulb name as defined in configuration.yaml_

  )
  
  Turn on light to day mode
  
* night(
  * name - _bulb name as defined in configuration.yaml_

  )
  
  Set light to night mode and turn off
  
  

Examples
--------

Example automation

```
automation:

  - alias: Weekday wake-up
    trigger:
      platform: time
      at: "05:30:00"
    condition:
      condition: time
      weekday:
        - mon
        - tue
        - wed
        - thu
        - fri
    action:
      service: tpbulb.sunrise
      data:
        name: badroom-corner-light
```

License
-------

MIT License
# EXAMPLE: CHARGE THE CAR USING THE LOWEST RATES

## PROBLEM DESCRIPTION
When you arrive home with your electric car, and you don't need to leave for a while, you want to charge it at the lowest rates possible. This is not necessarily a consecitve block of hours, so here the `split` functionality can be used.

## SOLUTION
This time a binary sensor will be used, in combination with `mode=is_now`. This binary sensor will turn on every time the prices are lowest, taking into account the time remaining to charge. As that remaining time will update on a regular basis, this will then also trigger the template sensor to update the result. For `start` the current time (`now()`) can be used, which will then automatically update the binary sensor every minute. So in this case a trigger based binary sensor is not needed.

### REQUIRED
* An electric vehicle (EV) or plug-in hybrid vehicle (PHEV)
* A device_tracker indicating it's at home (if you connect it to a charger elsewhere, you probably actually want to charge it)
* A sensor indicating the remaining charge time (in this example that sensor indicates the remaining time in minutes)
* A binary_sensor indicating it's connected to the charger
* An input_datetime indicating the time the car needs to be fully charged again (the time you want to use it), this should be a date + time input_datetime

```yaml
# template sensor
template:
  - binary_sensor:
      - unique_id: 911f0a21-48de-438f-90a2-4b46401268b3
        name: Charge Car Cheap
        state: >
          {% set sensor = 'sensor.energy_prices' %}
          {% set hours = states('sensor.remaining_charge_time') | float / 60 %}
          {% from "cheapest_energy_hours.jinja" import cheapest_energy_hours %}
          {{ cheapest_energy_hours(sensor=sensor, hours=hours, start=now(), end=states('input_datetime.leave_home_again'), mode='is_now') }}
        availability: >
          {{
            is_state('device_tracker.car', 'home')
            and is_state('binary_sensor.charger_connected', 'on')
            and states('sensor.remaining_charge_time') | is_number
          }}

# automation (using the state of the binary_sensor to either start or stop charging)
automation:
  - id: adb3e92e-2bd8-4d0e-a35f-3ac2058372d1
    alias: Charge car
    trigger:
      - platform: state
        entity_id: binary_sensor.charge_car_cheap
        to:
          - "on"
          - "off"
    variables:
      charge_switch: switch.charge_car
    condition:
      - platform: template
        value_template: "{{ not is_state(charge_switch, trigger.to_state.state) }}"
    action:
      - service: swith.turn_{{ trigger.to_state.state }}
        target:
          entity_id: "{{ charge_switch }}"
```

### NAVIGATION
[CONTENTS](0-how-to.md) | [EXAMPLE: TURN A DEVICE ON AT THE LOWEST PRICE WHILE YOU ARE SLEEPING](./6a-dishwasher_overnight.md)
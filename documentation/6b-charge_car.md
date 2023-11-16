# EXAMPLE: CHARGE THE CAR WITH THE LOWEST PRICES

## PROBLEM DESCRIPTION
When you arrive home with your electric car, and you don't need to leave for a while, you want to charge it at the lowest rates possible. This is not nnecessarily a consecitve block of hours, so here the `split` functionality can be used.

## SOLUTION
This time we will use a binary sensor, and `mode=is_now`. This binary sensor will turn on every time the prices are lowest, taking into account the time remaining to charge. As that remaining time will update on a regular basis, this will then also trigger the template sensor to update the result. We can also simply use the current time (`now()`) as the start, and that will then also automatically update the binary sensor every minute. So we don't need a trigger based binary sensor.

### REQUIRED
* An electric or hybrid car
* A sensor indicating the remaining charge time (in this example that sensor indicates the remaining time in minutes)
* A device_tracker indicating it's at home (if you connect it to a charger elsewhere, you probably actually want to charge it)
* A binary_sensor indicating it's connected to the charger
* An input_datetime indicating the time it needs to be full, this should be a date + time input_datetime

```yaml
# template sensor
template:
  - binary_sensor:
      - unique_id: 911f0a21-48de-438f-90a2-4b46401268b3
        name: Charge Car Cheap
        device_class: timestamp
        state: >
          {% set sensor = 'sensor.energy_prices' %}
          {% set hours  = states('sensor.remaining_charge_time') | float / 60 %}
          {% from "cheapest_energy_hours.jinja" import cheapest_energy_hours %}
          {{ cheapest_energy_hours(sensor=sensor, hours=hours, start=now(), end=states('input_datetime.leave_home_again'), mode='is_now') }}
        availability: >
          {{
            is_state('device_tracker.car', 'home')
            and is_state('binary_sensor.charger_connected', 'on')
            and states('sensor.remaining_charge_time') | is_number
          }}

# automation
automation:
  - id: adb3e92e-2bd8-4d0e-a35f-3ac2058372d1
    alias: Charge car
    trigger:
      - platform: state
        entity_id: binary_sensor.charge_car_cheap
        to: "on"
    action:
      - service: swith.turn_on
        target:
          entity_id: switch.charge_car
```

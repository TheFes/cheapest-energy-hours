# EXAMPLE: TURN ON YOUR DISHWASHER OVERNIGHT

## PROBLEM DESCRIPTION
Every time before going to bed, the dishwasher is turned on. But it could be that later during the night, the prices are lower. Luckily it is a smart dishwasher which can be turned on remotely, and is integrated in Home Assistant. The program which is always used takes 2.5 hours, and the start time should be after 22:00 when the dishwasher is alreadye closed, or when the door is closed after 22:00. It should be finished at 8:00 in the morning.

## COMPLICATING FACTORS
The fact that the start time can be either before or after midnight makes this problem a bit tricky. If the cheapest block of 2.5 hours starts at 23:00, it should finish at 1:30. However, after midnight the data will be different, as there is no data of yesterday anymore. Furthermore, if you use `start='22:00', end='08:00', include_tomorrow=true` this will be the eveninng of day 2 after midnight, and the macro will return an error because there is no data of the next day available yet, and therefor there are only 2 hours of data in the selection. With some templates you could work around that issue, but then again a block of 3.5 hours will be selected which can be eg 4:00 - 6:30, which potentitally can make the dishwasher run the program twice.

## SOLUTION
If the data would not span the night `mode='is_now'` could be used, but that's not possible here because of the factors described above. In this case it's best to use a trigger based template sensor which will trigger before your stat time (with some fallbacks if HA down at that moment). You can then turn on the dishwasher when the current time matches that sensor.

```yaml
# template sensor
template:
  - trigger:
      -  platform: time
         at:
           - '19:30'
           - '20:30'
           - '21:30'
    sensor:
      - unique_id: f8853830-bf81-46d4-85a9-379c25c37c23
        name: Dishwasher Start Time
        device_class: timestamp
        state: >
          {%- set sensor = 'sensor.energy_prices' -%}
          {% from "cheapest_energy_hours.jinja" import cheapest_energy_hours %}
          {{ cheapest_energy_hours(sensor=sensor, hours=2.5, start='22:00', end='08:00, include_tomorrow=true) }}

# automation
automation:
  - id: 3f61bd8e-81b8-4d62-8d5d-96d8596e29b1
    alias: Start Dishwasher During Night
    trigger:
      - platform: time
        at: sensor.dishwasher_start_time
    condition:
      - platform: state
        entity_id: binary_sensor.dishwasher_door
        state: "off"
    action:
      - service: swith.turn_on
        target:
          entity_id: switch.start_dishwasher
```
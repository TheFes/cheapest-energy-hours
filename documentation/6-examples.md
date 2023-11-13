# EXAMPLES

TO BE REWRITTEN

Examples to be added
* Start smart dishwasher overnight
* Charge car using split

## Basic examples

You always need to import the macro, so the first line should always be:
```jinja
{% from "cheapest_energy_hours.jinja" import cheapest_energy_hours %}
```

To get the start datetime of an a 3 hour time block when the energy price is lowest, only taking account the data of today
```jinja
{{ cheapest_energy_hours("sensor.nordpool_kwh_nl_eur", hours=3) }}
```

To find a 2 hour time block where the sensor uses the key `banana` for the show the dateime, and `apple` to show the energy price
```jinja
{{ cheapest_energy_hours("sensor.fruity_energy_prices", time_key="banana", value_key="apple", hours=2) }}
```

To only show the time in 24 hour format, and not the entire datetime string
```jinja
{{ cheapest_energy_hours("sensor.nordpool_kwh_nl_eur", hours=3, time_format="time24") }}
```

To also include seconds for the time, and do not take the hours in the past into account
```jinja
{{ cheapest_energy_hours("sensor.nordpool_kwh_nl_eur", hours=3, time_format="%H:%M:%S", look_ahead=true) }}
```

To include also the prices of tomorrow (if available)
```jinja
{{ cheapest_energy_hours("sensor.nordpool_kwh_nl_eur", hours=3, include_tomorrow=true) }}
```

To show the average price in the 3 hour period:
```jinja
{{ cheapest_energy_hours("sensor.nordpool_kwh_nl_eur", hours=3, mode="average") }}
```

To list the prices of the most expesive 5 hour time block
```jinja
{{ cheapest_energy_hours("sensor.nordpool_kwh_nl_eur", hours=5, lowest=false, mode="list") }}
```

## Advanced examples

For a device shows a higher power usage in the first hour, and last half hour. Based on the number of weight points the `hours` will be set to 3 automatically.
```jinja
{{ cheapest_energy_hours("sensor.nordpool_kwh_nl_eur", no_weight_points=2, weight=[2 , 4, 1, 1, 1, 5]) }}
```

### NAVIGATION
[PREVIOUS: ERROR HANDLING](5-error_handling.md)
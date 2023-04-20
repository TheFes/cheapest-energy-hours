[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/github/v/release/TheFes/cheapest-energy-hours)

# Cheapest Energy Hours

A jinja macro to easily find the cheapest consecutive block of hours to know when to turn on your dryer

## Why this macro

If your energy provider uses dynamic pricing, you might want to know when to turn on devices which consume a lot of power. It is relatively easy to find the lowest price on the day, but if it takes 3 hours for your dryer to complete, you might want to find the cheapest block of hours. It could be that the cheapest hour is not even in that block.
This macro comes to the rescue!

## How to install
Install it in HACS, or copy the contents of `cheapest_energy_hours.jinja` to a jinja file in your `custom_templates` folder.
Run the `homeassistant.reload_custom_templates` service call to load the file.

## How to use
The only required field is the `sensor` which provides you the data. I use the [Nordpool](https://github.com/custom-components/nordpool) integration for that, but you can use another. The sensor should provide the attributes `raw_today` and `raw_tomorrow` which then need to contain a list with hourly prices, and the datetime on which that hour starts. The nordpool integration also provides the end time, but that is not required for this macro.

Other optional fields are:

sensor, hours, start, end, time_key, value_key, include_today, include_tomorrow, lowest, mode)

|name|type|default|example|description|
|---|---|---|---|---|
|`hours`|integer|`1`|`3`|The number of consecutive hours|
|`start`|string|"00:00"|"19:00"|Start time to take into consideration for the value selection, use `now().strftime("%H:00")` if you don't want hours in the past|
|`end`|string|`none`|"23:00"|End time to take into consideration for the value selection, if `include_tomorrow` is set to `true` this will be the time tomorrow|
|`value_key`|string|`"start"`|`"datetime"`|The key used in the attributes of your integration for the start times of the hours|
|`value_key`|string|`"value"`|`"price"`|The key used in the attributes of your integration for the price values|
|`include_today`|boolean|`true`|`false`|Boolean to select if todays values should be included|
|`includ_tomorrow`|boolean|`false`|`true`|Boolean to select if tomorrows values should be included|
|`lowest`|boolean|`true`|`false`|Boolean to select if the marco should find the lowest price, set to `false` to find the highest price|
|`mode`|string|`"start"`|`"average"`|You can choose what to output, these values are accepted: `min` (lowest price in hours found), `max` (highest price in hours found), `average` (average price in hours found), `start` (start of the hours found), `end` (end of the hours found), `list` (list with the prices in hours found)|
|`top_hour`|integer|1|2|The most important hour in your hour range. Eg if hour device uses most energy in the 2nd hour, you can set this to `2` to give more weight to that energy price|
|`hour_weight`|float|2|2.5|The weight to add to the `top_hour` setting. If no `top_hour` is provided all hours have equal weight, when a `top_hour` is provided the default for this setting is `2`. Values below `1` will decrease the weight of the selected `top_hour`|

### Examples
You always need to import the macro, so the first line should always be:
```jinja
{% from 'cheapest_energy_hours.jinja' import cheapest_energy_hours %}
```

To get the start datetime of an a 3 hour time block when the energy price is lowest, only taking account the data of today
```jinja
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', hours=3) }}
```

To include also the prices of tomorrow (if available)
```jinja
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', hours=3, include_tomorrow=true) }}
```

To show the average price in the 3 hour period:
```jinja
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', hours=3, mode='average') }}
```

To list the prices of the most expesive 5 hour time block
```jinja
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', hours=5, lowest=false, mode='list') }}
```

To find the end datetime of a 4 hour time block where the 3rd hour has been given a weight of 5
```jinja
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', hours=4, lowest=false, mode='end', top_hour=3, hour_weight=5) }}
```

To find a 2 hour time block where the sensor uses the key `banana` for the show the dateime, and `apple` to show the energy price
```jinja
{{ cheapest_energy_hours('sensor.fruity_energy_prices', time_key='banana', value_key='apple', hours=2) }}
```

# Thanks to
* [@basbruss](https://github.com/basbruss) for providing the output mode 


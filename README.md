[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/github/v/release/TheFes/easy-energy-price)

# Easy Energy Price

A jinja macro to easily find the cheapest block of hours to know when to turn on your dryer

## Why this macro

If your energy provider uses dynamic pricing, you might want to know when to turn on devices which consume a lot of power. It is relatively easy to find the lowest price on the day, but if it takes 3 hours for your dryer to complete, you might want to find the cheapest block of hours. It could be that the cheapest hour is not even in that block.
This macro comes to the rescue!

## How to install
Install it in HACS, or copy the contents of `easy-energy-prices.jinja` to a jinja file in your `custom_templates` folder.
Run the `homeassistant.reload_custom_templates` service call to load the file.

## How to use
The only required field is the sensor which provides you the data. I use the [Nordpool](https://github.com/custom-components/nordpool) integration for that, but you can use another. The sensor should provide the attributes `raw_today` and `raw_tomorrow` which then need to contain a list with hourly prices, and the datetime on which that hour starts. The nordpool integration also provides the end time, but that is not required for this macro.

Other optional fields are:

sensor, hours, start, end, time_key, value_key, include_today, include_tomorrow, lowest, mode)

|name|type|default|example|description|
|---|---|---|---|---|
|`hours`|integer|`1`|`3`|The number of consecutive hours|
|`start`|string|"00:00"|"19:00"|Start time to take into consideration for the value selection, use `now().strftime("%H:00")` if you don't want hours in the past|
|`end`|string|`none`|"23:00"|End time to take into consideration for the value selection, if `include_tomorrow` is set to `true` this will be the time tomorrow|
|`value_key`|string|`"start"`|`"datetime"`|The key used in the attributes of your integration for the start times of the hours|
|`value_key`|string|`"value"`|`"price"`|The key used in the attributes of your integration for the price values|
|`include today`|boolean|`true`|`false`|Boolean to select if todays values should be included|
|`include tomorrow`|boolean|`false`|`true`|Boolean to select if tomorrows values should be included|
|`lowest`|boolean|`true`|`false`|Boolean to select if the marco should find the lowest price, set to `false` to find the highest price|
|`mode`|string|`"start"`|`"average"`|You can choose what to output, these values are accepted: 'min' (lowest price in hours found), 'max' (highest price in hours found), 'average' (average price in hours found), 'start' (start of the hours found), 'end' (end of the hours found), 'list' (list with the prices in hours found)|

Example usage:
Using a sensor state:
```jinja
{% from 'relative_time_plus.jinja' import relative_time_plus %}
{{ relative_time_plus(states('sensor.uptime'), parts=3, week=false, time=true, verbose=true, language='nl') }}
```
This will output something like
`10 dg, 2 u en 7 min`

Using a last_changed datetime of an entity:
```jinja
{% from 'relative_time_plus.jinja' import relative_time_plus %}
{{ relative_time_plus(states.light.office.last_changed, 2) }}
```

This will output something like
`3 hours and 1 minute`

Using a date string:
```jinja
{% from 'relative_time_plus.jinja' import relative_time_plus %}
{{ relative_time_plus('2023-01-01', parts=2, time=false, week=false) }}
```

This will output something like (assuming the current date is 9th of April 2023)
`3 months and 8 days`

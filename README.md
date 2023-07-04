[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/github/v/release/TheFes/cheapest-energy-hours)
[![Buy me a coffe](https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white)](https://www.buymeacoffee.com/TheFes)

# Cheapest Energy Hours

A jinja macro to easily find the cheapest consecutive block of hours to know when to turn on your dryer

## Why this macro

If your energy provider uses dynamic pricing, you might want to know when to turn on devices which consume a lot of power. It is relatively easy to find the lowest price on the day, but if it takes 3 hours for your dryer to complete, you might want to find the cheapest block of hours. It could be that the cheapest hour is not even in that block.
This macro comes to the rescue!

## How to install
You need to have Home Assistant 2023.4 or higher installed to use custom templates.

To install it using HACS, you need to have experimental mode enabled, this is required to install templates.
After that, press the button below to go directly to the right section:

[![HACS repository.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TheFes&repository=cheapest-energy-hours&category=template)

For a manual install you can copy the contents of `cheapest_energy_hours.jinja` to a jinja file in your `custom_templates` folder.
Run the `homeassistant.reload_custom_templates` service call to load the file.



## How to use
The only required field is the `sensor` which provides you the data. I use the [Nordpool](https://github.com/custom-components/nordpool) integration for that, but you can use another. The sensor should provide the attributes `raw_today` and `raw_tomorrow` which then need to contain a list with hourly prices, and the datetime on which that hour starts. The nordpool integration also provides the end time, but that is not required for this macro.

Other optional fields are listed below:

### Source sensor settings
|name|type|default|example|description|
|---|---|---|---|---|
|`attr_today`|string|`raw_today`|`prices_today`|The attribute which has the datetimes and prices for today used by the macro, defaults to `raw_today`|
|`attr_tomorrow`|string|`raw_tomorrow`|`prices_tomorrow`|The attribute which has the datetimes and prices for today used by the macro, defaults to `raw_tomorrow`|
|`time_key`|string|`"start"`|`"datetime"`|The key used in the attributes of your integration for the start times of the hours|
|`value_key`|string|`"value"`|`"price"`|The key used in the attributes of your integration for the price values|


### Basic data selection settings
|name|type|default|example|description|
|---|---|---|---|---|
|`hours`|integer|`1`|`3`|The number of consecutive hours|
|`start`|string|`"00:00"`|`"19:00"`|Start time to take into consideration for the value selection|
|`end`|string|`none`|`"23:00"`|End time to take into consideration for the value selection, if `include_tomorrow` is set to `true` this will be the time tomorrow|
|`include_today`|boolean|`true`|`false`|Boolean to select if todays values should be included|
|`include_tomorrow`|boolean|`false`|`true`|Boolean to select if tomorrows values should be included|

### Data output settings
|name|type|default|example|description|
|---|---|---|---|---|
|`lowest`|boolean|`true`|`false`|Boolean to select if the marco should find the lowest price, set to `false` to find the highest price|
|`mode`|string|`"start"`|`"average"`|You can choose what to output, these values are accepted: `min` (lowest price in hours found), `max` (highest price in hours found),`time_min` (time of lowest price in hours found),`time_max` (time of highest price in hours found), `average` (average price in hours found), `start` (start of the hours found), `end` (end of the hours found), `list` (list with the prices in hours found), `weighted_average` (the average price taking into account the weight for the `top_hour`)|
|`look_ahead`|boolean|`false`|`true`|When set to true, only the hours as of the current hour are taken into account. This overrides the `start` time if that time is earlier than the current hour.
|`time_format`|string|`none`|`"time24"`|You can use `time12` for the 12-hour format including `AM` or `PM`, `time24` for the 24-hour format, or any custom format using the variables from the python strftime method ([cheatsheet](https://strftime.org))

### Advanced data selection settings
It could be that your device doesn't have a stable consumption during the period it is on. A washing machine for example will use most power at the start of the program to heat up the water, and at the end, for the spinning to get the water out again.
To take this into account, you can provide a `weight` list which will be used to find the optimal period to turn your device on. You can even break down the hours into smaller parts, so the result could be that the device should be turned on at eg 11:45.
To break down into smaller time fractions, you can provide a number in the `no_weight_points` setting. So to break it down into parts of 15 minutes, you need to provide `4` for this setting (4 weight points per hour).

The number or hours will be calculated based on `weight` and `no_weight_points`. So eg if there are 4 weight points per hour, and the `weight` list has 8 items, `hours` will be set to `2` (8/4). This value will be rounded up, and zeros will be added to the `weight` list to make sure the number of items in the list matches the expected number. 

In case `hours` is provided, this will overrule the calculated number of hours, if there are more items in the `weight` list based on the provided number of hours, these will be removed from the list, and not taken into account.

|name|type|default|example|description|
|---|---|---|---|---|
|`no_weight_points`|integer|`1`|`4`|The most important hour in your hour range. Eg if hour device uses most energy in the 2nd hour, you can set this to `2` to give more weight to that energy price|
|`weight`|list|`none`|`[25, 1, 4, 0]`|The list with weight factors to be used for the calculation| 

To help getting the weight data from your device, I created a script and a template sensor which stores the data. The script requires a energy sensor for the device you want to track, and some entity to determine when to stop plotting the data (this can be an input_boolean, or the state of the device iteself)
You can start the script manually, or automate it. The data will be stored in a template sensor called `sensor.energy_plots`.
It will survive reboots, so you can refer to the data directly in the template for the macro, but if you store a lot of data it will be ommited from saving in your database automatically. So it might be better to store the list in another entity (an input_text for example) or just copy it in use it directly in the macro.

More information on how to use the script and template sensor can be found [here](./example_package/README.md)

### Basic examples

You always need to import the macro, so the first line should always be:
```jinja
{% from 'cheapest_energy_hours.jinja' import cheapest_energy_hours %}
```

To get the start datetime of an a 3 hour time block when the energy price is lowest, only taking account the data of today
```jinja
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', hours=3) }}
```

To find a 2 hour time block where the sensor uses the key `banana` for the show the dateime, and `apple` to show the energy price
```jinja
{{ cheapest_energy_hours('sensor.fruity_energy_prices', time_key='banana', value_key='apple', hours=2) }}
```

To only show the time in 24 hour format, and not the entire datetime string
```jinja
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', hours=3, time_format='time24') }}
```

To also include seconds for the time, and do not take the hours in the past into account
```jinja
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', hours=3, time_format='%H:%M:%S', look_ahead=true) }}
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

### Advanced examples

For a device shows a higher power usage in the first hour, and last half hour. Based on the number of weight points the `hours` will be set to 3 automatically.
```jinja
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', no_weight_points=2, weight=[2 , 4, 1, 1, 1, 5] }}
```

# Thanks to
* [@basbruss](https://github.com/basbruss) for providing the output mode 


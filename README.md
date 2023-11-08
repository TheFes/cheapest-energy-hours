[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/github/v/release/TheFes/cheapest-energy-hours)
[![Buy me a coffe](https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white)](https://www.buymeacoffee.com/TheFes)


A jinja macro to easily find the cheapest consecutive block of hours to know when to turn on your dryer

- [Why this macro](#why-this-macro)
- [How to install](#how-to-install)
- [How to use](#how-to-use)
  - [Source sensor settings](#source-sensor-settings)
  - [Basic data selection settings](#basic-data-selection-settings)
  - [Data output settings](#data-output-settings)
    - [Output modes](#output-modes)
  - [Advanced data selection settings](#advanced-data-selection-settings)
  - [Basic examples](#basic-examples)
  - [Advanced examples](#advanced-examples)
- [Error handling](#error-handling)
- [Thanks to](#thanks-to)


# Why this macro

If your energy provider uses dynamic pricing, you might want to know when to turn on devices which consume a lot of power. It is relatively easy to find the lowest price on the day, but if it takes 3 hours for your dryer to complete, you might want to find the cheapest block of hours. It could be that the cheapest hour is not even in that block.
This macro comes to the rescue!

# How to install
You need to have Home Assistant 2023.4 or higher installed to use custom templates.

This custom template is compatible with [HACS](https://hacs.xyz/), which means that you can easily download and manage updates for it. Custom templates are currently only available in HACS when you enable experimental features. Make sure to enable it in the HACS settings, which you can access from Settings > [Devices & Services](https://my.home-assistant.io/create-link/?redirect=integrations) > HACS When experimental features are enabled you click the button below to add it to your HACS installation,
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TheFes&repository=cheapest-energy-hours&category=template)


For a manual install you can copy the contents of `cheapest_energy_hours.jinja` to a jinja file in your `custom_templates` folder.
Run the `homeassistant.reload_custom_templates` service call to load the file.



# How to use
The only required field is the `sensor` which provides you the data. I use the [Nordpool](https://github.com/custom-components/nordpool) integration for that, but you can use another. The sensor should provide attributes with the prices for today and tomorrow, either in seperate attributes or in a combined one and which then need to contain a list with hourly prices, and the datetime on which that hour starts. The nordpool integration also provides the end time, but that is not required for this macro.

The macro will try to find the right attributes with the data for today and tomorrow and the correct keys for the start datetime and price, if this doesn't work, you can provide it.

Optional parameters are listed below:

## Source sensor settings
|name|type|default|example|description|
|---|---|---|---|---|
|`attr_today`|string|`"raw_today"`|`"prices_today"`|The attribute which has the datetimes and prices for today used by the macro, defaults to `raw_today`|
|`attr_tomorrow`|string|`"raw_tomorrow"`|`"prices_tomorrow"`|The attribute which has the datetimes and prices for today used by the macro, defaults to `raw_tomorrow`|
|`attr_all`|string|`prices`|`prices_all`|The attribute which contains both the data of today and tomorrow if provided by the sensor, defaults to `prices`|
|`time_key`|string|`"start"`|`"datetime"`|The key used in the attributes of your integration for the start times of the hours|
|`value_key`|string|`"value"`|`"price"`|The key used in the attributes of your integration for the price values|


## Basic data selection settings
|name|type|default|example|description|
|---|---|---|---|---|
|`hours`|integer|`1`|`3`|The number of consecutive hours|
|`start`|string|`"00:00"`|`"19:00"`|Start time to take into consideration for the value selection|
|`end`|string|`none`|`"23:00"`|End time to take into consideration for the value selection, if `include_tomorrow` is set to `true` this will be the time tomorrow|
|`include_today`|boolean|`true`|`false`|Boolean to select if todays values should be included|
|`include_tomorrow`|boolean|`false`|`true`|Boolean to select if tomorrows values should be included|

## Data output settings
|name|type|default|example|description|
|---|---|---|---|---|
|`lowest`|boolean|`true`|`false`|Boolean to select if the marco should find the lowest price, set to `false` to find the highest price|
|`mode`|string|`"start"`|`"average"`|see [seperate section](#output-modes)|
|`precision`|integer|`5`|`2`|The number of decimals used for the price output|
|`look_ahead`|boolean|`false`|`true`|When set to true, only the hours as of the current hour are taken into account. This overrides the `start` time if that time is earlier than the current hour.
|`time_format`|string|`none`|`"time24"`|You can use `time12` for the 12-hour format including `AM` or `PM`, `time24` for the 24-hour format, or any custom format using the variables from the python strftime method ([cheatsheet](https://strftime.org))
|`price_factor`|flaot|`1`|`0.01`|All prices will be multiplied with this value, so if your pr`ices are in cents and you want divided by 100, you can use `0.01`. Or if you want to add 20% VAT, you can use `1.2`
|`value_on_error`|any|error description|`as_datetime('2099-12-31)`|You can optionally provide a value to be outputted in case there is an error. This can be useful if you eg want it to use as state in a template sensor which has `device_class: timestamp` which will run in error if the state value is not as expected. Or if you output the data on your dashboard in a markup card and want to provide your own message.

### Output modes

#### start (default)
The isoformat datetime string with the start of the selected time period

#### end
The isoformat datetime string with the start of the selected time period

#### min
The lowest price in the the selected time period

#### max
The highest price in the selected time period

#### time_min
The isoformat datetime string of the time section with the lowest price within the selected time period

#### time_max
The isoformat datetime string of the time section with the highest price within the selected time period

#### list
A json string with the prices in the selected time period (use `from_json` to convert it to a list)

#### weighted_average
The average price taking into account the weight assigned to the different time sections

#### cheap_now
Returns `"true"` if the current time is within the cheapest hours based on your selection, otherwise `"false"`

#### all
Outputs all the above modes in a json string dictionary. Convert to a actual dictionary using `from_json`. This can be useful if you need more than one output mode for the same selection.
Exmple output:
```yaml
{
  "start": "2023-10-24T01:00:00+02:00",
  "end": "2023-10-24T06:00:00+02:00",
  "min": 0.08946,
  "max": 0.09721,
  "time_min": "2023-10-24T03:00:00+02:00",
  "time_max": "2023-10-24T01:00:00+02:00",
  "average": 0.09319,
  "weighted_average": 0.09319,
  "list": [
    0.09721,
    0.09454,
    0.08946,
    0.09027,
    0.09445
  ]
}
```

#### split
This specific output mode will return a json string with the consecutive time blocks in which the prices are lowest for the selected hours (within the selected `start` and `end`). This can be convenient if you eg want to charge your car for, and you know this is going to take 6 hours, and you only want to charge it during the 6 cheapest hours.
It will also return the number of hours in each time block, and the prices in that block.
This mode will not work with weights and programs, it will only look a the hours within your selection. Use `from_json` to convert it to a proper list with dictionaries.

Example
```jinja
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur_3_10_021', hours=6, mode='split', look_ahead=true, include_tomorrow=true, end='14:00') | from_json }}
```
Example output:
```json
[
  {
    "start": "2023-09-19T15:00:00+02:00",
    "end": "2023-09-19T16:00:00+02:00",
    "hours": 1,
    "prices": [
      -0.004
    ],
    "cheap_now": false
  },
  {
    "start": "2023-09-20T02:00:00+02:00",
    "end": "2023-09-20T03:00:00+02:00",
    "hours": 3,
    "prices": [
      -0.002,
      -0.004,
      -0.003
    ],
    "cheap_now": true
  },
  {
    "start": "2023-09-20T12:00:00+02:00",
    "end": "2023-09-20T14:00:00+02:00",
    "hours": 2,
    "prices": [
      -0.004,
      -0.006
    ],
    "cheap_now": false
  }
]
```

## Advanced data selection settings
It could be that your device doesn't have a stable consumption during the period it is on. A washing machine for example will use most power at the start of the program to heat up the water, and at the end, for the spinning to get the water out again.
To take this into account, you can provide a `weight` list which will be used to find the optimal period to turn your device on. You can even break down the hours into smaller parts, so the result could be that the device should be turned on at eg 11:45.
To break down into smaller time fractions, you can provide a number in the `no_weight_points` setting. So to break it down into parts of 15 minutes, you need to provide `4` for this setting (4 weight points per hour).

The number or hours will be calculated based on `weight` and `no_weight_points`. So eg if there are 4 weight points per hour, and the `weight` list has 8 items, `hours` will be set to `2` (8/4). This value will be rounded up, and zeros will be added to the `weight` list to make sure the number of items in the list matches the expected number. 

In case `hours` is provided, this will overrule the calculated number of hours, if there are more items in the `weight` list based on the provided number of hours, these will be removed from the list, and not taken into account.

|name|type|default|example|description|
|---|---|---|---|---|
|`no_weight_points`|integer|`1`|`4`|The number of weight points per hour, eg set to `4` if each weight point represents 15 minutes. This should match with the datapoints per hour, meaning the number of minutes each list item in the sensor represents (normally 60, for dynamic prices per hour) shoudl be divisable by the number of minutes per weight point. So with hourly data you can use `4` or `12` but not `7`|
|`weight`|list|`none`|`[25, 1, 4, 0]`|The list with weight factors to be used for the calculation|
|`program`|string|none|`"Dryer Clothes"`|Description of data used in the energy plot sensor. Adds automatically the correct weight and number of weight points.|
|`plot_sensor`|string|`"sensor.energy_plots"`|`"sensor.plot_data"`| The entity_id of the sensor with the energy plots.|
|`plot_attr`|string|`"energy_plots"`|`"plot_data"`|The attribute in which the enery plots are stored.|

To help getting the weight data from your device, I created a script and a template sensor which stores the data. The script requires a energy sensor for the device you want to track, and some entity to determine when to stop plotting the data (this can be an input_boolean, or the state of the device iteself)
You can start the script manually, or automate it. The data will be stored in a template sensor called `sensor.energy_plots`.
It will survive reboots, so you can refer to the data directly in the template for the macro, but if you store a lot of data it will be ommited from saving in your database automatically. So it might be better to store the list in another entity (an input_text for example) or just copy it in use it directly in the macro.

More information on how to use the script and template sensor can be found [here](./example_package/README.md)

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

# Error handling

The macro will display error messages as output in case of incorrect input.
|Message|What do do|
|---|---|
|parameter 'sensor' was not provided|No sensor was provided to get the data from, note that unless you use `sensor=` to name the parameter, you need to start with the sensor as first parameter|
|No valid data in selected sensor|The provided sensor does not have valid data to work with, the sensor might be unavailable, or you need to provide a specific `attr_today` or `attr_tomorrow`|
|Time key not found in data|The time key can not be found in the source data, you might need to proviee a `time_key` parameter|
|Value key not found in data|The value key can not be found in the source data, you might need to provide a `value_key` parameter|
|Boolean input expected for {parameter}|The mentioned parameter expects a boolean input, but something else is provided. You can provice values like `0`, `false`, `"True"` but not `"banana"`|
|Invalid mode selected|An invalid value for the `mode` parameter was provided, check your input|
|Selected program is not available or has no data|The value provided for the `program` parameter can not be found in the sensor, or has no data|
|Data plot for selected program not complete|The data plot for the value in the `program` parameter is incomplete|
|Invalid combination of data points per hour and number of weight points|The number of weight points does not match with the datapoints per hour provided by the sensor. If you eg have quarterly prices, you can't have 6 datapoints per hour, as 15 is not divisable by 10|
|No(t enough) data within current selection|There is no, or not enough data to match your input. This can happen if you eg want a consecutive block of 4 hours, and you only use todays data for future hours, when it's already after 21:00|

# Thanks to
* [@basbruss](https://github.com/basbruss) for providing the output mode and a lot of other additions!


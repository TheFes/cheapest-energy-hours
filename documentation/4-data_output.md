# 4. DATA OUTPUT

## 🚨 IMPORTANT NOTE 🚨

* The macro is created in a way which allows to return native types. So a datetime value will be a datetime object. The same applies to numeric values and booleans. It can also retrun a dictionary when `mode='all` or `debug=true` is used. 

## PARAMETERS

### **mode** <span style="color:grey">_string (default: start)_</span>
See [separate section](#output-modes)
***
### **split** <span style="color:grey">_boolean (default: false)_</span>
Splits the `hours` input into sections with the cheapest prices. So it will not always be a consecutive block of hours, but it will select all the lowest time sections within your selection. `weight` will not be used when `split=true`
***
### **debug** <span style="color:grey">_boolean (default: false)_</span>
Outputs debug data besides the actual output of the macro
***
### **precision** <span style="color:grey">_integer (default: 5)_</span>
The number of decimals used for the price output
***
### **time_format** <span style="color:grey">_string (default: none)_</span>
You can use `time12` for the 12-hour format including `AM` or `PM`, `time24` for the 24-hour format, or any custom format using the variables from the python strftime method ([cheatsheet](https://strftime.org)). `time_format='isoformat'` can be used to make the macro not use datetime objects as output, but let it return isoformat datetime strings instead, this is set by default when `mode='all'` is used or `debug` is set to `true`. In other cases the default time format is to return full datetime objects. This can be forced in `mode='all'` by setting `time_format='datetime'`.
***
### **price_factor** <span style="color:grey">_float (default: 1)_</span>
All prices will be multiplied with this value. So if your prices are in cents and you want them to be divided by 100, you can use `0.01`. Or if you want to add 20% VAT, you can use `1.2`
***
### **lowest** <span style="color:grey">_boolean (default: true)_</span>
Determines if the marco should find the lowest price. Set this to `false` to find the highest price
***
### **latest_possible** <span style="color:grey">_boolean (default: false)_</span>
By default the macro will return the first time block with the cheapest (or highest when `lowest` is set to `false`). When `latest_possible` is set to `true` it will return the last time block with the cheapest prices.
***
### **price_tolerance** <span style="color:grey">_float or percentage (default: 0.0)_</span>
When set, prices which are within the price_tolerance compared to the lowest price (highest when `lowest` is set to `false`) are also considered as the lowest (or highest) price. Can be added as a fixed value (eg `0.2`) or as a percentage (eg `"5%"`). In case a percentage is used, it will be used on the lowest price in the time range (or highest price in case `lowest=false`)
***
### **use_hourly_avg** <span style="color:grey">_boolean (default: false)_</span>
Uses hourly prices instead of multiple prices per hour. The hourly prices are the average of the prices in that hour.
### **value_on_error** <span style="color:grey">_anything (default: none)_</span>
Will be used as output instead of error messages. So for eg in combination with `mode="is_now"`, this can be used to set the output to `false` when there is an error by setting `value_on_error=false`

## OUTPUT MODES

### split=false (default)
|mode|description|
|---|---|
|`start` (default)|The isoformat datetime string with the start of the selected time period|
|`end`|The isoformat datetime string with the end of the selected time period|
|`min`|The lowest price in the the consecutive time period|
|`max`|The highest price in the consecutive time period|
|`time_min`|The isoformat datetime string of the time section with the lowest price within the selected time period|
|`time_max`|The isoformat datetime string of the time section with the highest price within the selected time period|
|`list`|A list with the prices in the selected time period|
|`average`|The average price not taking into account the weight assigned to the different time sections|
|`weighted_average`|The average price taking into account the weight assigned to the different time sections|
|`is_now`|Returns `True` if the current time is within the consecutive based on your selection, otherwise `False`|
|`extreme_now`|Returns `"true"` if the current time matches the lowest (or highest in case `lowest=false`) price in the time range. Can be used in combination with `price_tolerance`|
|`estimated_costs`|Returns the estimated costs based on the `kwh` and optionally the `weight` input|
|`all`|Outputs all the above modes in a dictionary. This can be useful if you need more than one output mode for the same selection. Besides the data from all modes above, it will also output the number of hours used for the calculation (it can differ from the input because of the calculation to split the data), the number or datapoints per hour used for the calculations, and the total number of datapoints. [example](#example-output-modeall|
|`split`|This will output the same as when `split=true, mode="all"` is set.

#### EXAMPLE OUTPUT MODE="ALL"
```yaml
{
  "start": "2023-11-10T03:00:00+01:00",
  "end": "2023-11-10T04:30:00+01:00",
  "min": 0.059,
  "max": 0.06,
  "time_min": "2023-11-10T03:00:00+01:00",
  "time_max": "2023-11-10T04:00:00+01:00",
  "average": 0.05933,
  "weighted_average": 0.05933,
  "list": [
    0.059,
    0.059,
    0.06
  ],
  "is_now": false,
  "extreme_now": false,
  "estimated_costs": 0.243,
  "no_weight_points": 2,
  "datapoints_per_hour": 2,
  "hours": 1.5,
  "datapoints": 3
}
```

### split=true
|mode|description|
|---|---|
|`start` (default)|The isoformat datetime string with the start of the first time block|
|`end`|The isoformat datetime string with the end of the last time block|
|`min`|The lowest price in all the time blocks|
|`max`|The highest price in all the time blocks|
|`time_min`|The isoformat datetime string of the time block that has the lowest price in it|
|`time_max`|The isoformat datetime string of the time block that has the highest price in it|
|`list`|A json string with all the prices in all time blocks|
|`average`|The average of all the prices|
|`weighted_average`|The same as `mode="average"` as `weight` is not used in split|
|`is_now`|Returns `True` if the current time is within any of the time blocks otherwise it will return `False`|
|`all`|Outputs the data of all time blocks in a dictionary|
|`split`|This will output the same as when `split=true, mode="all"` is set

#### EXAMPLE OUTPUT SPLIT=TRUE, MODE="ALL"
```json
[
  {
    "start": "2023-09-19T15:00:00+02:00",
    "end": "2023-09-19T16:00:00+02:00",
    "hours": 1,
    "prices": [
      -0.004
    ],
    "is_now": false
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
    "is_now": true
  },
  {
    "start": "2023-09-20T12:00:00+02:00",
    "end": "2023-09-20T14:00:00+02:00",
    "hours": 2,
    "prices": [
      -0.004,
      -0.006
    ],
    "is_now": false
  },
  {
    "total_hours": 6,
    "datapoints_per_hour": 1,
    "datapoints": 6
  }
]
```

### NAVIGATION
[PREVIOUS: ADVANCED DATA](3-advanced_data.md) | [CONTENTS](0-how-to.md) | [NEXT: ERROR HANDLING](5-error_handling.md)

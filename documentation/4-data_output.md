# 4. DATA OUTPUT

## 🚨 IMPORTANT NOTE 🚨

* A macro **ALWAYS** returns a string. So you need to convert the output based on the selected [mode](#output-modes). So if your output is the price, you need to convert it to a number using the `float` function of filter to be able to calculate with it, if it is the start or end time, you can use `as_datetime`. For more complex structures used in the modes `split` and `all` use `from_json` (only available as filter) and for the mode `is_now` you can use `bool`. Make sure to use defaults, or use the `value_on_error` parameter to avoid errors while converting the data.

## PARAMETERS

### **mode** <span style="color:grey">_string (default: start)_</span>
See [seperate section](#output-modes)
***
### **split** <span style="color:grey">_boolean (default: false)_</span>
Splits the `hours` input into sections with the chepest prices. So it will not alwasy be a consecutive block of hours, but it will select all the lowest time sections within your selection. `weight` will not be used when `split=true`
***
### **debug** <span style="color:grey">_bolean (default: false)_</span>
Outputs debug data besides the actual output of the macro
***
### **precision** <span style="color:grey">_integer (default: 5)_</span>
The number of decimals used for the price outpu
***
### **time_format** <span style="color:grey">_string (default: none)_</span>
You can use `time12` for the 12-hour format including `AM` or `PM`, `time24` for the 24-hour format, or any custom format using the variables from the python strftime method ([cheatsheet](https://strftime.org))
***
### **price_factor** <span style="color:grey">_float (default: 1)_</span>
All prices will be multiplied with this value, so if your prices are in cents and you want divided by 100, you can use `0.01`. Or if you want to add 20% VAT, you can use `1.2`
***
### **lowest** <span style="color:grey">_bolean (default: true)_</span>
Determines if the marco should find the lowest price, set to `false` to find the highest price
***
### **latest_possible** <span style="color:grey">_boolean (default: false)_</span>
By default the macro will return the first time block with the cheapest (or highest when `lowest` is set to `false`). When `latest_possible` is set to `true` it will return the last time block with the cheapest prices.
***
### **price_tolerance** <span style="color:grey">_float (default: 0.0)_</span>
When set, prices which are within the price_tolerance compared to the lowest price (highest when `lowest` is set to `false`) are also considered as the lowest (or hightest) price.
***
### **value_on_error** <span style="color:grey">_anything (default: none)_</span>
Will be used as output instead of error messages, so for eg in combination with `mode="is_now"` this can be used to set the output to `false` when there is an error by setting `value_on_error=false`

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
|`list`|A json string with the prices in the selected time period (use `from_json` to convert it to a list)|
|`average`|The average price not taking into account the weight assigned to the different time sections|
|`weighted_average`|The average price taking into account the weight assigned to the different time sections|
|`is_now`|Returns `"true"` if the current time is within the consecutive based on your selection, otherwise `"false"`|
|`all`|Outputs all the above modes in a json string dictionary. Convert to a actual dictionary using `from_json`. This can be useful if you need more than one output mode for the same selection. Besides the data from all modes above, it will also output the number of hours used for the calculation (it can differ from the input because of the calculation to split the data), the number or datapoints per hour used for the calculations, and the total number of datapoints. [example](#example-output-modeall|
|`split`|This will output the same as when `split=true, mode="all"` is set

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
|`time_min`|The isoformat datetime string of the time block which has the lowest price in it|
|`time_max`|The isoformat datetime string of the time block which has the highest price in it|
|`list`|A json string with all the prices in the all time blocks|
|`average`|The average of all the prices|
|`weighted_average`|The same as `mode="average"` as `weight` is not used in split|
|`is_now`|Returns `"true"` if the current time is within any of the time blocks otherwise it will return `"false"`|
|`extreme_now`|Retruns `"true"` if the current time is matches the lowest (or highest) price in the time range. Can be used in combination with `price_tolerance`|
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
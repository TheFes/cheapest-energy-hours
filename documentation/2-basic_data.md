# 2. BASIC DATA

## 🚨 IMPORTANT NOTES 🚨

* `start` and `end`
  * When using a `start` and `end` which spans midnight, the output will change after midnight, as the source data will change as well (the data for the previous day will no longer be available). To avoid issues with changing data, it might be best to use a [trigger based template sensor](https://www.home-assistant.io/integrations/template/#trigger-based-template-binary-sensors-buttons-images-numbers-selects-and-sensors) and trigger it e.g. an hour before your `start` setting.
  * When using a `start` and `end` which spans midnight, selected period is calculated based on current time "now()".	
    + Example Start="22:00", end="06:00"
       - now() between "06:00" and "23:59" : Start set to today at '22:00', end set to tomorrow at '06:00'
         Note: At "14:00" Cheapest time search might change as before "14:00" prices for tomorrow are missing and cheapest time search stops at "23:59".
       - now() between "00:00" and "05:59" : Start set to today at '00:00', end set to today at '06:00'
         Note: At "00:00" cheapest time search might change as the price info between "22:00" to "23:59" is no longer available.
  * In case a time string like `"16:00"` is provided for the `end` time, this will be the time today if `inlcude_tomorrow` is not provided or set to `false`. When set to `true`, it will be the same time tomorrow. If no data for tomorrow is available, it will in practice be next midnight.
  * Using `look_ahead` doesn't automatically include the dates of tomorrow if it is currently after the time set for `end`. That will just make the data selection empty and an error message will be the output of the macro.
  * If `look_ahead` is set to `true`, the start date will always be in the future, unless `mode='is_now'` is set.
  * Setting `look_ahead` to `true` will move your data range, and the macro has no knowledge about the data in the past. So if the cheapest time is eg `13:00`, there will be a new cheapest time after that hour is passed. To avoid issues with changing data, it might be best to use a [trigger based template sensor](https://www.home-assistant.io/integrations/template/#trigger-based-template-binary-sensors-buttons-images-numbers-selects-and-sensors).
* conversion of input to match source data and/or provided `program`, `weight` or `no_weight_points` (see [3. ADVANCED DATA](./3-advanced_data.md))
  * `hours`, `start` and `end` will be converted to be divisible by 5, 10, 12, 15 or 30 minutes (whaterever is closest to the current setting), `hours` and `end` will be rounded up, `start` will be rounded down. If there is a conflict between 2 of these calculations (eg `hours` is divisible by 12 minutes, and `start` by 10 minutes), they will all be converted to be divisible by 5 minutes.

## PARAMETERS

### **hours** <span style="color:grey">_float (default: 1)_</span>
The number of consecutive hours to be used. It can be any number. If it is not a whole number, it will be converted so that the number of minutes are divisible by either 5, 10, 12, 15 or 30 minutes. Can be set to `'all'` to include all hours between the start and end time.
***
### **start** <span style="color:grey">_time string, datetime (string), number (default: 00:00)_</span>
The start time to take into consideration for the value selection. By default it will be last midnight.
Time strings should be in military time so eg `16:30`. If `include_today` is set to `false`, it will be the time tomorrow, otherwise it will be today. If set to a numeric value, it will be treated as a timestamp. So if you use something like `3600`, it will be 01:00 UTC on 1st of January 1970. Anything that can be converted to a datetime using `as_datetime` will work. In case a datetime string or number is used, the date from the resulting datetime value is leading. `include_today` and `include_tomorrow` will not be used for the start time then. The minutes of the start time will be recalculated to 5, 10, 12, 15 or 30 minutes.
***
### **end** <span style="color:grey">_string (default: 00:00)_</span>
The end time to take into consideration for the value selection. By default it is set to next midnight. If `include_tomorrow` is set, it will be midnight between tomorrow and the day after tomorrow.
Time strings should be in military time so eg `16:30`. If `include_tomorrow` is set to `true`, it will be the time tomorrow, otherwise it will be today. If set to a numeric value, it will be treated as a timestamp, so if you use something like `3600` it will be 01:00 UTC on 1st of January 1970. Anything that can be converted to a datetime using `as_datetime` will work. In case a datetime string or number is used, the date from the resulting datetime value is leading. `include_today` and `include_tomorrow` will not be used for the end time then. The minutes of the end time will be recalculated to 5, 10, 12, 15 or 30 minutes.
***
### **include_today** <span style="color:grey">_boolean (default: true)_</span>
Determines if the data of today should be used. Only used when no `start` parameter is provided, or if a time string is used for the `start` parameter.
***
### **include_tomorrow** <span style="color:grey">_boolean (default: false)_</span>
Determines if the data of tomorrow should be used. Only used when no `end` parameter is provided, or if a time string is used for the `end` parameter.
***
### **look_ahead** <span style="color:grey">_boolean (default: false)_</span>
To only include prices as of now, set this to `true`. If combined with `start`, the latest time of the two is used (so if the `start` parameter is set to a future time, that time will be leading, if it is set to a time in the past, the current time will be leading). If not combined with the parameter `start`, you can achieve the same by using `start=now()`

## EXAMPLE

```jinja
{% from 'cheapest_energy_hours.jinja' import cheapest_energy_hours %}
{% set output = cheapest_energy_hours(sensor='sensor.cheap_energy', hours=2.25, start='12:00', end=today_at('19:00') + timedelta(days=1), look_ahead=true) %}
```

### NAVIGATION
[PREVIOUS: SOURCE SENSOR](./1-source_sensor.md) | [CONTENTS](0-how-to.md) | [NEXT: ADVANCED DATA](./3-advanced_data.md)

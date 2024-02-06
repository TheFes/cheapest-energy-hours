# 5. ERROR HANDLING

The macro will display error messages as output in case of incorrect input.
|Message|What do do|
|---|---|
|parameter 'sensor' was not provided|No sensor was provided to get the data from, note that unless you use `sensor=` to name the parameter, you need to start with the sensor as first parameter|
|No valid data in selected sensor|The provided sensor does not have valid data to work with, the sensor might be unavailable, or you need to provide a specific `attr_today` or `attr_tomorrow`|
|Time key not found in data|The time key can not be found in the source data, you might need to proviee a `time_key` parameter|
|Value key not found in data|The value key can not be found in the source data, you might need to provide a `value_key` parameter|
|Boolean input expected for {parameter}|The mentioned parameter expects a boolean input, but something else is provided. You can provice values like `0`, `false`, `"True"` but not `"banana"`|
|Numeric input expected for {parameter}|The mentioned parameter expects a boolean input, but something else is provided. You can provice values like `0`, `"0.02"`, `"3"` but not `"orange"`|
|Invalid mode selected|An invalid value for the `mode` parameter was provided, check your input|
|Selected program is not available or has no data|The value provided for the `program` parameter can not be found in the sensor, or has no data|
|Data plot for selected program not complete|The data plot for the value in the `program` parameter is incomplete|
|Selected start parameter is after the end parameter|The start time is after the end time, check if `include_today` and `include_tomorrow` are set correct, and if `look_ahead` is working correctly in combination with your `end` parameter|
|{} hours between start and end, where {} hours are required|The start and end time are not providing enough hours for the `hours` parameter. Check if `include_today` and `include_tomorrow` are set correct, and if `look_ahead` is working correctly in combination with your `end` parameter|
|Invalid combination of data points per hour and number of weight points|The number of weight points does not match with the datapoints per hour provided by the sensor. If you eg have quarterly prices, you can't have 6 datapoints per hour, as 15 is not divisable by 10|
|No(t enough) data within current selection|There is no, or not enough data to match your input. This can happen if you eg want a consecutive block of 4 hours, and you only use todays data for future hours, when it's already after 21:00|


### NAVIGATION
[PREVIOUS: DATA OUTPUT](./4-data_output.md) | [CONTENTS](0-how-to.md) | [NEXT: EXPAMPLES](./6-examples.md)
# 3. ADVANCED DATA

It could be that your device doesn't have a stable consumption during the period it is on. A washing machine for example will use most power at the start of the program to heat up the water, and at the end, for the spinning to get the water out again.
To take this into account, you can provide a `weight` list which will be used to find the optimal period to turn your device on. You can even break down the hours into smaller parts, so the result could be that the device should be turned on at eg 11:45.
To break down into smaller time fractions, you can provide a number in the `no_weight_points` setting. So to break it down into parts of 15 minutes, you need to provide `4` for this setting (4 weight points per hour).

To help getting the weight data from your device, a script and a template sensor which stores the data are provided. The script requires a energy sensor for the device you want to track, and some entity to determine when to stop plotting the data (this can be an input_boolean, the state of a power sensor going below a threshold or the state of the device iteself)
You can start the script manually, or automate it. The data will be stored in a template sensor called `sensor.energy_plots`. It will survive reboots, so you can refer to the data directly in the template for the macro, but if you store a lot of data it will be ommited from saving in your database automatically. So it might be better to store the list in another entity (an input_text for example) or just copy it in use it directly in the macro.

More information on how to use the script and template sensor can be found [here](../example_package/README.md)

## 🚨 IMPORTANT NOTES 🚨

* When `no_weight_points` is set, the input for `hours`, `start` and `end` will be calculated according to this setting. So with `no_weight_points` set to `4` and a the `start` paramater is set to `12:59` the start time will be converted to `12:45`
* In case `no_weight_points` is set, and no `weight` is provided, a weight of `1` will be used.
* In case the `program` parameter is used, the `no_weight_points` and `weight` from the sensor are used, and the respective parameters will be ignored.
* If the `hours` parameter is not set the number or hours will be calculated based on `weight` and `no_weight_points`. So e.g. if there are 4 weight points per hour, and the `weight` list has 7 items, `hours` will be set to `1.75` (7/4).
* If the `hours` parameter is set, and it is less as expected based on the number of weight points, the `weight` value is truncated and only the first part is used. If `hours` is longer than expected based on the `weight` input a weight of `0` will be added for all missing items in the list.

## PARAMETERS

### **no_weight_points** <span style="color:grey">_integer (default: 1)_</span>
The number of weight points per hour, e.g. set to `4` if each weight point represents 15 minutes. This should match with the datapoints per hour, meaning the number of minutes each list item in the sensor represents (normally 60, for dynamic prices per hour) should be divisible by the number of minutes per weight point. So data per half hour can use `4` or `12` but not `3` (`30` is not divisible by `20`). This also applies the other way around if the minutes for the weight points are higher than the minutes for your source data, so `no_weight_points=3` (20 minutes) won't work with data per 15 minutes.
***
### **weight** <span style="color:grey">_list (default: none)_</span>
The list with weight factors to be used for the calculation.
***
### **kwh** <span style="color:grey">_float (default: none)_</span>
The kWh usage for the total number of hours, required to calculate the estimated costs.
***
### **plot_sensor** <span style="color:grey">_string (default: sensor.energy_plots)_</span>
The `entity_id` of the sensor with the energy plots.
***
### **plot_attr** <span style="color:grey">_string (default: plot_data)_</span>
The attribute in which the enery plots are stored.
***
### **program** <span style="color:grey">_string (default: none)_</span>
Description of data used in the energy plot sensor. Automatically adds the weight, number of weight points and kWh based on the energy plot.

## EXAMPLE

```jinja
{% from 'cheapest_energy_hours.jinja' import cheapest_energy_hours %}
{% set output = cheapest_energy_hours(sensor='sensor.cheap_energy', no_weight_points=2, weight=[2, 1, 1.5, 3, 3]) %}
```

### NAVIGATION
[PREVIOUS: BASIC DATA](./2-basic_data.md) | [CONTENTS](0-how-to.md) | [NEXT: DATA OUTPUT](4-data_output.md)

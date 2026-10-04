# 3. ADVANCED DATA

It could be that your device doesn't have a stable consumption during the period it is on. A washing machine for example will use most power at the start of the program to heat up the water, and at the end, for the spinning to get the water out again.
To take this into account, you can provide a `weight` list which will be used to find the optimal period to turn your device on. You can even break down the hours into smaller parts, so the result could be that the device should be turned on at eg 11:45.
To break down into smaller time fractions, you can provide a number in the `no_weight_points` setting. So to break it down into parts of 15 minutes, you need to provide `4` for this setting (4 weight points per hour), or `60` for one weight per minute (see [weights finer than the price data](#weights-finer-than-the-price-data)).

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
The number of weight points per hour, e.g. set to `4` if each weight point represents 15 minutes, or `60` if each weight point represents one minute. This should match with the datapoints per hour, meaning the number of minutes each list item in the sensor represents (normally 60, for dynamic prices per hour) should be divisible by the number of minutes per weight point. So data per half hour can use `4` or `12` but not `3` (`30` is not divisible by `20`). This also applies the other way around if the minutes for the weight points are higher than the minutes for your source data, so `no_weight_points=3` (20 minutes) won't work with data per 15 minutes.
***
### **weight** <span style="color:grey">_list (default: none)_</span>
The list with weight factors to be used for the calculation. The weights are relative: only their ratios matter for the result.

#### Weights finer than the price data

When `weight` has a finer resolution than the price data (eg one weight per minute with `no_weight_points: 60` on 15-minute or hourly prices), the price data is not upsampled: the macro keeps the price slots and compares all candidate starts at weight point resolution, so the result can be eg `02:07` even though the price only changes at quarters. The cost of a candidate is `sum(weight[m] x price of the slot containing weight point m) / sum(weight)`, the earliest start wins on a tie (the latest with `latest_possible=true`), and `start` and `end` are rounded up to a whole weight point. `list` contains one price per weight point. The `split` mode does not use the `weight` list and is unchanged.

Making each weight the energy (Wh) the device consumes in that minute (eg integrated from a smart plug) means `weight | sum / 1000` is the kWh of one run, which can be passed as `kwh` to get `estimated_costs`:

```yaml
template:
  - trigger:
      - trigger: time
        at: "21:30:00"
    sensor:
      - name: Dishwasher Start Time
        device_class: timestamp
        state: >
          {% from 'cheapest_energy_hours.jinja' import cheapest_energy_hours %}
          {% set wh = [0.15, 0.16, 0.24, 0.35, 21.13, 28.58, 28.85, 28.92, 11.52, 0.65] %}  {# one number per minute of the program #}
          {{ cheapest_energy_hours(
               sensor='sensor.electricity_prices',
               no_weight_points=60,
               weight=wh,
               kwh=wh | sum / 1000,
               start='22:00',
               end='08:00',
               include_tomorrow=true,
               mode='start') }}
```

***
### **kwh** <span style="color:grey">_float (default: none)_</span>
The kWh usage for the total number of hours, required to calculate the estimated costs. With per-minute energy totals (Wh) in `weight` this is `weight | sum / 1000`.
***
### **plot_sensor** <span style="color:grey">_string (default: sensor.energy_plots)_</span>
The `entity_id` of the sensor with the energy plots.
***
### **plot_attr** <span style="color:grey">_string (default: energy_plots)_</span>
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

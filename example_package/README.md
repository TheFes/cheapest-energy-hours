# Why this package?

The macro supports providing weight factors in case your device doesn't have a stable energy usage pattern. With this script and template sensor you can plot the weight factors needed for the macro.

# How to install this

You need both the script and the template sensor. The script sends events which are used to store the data in the sensor. You can put it in your configuration as a package, or place the script in your scripts.yaml, and the template sensor in your configuration.yaml.
The [script.yaml](./script.yaml) can be placed in `script.yaml` directly, and [sensor.yaml](./sensor.yaml) in your `configuration.yaml`. In case you already have definded `template:` in `configuration.yaml` make sure to place it under that key, and remove the `template:` line from my code.

# How to use it

Start the script in either an automation, or manually from developer tools > services
You need to provide some details as script variables:
|variable|mandatory|type|default|example|description|
|---|---|---|---|---|---|
|description|no|string|`"unknown"`|`"washing machine"`|Description which will be used as key to for which device the data is plotted|
|sensor|yes|string|`none`|`"sensor.wasmachine_energy"`|The energy sensor used to track the usage of the device|
|no_weight_points|no|integer|`4`|`2`|The number of weight points per hour|
|stop_entity|yes|string|`none`|`sensor.washing_machine`|An entity which is used to define when the script should stop sending data. This can be provided by the device, but can also be a input_boolean or binary_sensor which is eg toggled based on the power usage of the device|
|stop_state|yes|string|`none`|`"off"`|The state the `stop_entity` should be on to stop the script|

Example of the total script service call (using `script.turn_on` in this case)
```yaml
service: script.turn_on
target:
  entity_id: script.plot_energy_usage
data:
  variables:
    description: Washing Machine Cotton 1400rpm
    sensor: sensor.washing_machine_energy
    no_weight_points: 6
    stop_entity: binary_sensor.washing_machine_power_usage
    stop_state: "off"
```

# Important to know
* If Home Assistants restarts during the process or the script is stopped because of another reason, it won't be restarted. You'll have to start the process again.
* Plots with the same `description` will be overwritten
* There is a limited number of bytes which is allowed in an attribute. If you store too many plots, you could lose the data

# How to use the plot in the macro
Use the following in developer tools > template to get the data from the sensor. Copy paste that somewhere (or store it in an input_text) to use it later.
```jinja
{{ state_attr('sensor.energy_plots', 'energy_plots')['Your Description'].data }}
```
As long as the data is still in the sensor, you can directly refer to it. 
```jinja
{% set w = state_attr('sensor.energy_plots', 'energy_plots')['Your Description'].data %}
{% set wp = state_attr('sensor.energy_plots', 'energy_plots')['Your Description'].no_weight_points %}
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', no_weight_points=wp, weight=w }}
```

If you store the data in an input_text, or otherwise in a string instead of a list, you need to apply `| from_json` to convert it to a list again
```jinja
{% set w = states('input_text.energy_plot') | from_json %}
{{ cheapest_energy_hours('sensor.nordpool_kwh_nl_eur', no_weight_points=4, weight=w }}
```

# How to remove a plot from the sensor
In developer tools > events, you can send an event to remove a plot. The event type should be `update_energy_plot`
As event_data you need to send the description of the data you want to remove, and `status: remove`
```yaml
description: Washing Machine Cotton 1400rpm
status: remove
```


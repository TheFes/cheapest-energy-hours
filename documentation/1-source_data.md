# 1. SOURCE DATA

These parameters are used to determine where the source data can be found. If you use the custom [Nordpool integration](https://github.com/custom-components/nordpool) (can be downloaded using HACS), or an integration which uses the same attributes, you don't need to provide any of the parameters, but it is advised to provide the `sensor` as it will be more resource friendly if the macro doesn't need to search for it.

## 🚨 IMPORTANT NOTES 🚨
* It is advised to either provide the `source_settings` parameter, or provide all other parameters if they don't match the defaults. The default setting is to use the values as provided by the Nordpool custom integration, so if that is your source, there is no need to set anything. The macro will search for the attributes and keys in case they are not provided, but it is more resource friendly if they are already provided correctly.
* If your sensor uses other attributes for the data of today and tomorrow, you need to provide the correct `sensor` parameter or the correct `attr_today` and `attr_tomorrow` parameters. It can't find the right sensor if the atrributes differ from the defaults, and it can't find the right attributes if the right sensor is not provided, but as mentioned above, it's best to provide all the correct source parameters.
* In case `datetime_in_data` is set to `false` the attribute finder will not work, so you need to make sure to set `attr_today`, `attr_tomorrow` and/or `attr_all` yourself.

## PARAMETERS

### **sensor** <span style="color:grey">_string_</span>
The entity_id of the sensor containing the source data, in case this is not provided, the macro will search for a sensor matching attributes for the data for today and tomorrow. It is advised to provide a sensor though, as it will speed up the macro.
***
### **price_data** <span style="color:grey">_list_</span>
A list with the price data of the period you want to use. You can use this in case your energy price integration doesn't provide the price data in sensor attributes, but uses an action with an action response to provide the prices. This way there is no need to create a template sensor with the price data in attributes, but you can use the result from the action response directy. See the section [below](#using-the-action-response-as-input-for-the-macro) for an example.
### **source_settings** <span style="color:grey">_string (default: nordpool)_</span>
For certain (custom) integrations the settings for `attr_today`, `attr_tomorrow`, `attr_all`, `time_key`  and `value_key` can be provided in one go using this parameter. The correct value for each integration can be found in the table below. In case any of the parameters is also set, this will overrule the value from `source_settings`, meaning if you use `source_settings='entso-e, value_key='bananas'` the macro will use `bananas` instead of `price` which would be normally used based on the Entso-E source settings.
***
### **attr_today** <span style="color:grey">_string (default: raw_today)_</span>
The attribute that has the datetimes and prices for today used by the macro
***
### **attr_tomorrow** <span style="color:grey">_string (default: raw_tomorrow)_</span>
The attribute that has the datetimes and prices for tomorrow used by the macro
***
### **attr_all** <span style="color:grey">_string (default: prices)_</span>
The attribute that contains both the data of today and tomorrow if provided by the sensor
***
### **time_key** <span style="color:grey">_string (default: start)_</span>
The key used in the attributes of your integration for the start times of the hours
***
### **value_key** <span style="color:grey">_string (default: price)_</span>
The key used in the attributes of your integration for the price values
***
### **datetime_in_data** <span style="color:grey">_boolean (default: true)_</span>
In case the source data only provides the price values, without information about the date and time, set this to `false`
***
### **data_minutes** <span style="color:grey">_integer (default: 60)_</span>
The number of minutes each item in the source data represents. Only used in combination with `datetime_in_data=false`. Defaults to 1 hour (60 minutes)

## EXAMPLE

```jinja
{% from 'cheapest_energy_hours.jinja' import cheapest_energy_hours %}
{% set output = cheapest_energy_hours(sensor='sensor.cheap_energy', attr_today='forecast_today', attr_tomorrow='prices_tomorrow', time_key='datetime', value_key='value') %}
```

## DATA PROVIDER SETTINGS

This section provides the attributes and key settings for energy providers. The name links to the (custom) component used for the data.
If your provider is missing, you can create a Pull Request to add them, or create an [issue](<https://github.com/TheFes/cheapest-energy-hours/issues/new>), and give the details there so I can add them.

|Data Provider|core integraton|source_settings|parameters|comment|
|---|---|---|---|---|
|[Amber Electric](https://www.home-assistant.io/integrations/amberelectric/)|Yes|`amber_electric`|`attr_all='forecasts', time_key='start_time', value_key='per_kwh'`||
|[EasyEnergy](<https://www.home-assistant.io/integrations/easyenergy/>)|Yes|||Using the blueprint [below](#creating-a-forecast-sensor-using-the-action)|
|[EnergyZero](<https://www.home-assistant.io/integrations/energyzero/>)|Yes|||Using the blueprint [below](#creating-a-forecast-sensor-using-the-action)|
|[ENTSO-E](<https://github.com/JaccoR/hass-entso-e>)|No|`entso_e`|`attr_today='prices_today', attr_tomorrow='prices_tomorrow', time_key='time', value_key='price'`||
|[Frank Energie](<https://github.com/bajansen/home-assistant-frank_energie>)|No|`frank-energie`|`attr_all='prices', time_key='from', value_key='price'`||
|[GE-Spot](<https://github.com/enoch85/ge-spot>)|No|`ge-spot` or `ge-spot-hourly`|`attr_today='today_interval_prices', attr_tomorrow='tomorrow_interval_prices', time_key='time', value_key='value'`|Interval prices are per 15m, replace `*_interval_prices` with `*_hourly_prices` for prices per 60m|
|[Octopus Energy](<https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy>)|No|`octopus-energy`|`attr_all='rates', value_key='value_incl_vat'`||
|[Omie](<https://github.com/luuuis/hass_omie>)|No|||Using the template sensor [below](#omie)|
|[Nordpool (custom)](<https://github.com/custom-components/nordpool>)|No|||all set by default, but `source_settings='nordpool'` can be used as well|
|[Nordpool (core)](<https://www.home-assistant.io/integrations/nordpool/>)|Yes|||Using the blueprint [below](#creating-a-forecast-sensor-using-the-action)|
|[Spain electriciy hourly pricing (PVPC)](<https://www.home-assistant.io/integrations/pvpc_hourly_pricing/>)|Yes||Using the template sensor [below](#spain-electricity-hourly-pricing-pvpc)|
|[Tibber](https://www.home-assistant.io/integrations/tibber/)|Yes|||Using the blueprint [below](#creating-a-forecast-sensor-using-the-action)|
|[Tibber](<https://github.com/Danielhiversen/home_assistant_tibber_custom>)|No||`attr_today='today', attr_tomorrow='tomorrow', datetime_in_data=false`|This uses the custom component, not the core integration|
|[Zonneplan](<https://github.com/fsaris/home-assistant-zonneplan-one>)|No|`zonneplan`|`attr_all='forecast', value_key='electricity_price'`||

## USING THE ACTION RESPONSE AS INPUT FOR THE MACRO

Using the action response directly allows you to use integrations which do not provide the prices in an attribute without the need to create a template sensor (as described in the section below this one).
Here is an example using the EnergyZero integration, which will result in a sensor which has the datetime of the start of a block of 3.5 hours, starting now and ending tomorrow at midnight. It is updated every 5 minutes.

```yaml
template:
  - triggers:
      - alias: Triggers every 5 minutes
        trigger: time_pattern
        minutes: "/5"
    actions:
      - alias: Collects the price information and stores this in a response variable
        action: energyzero.get_energy_prices
        data:
          config_entry: fe7bdc80dd3bc850138998d869f1f19d # adjust to the config entry for your system
          incl_vat: false # set to false as it won't apply rounding to the prices
          start: "{{ now() }}"
          end: "{{ today_at('00:00') + timedelta(days=2) }}"      
    sensor:
      - unique_id: d8a349b4-2e83-417a-90dd-e38d0a9f3935
        name: Cheapest 3.5 hours from now
        state: >
          {% from 'cheapest_energy_hours.jinja' import cheapest_energy_hours %}
          {{ cheapest_energy_hours(price_data=prices['prices'], time_key='timestamp', value_key='price', hours=3.5, look_ahead=true, include_tomorrow=true) }}
        device_class: timestamp
```

## TEMPLATE SENSOR CONFIGURATION

### CREATING A FORECAST SENSOR USING THE ACTION

Some integrations (like the core [EnergyZero](<https://www.home-assistant.io/integrations/energyzero/>) and [EasyEnergy](<https://www.home-assistant.io/integrations/easyenergy/>) integrations) don't provide the forecast by default in an attribute. However they provide an action to retrieve the prices. 

I've createad a blueprint to create a template sensor which stores the prices in an attribute. The template sensor will store the prices for yesterday, today and tomorrow (when available). It will trigger every 15 minutes to ensure that the state is updated and reflects the current price.

It will only fetch prices using the action when needed, and only for the periods missing. If all prices are already stored in the sensor, it will only update the state.

The blueprints works with the core integrations for Easy Energy, Energy Zero, Nordpool and Tibber.

To use the blueprint, first import it using the button below:
[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FTheFes%2Fcheapest-energy-hours%2Ftree%2Fmain%2Fblueprints%2Fenergy_price_sensor.yaml)

Note that after importing the blueprint it will not be shown in Settings > Automations & Scenes > Blueprints. Only automation and script blueprints will be shown there. 
There is currently no GUI support for template blueprints, so you need to use it with YAML configuration. For the supported integrations you will find examples below.

For some integrations the `config_entry` is required, the easiest way to retrieve this is to go to [Developer tools > Action](<https://my.home-assistant.io/redirect/developer_services/>) and select an action for this integration. Then using GUI mode select the right integration. Then switch to YAML mode to see the config entry id.

Use the `entity_id` setting to provide the entity id for the template sensor which will be created. If you change this entity_id in the GUI, make sure to also change it in the YAML settings, because it is used in the templates.

#### ENERGYZERO AND EASYENERGY

Notes:
* When `incl_vat` is set to `true`, the EnergyZero result will use a 2 decimal precision, when set to `false` it will be 5 decimal precision. If you want more precise prices, set `incl_vat` to `false` (like in the example below, and optionally use `add_vat` to include the VAT percentage)

```yaml
- use_blueprint:
    path: TheFes/energy_price_sensor.yaml
    input:
      source: easyenergy # or use energyzero
      config_entry: 40b3351fd6f7baeae006a00e2a8a78e3
      incl_vat: false
      add_vat: 21
      entity_id: sensor.easyenergy_ceh_prices
  name: Easy Energy Cheapest Energy Hours
  unique_id: 9aedf25f-cfa7-4603-bcff-3f0c22a59fa1
```

#### NORDPOOL
```yaml
- use_blueprint:
    path: TheFes/energy_price_sensor.yaml
    input:
      source: nordpool
      config_entry: 01K7YVVKK4RJ9SA25SZVS0AR19
      price_factor: 0.001 # conversion from MWh prices to kWh
      add_vat: 21
      add_fixed: 0.023 # the fixed price added by your energy provider
      entity_id: sensor.nordpool_ceh_prices
  name: Nordpool Cheapest Energy Hours
  unique_id: 881b6558-26c6-44bb-81c5-d86c05451bd4
```

#### TIBBER
```yaml
- use_blueprint:
    path: TheFes/energy_price_sensor.yaml
    input:
      source: tibber
      entity_id: sensor.tibber_ceh_prices
  name: Tibber Cheapest Energy Hours
  unique_id: 2fc0bc4c-10c0-4844-8c12-ff50a80d44c8
```

### CREATE A TEMPLATE SENSOR TO CONVERT UNSOPPORTED DATA FORMATS

#### OMIE

This template sensor converts the data from the `omie` integration to a format which can be used by the macro.
Replace `sensor.omie_spot_price_es` (4 times) in the yaml code below with the entity_id used by you, and place this code in your configuration.yaml

```yaml
template:
  - sensor:
      - unique_id: fa408bd9-458d-4104-94a2-8d76a5065f80
        name: Omie prices for macro
        state: >
          {% set sensor = 'sensor.omie_spot_price_es' %}
          {{ states(sensor) if sensor | has_value else 'source sensor not available' }}
        attributes:
          tomorrow_valid: >
            {% set sensor = 'sensor.omie_spot_price_es' %}
            {{ (state_attr(sensor, 'tomorrow_hours') | default({'na': none}, true)).values() | first is not none }}
          raw_today: >
            {% set sensor = 'sensor.omie_spot_price_es' %}
            {% if sensor and sensor | has_value and state_attr(sensor, 'today_hours') is mapping %}
              {% set ns = namespace(today=[]) %}
              {% for k, v in state_attr('sensor.omie_spot_price_es', 'today_hours').items() if v | is_number %}
                {% set ns.today = ns.today + [dict(start=k.isoformat(), price=v)] %}
              {% endfor %}
              {{ ns.today }}
            {% else %}
              []
            {% endif %}
          raw_tomorrow: >
            {% set sensor = 'sensor.omie_spot_price_es' %}
            {% if false %}
              {% set ns = namespace(tomorrow=[]) %}
              {% for k, v in state_attr('sensor.omie_spot_price_es', 'tomorrow_hours').items() if v | is_number %}
                {% set ns.tomorrow = ns.tomorrow + [dict(start=k.isoformat(), price=v)] %}
              {% endfor %}
              {{ ns.tomorrow }}
            {% else %}
              []
            {% endif %}
```

#### SPAIN ELECTRICITY HOURLY PRICING (PVPC)

This template sensor converts the data from the `Spain electricity hourly pricing (PVPC)` integration to a format which can be used by the macro.
Replace `sensor.esios_pvpc` (4 times) in the yaml code below with the entity_id used by you, and place this code in your configuration.yaml

```yaml
template:
  - sensor:
      - unique_id: c3d573fe-ce23-49fe-bd6f-07825b9528ed
        name: PVPC prices for macro
        state: >
          {% set sensor = 'sensor.esios_pvpc' %}
          {{ states(sensor) if sensor | has_value else 'source sensor not available' }}
        attributes:
          tomorrow_valid: >
            {% set sensor = 'sensor.esios_pvpc' %}
            {{ states[sensor].attributes.keys() | select('search', '^price_next_day_.*h$') | list | count > 0 }}
          raw_today: >
            {% set sensor = 'sensor.esios_pvpc' %}
            {% set today = states[sensor].attributes.keys() | select('search', '^price_.*h$') | reject('search', 'next') | sort | list %}
            {% set ns = namespace(today=[]) %}
            {% for attr in today %}
              {% set h = attr.split('_')[-1] | replace('h', '') | int %}
              {% set ns.today = ns.today + [dict(start=(today_at()+timedelta(hours=h)).isoformat(), price=state_attr(sensor, attr))] %}
            {% endfor %}
            {{ ns.today }}
          raw_tomorrow: >
            {% set sensor = 'sensor.esios_pvpc' %}
            {% set tomorrow = states[sensor].attributes.keys() | select('search', '^price_next_day_.*h$') | sort | list %}
            {% set ns = namespace(tomorrow=[]) %}
            {% for attr in tomorrow %}
              {% set h = attr.split('_')[-1] | replace('h', '') | int %}
              {% set ns.tomorrow = ns.tomorrow + [dict(start=(today_at()+timedelta(hours=h)).isoformat(), price=state_attr(sensor, attr))] %}
            {% endfor %}
            {{ ns.tomorrow }}
```

### NAVIGATION
[PREVIOUS: CONTENTS](./0-how-to.md) | [CONTENTS](0-how-to.md) | [NEXT: BASIC DATA](2-basic_data.md)

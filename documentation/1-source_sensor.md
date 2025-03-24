# 1. SOURCE SENSOR

These parameters are used to determine where the source data can be found. If you use the custom [Nordpool integration](https://github.com/custom-components/nordpool) (can be downloaded using HACS), or an integration which uses the same attributes, you don't need to provide any of the parameters, but it is advised to provide the `sensor` as it will be more resource friendly if the macro doesn't need to search for it.

## 🚨 IMPORTANT NOTES 🚨
* It is advised to provide all parameters if they don't match the defaults. Although the macro will search for the attributes and keys, it is more resource friendly if they are already provided.
* If your sensor uses other attributes for the data of today and tomorrow, you need to provide the correct `sensor` parameter or the correct `attr_today` and `attr_tomorrow` parameters. It can't find the right sensor if the atrributes differ from the defaults, and it can't find the right attributes if the right sensor is not provided.
* In case `datetime_in_data` is set to `false` the attribute finder will not work, so you need to make sure to set `attr_today`, `attr_tomorrow` and/or `attr_all` yourself.

## PARAMETERS

### **sensor** <span style="color:grey">_string_</span>
The entity_id of the sensor containing the source data
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

|Data Provider|core integraton|parameters|comment|
|---|---|---|---|
|[Amber Electric](https://www.home-assistant.io/integrations/amberelectric/)|Yes|`attr_all='forecasts', time_key='start_time', value_key='per_kwh'`||
|[EasyEnergy](<https://www.home-assistant.io/integrations/easyenergy/>)|Yes|`time_key='timestamp'`|Using the template sensor [below](#energyzero-and-easyenergy)|
|[EnergyZero](<https://www.home-assistant.io/integrations/energyzero/>)|Yes|`time_key='timestamp'`|Using the template sensor [below](#energyzero-and-easyenergy)|
|[ENTSO-E](<https://github.com/JaccoR/hass-entso-e>)|No|`attr_today='prices_today', attr_tomorrow='prices_tomorrow', time_key='time', value_key='price'`||
|[Omie](<https://github.com/luuuis/hass_omie>)|No||Using the template sensor [below](#omie)|
|[Nordpool](<https://github.com/custom-components/nordpool>)|No||all set by default|
|[Spain electriciy hourly pricing (PVPC)](<https://www.home-assistant.io/integrations/pvpc_hourly_pricing/>)|Yes||Using the template sensor [below](#spain-electricity-hourly-pricing-pvpc)|
|[Tibber](https://www.home-assistant.io/integrations/tibber/)|Yes|`time_key='start_time'`|Using the template sensor [below](#tibber)|
|[Tibber](<https://github.com/Danielhiversen/home_assistant_tibber_custom>)|No|`attr_today='today', attr_tomorrow='tomorrow', datetime_in_data=false`|This uses the custom component, not the core integration|
|[Zonneplan](<https://github.com/fsaris/home-assistant-zonneplan-one>)|No|`attr_all='forecast', value_key='electricity_price'`||

## TEMPLATE SENSOR CONFIGURATION

### CREATING A FORECAST SENSOR USING THE ACTION

Some integrations (like the core [EnergyZero](<https://www.home-assistant.io/integrations/energyzero/>) and [EasyEnergy](<https://www.home-assistant.io/integrations/easyenergy/>) integrations) don't provide the forecast by default in an attribute. However they provide a service call to retrieve the prices. The example below shows how to set up a sensor to be used in the macro. The state of the sensor will be the current price, and the `price` attribute will contain the prices of yesterday, today and tomorrow (when available). Prices will be fetched every hour and upon Home Assistant startup.

For each energy provider, the configuration differs. In all cases the code above needs to be placed in your `configuration.yaml`. You can use a code editor (like [Visual Studio Code Add-on](https://my.home-assistant.io/redirect/supervisor_addon/?addon=a0d7b954_vscode) or [File Editor Add-on](https://my.home-assistant.io/redirect/supervisor_addon/?addon=core_configurator)). You cannot create these template sensors in the GUI, as trigger based template sensors are not supported as a GUI created template helper.

#### ENERGYZERO AND EASYENERGY

Notes:
* The example below is for EnergyZero. For EasyEnergy the service call is `easyenergy.get_energy_usage_prices` instead of `energyzero.get_energy_prices`
* The `config_entry` value in the service call will differ for each HA instance. The easiest way to get yours is to go to [Developer tools > Action](<https://my.home-assistant.io/redirect/developer_services/>) and select the action. Make sure you are in UI Mode, and select the right config entry. Switch to YAML mode to see the config entry.
* When `incl_vat` is set to `true`, the EnergyZero API will use a 2 decimal precision, when set to `false` it will be 5 decimal precision. If you want more precise prices, set `incl_vat` to `false` (like in the example below).

```yaml
template:
  - trigger:
      - alias: Triggers every hour
        platform: time_pattern
        hours: "/1"
      - alias: Triggers on home assistant startup
        platform: homeassistant
        event: start
    action:
      - alias: Collects the price information and stores this in a response variable
        action: energyzero.get_energy_prices # replace with the service call for your integration
        data:
          incl_vat: false
          config_entry: fe7bdc80dd3bc850138998d869f1f19d # replace with the config entry for your entity
          start: "{{ today_at() - timedelta(days=1) }}"
          end: "{{ today_at() + timedelta(days=2) }}"
        response_variable: prices
    sensor:
      - unique_id: 79c470d8-4ccd-4f44-b3a2-e3d59d5dda8a
        name: Energy Zero prices
        state: "{{ prices.prices | selectattr('timestamp', '<=', utcnow().strftime('%Y-%m-%d %H:%M:%S+00:00')) | map(attribute='price') | list | last }}"
        attributes:
          prices: "{{ prices.prices }}"
```

#### TIBBER
Home Assistant 2024.11.0 and above
```yaml
template:
  - trigger:
      - alias: Triggers every hour
        platform: time_pattern
        hours: "/1"
      - alias: Triggers on home assistant startup
        platform: homeassistant
        event: start
    action:
      - alias: Collects the price information and stores this in a response variable
        action: tibber.get_prices
        data:
          start: "{{ (today_at() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S') }}"
          end: "{{ (today_at() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S') }}"
        response_variable: prices
    sensor:
      - unique_id: 4283313c-8ccc-460f-8d4f-92b804cdc711
        name: tibber_forecast
        state: "{{ prices.prices.values() | first | selectattr('start_time', '<=', now().isoformat()) | map(attribute='price') | list | last }}"
        attributes:
          prices: >
            {% set ns = namespace(prices=[]) %}
            {% for i in prices.prices.values() | first %}
              {% set n = dict(start_time = i.start_time, price = i.price) %}
              {% set ns.prices = ns.prices + [n] %}
            {% endfor %}
            {{ ns.prices }}
```

Versions of Home Assitant before 2024.11.0 (2024.10 and lower)
```yaml
template:
  - trigger:
      - alias: Triggers every hour
        platform: time_pattern
        hours: "/1"
      - alias: Triggers on home assistant startup
        platform: homeassistant
        event: start
    action:
      - alias: Collects the price information and stores this in a response variable
        service: tibber.get_prices
        data:
          start: "{{ (today_at() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S') }}"
          end: "{{ (today_at() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S') }}"
        response_variable: prices
    sensor:
      - unique_id: 79c470d8-4ccd-4f44-b3a2-e3d59d5dda8a
        name: Tibber prices
        state: "{{ prices.prices.values() | first | selectattr('start_time', '<=', now()) | map(attribute='price') | list | last }}"
        attributes:
          prices: >
            {% set ns = namespace(prices=[]) %}
            {% for i in prices.prices.values() | first %}
              {% set n = dict(start_time = i.start_time.isoformat(), price = i.price) %}
              {% set ns.prices = ns.prices + [n] %}
            {% endfor %}
            {{ ns.prices }}
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

# Energy Price Sensor Blueprint

<img width="512" height="256" alt="dark_logo" src="https://github.com/user-attachments/assets/afee8c82-0367-42b0-ab3a-91e86079b48d" />

Some integrations don't provide the forecast by default in an attribute, this is the case for all modern core integrations, as they are not allowed to store forecasts in attriutes. However these integrations provide an action to retrieve the prices. 

I've createad a blueprint to create a template sensor which stores the prices in an attribute. The template sensor will store the prices for yesterday, today and tomorrow (when available). It will trigger every 15 minutes to ensure that the state is updated and reflects the current price. The prices for yesterday are also included as it makes it much easier to use the macro for periods which span the night, for example from 22:00 to 6:00.

It will only fetch prices using the action when needed, and only for the days which are still missing. If all prices are already stored in the sensor, it will only update the state and not use the API to retrieve the prices. This means that in normal cases it will only need to fetch the new data for tomorrow.

The blueprint can be used with the following core Home Assistant integrations

- [EasyEnergy](<https://www.home-assistant.io/integrations/easyenergy/>)
- [EnergyZero](<https://www.home-assistant.io/integrations/energyzero/>)
- [Nordpool](<https://www.home-assistant.io/integrations/nordpool/>)
- [Tibber](https://www.home-assistant.io/integrations/tibber/)

To use the blueprint, first import it using the button below:

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FTheFes%2Fcheapest-energy-hours%2Ftree%2Fmain%2Fblueprints%2Fenergy_price_sensor.yaml)

Note that after importing the blueprint it will **<ins>not</ins>** be shown in Settings > Automations & Scenes > Blueprints. Only automation and script blueprints will be shown there. 
There is currently no GUI support for template blueprints, so you need to use it with YAML configuration. For the supported integrations you will find examples below.

When using the template sensor created by this blueprint there is no need to provide settings for `attr_today`, `attr_tomorrow`, `attr_all`, `time_key` or `value_key` for the cheapest energy hours macro. The default settings will already be correct.

**<ins>Note:</ins>** This blueprint will create a template entity with a exceptionally large attribute with all the prices, especially when 15 minute prices are used. It will store 288 items (3 days with 96 items per day) with the date and time and the price for all those items. It is advisable to exclude this sensor from being included in the database. You can do that using the [recorder integration](<https://www.home-assistant.io/integrations/recorder/>). This can only be done using YAML, the below example excludes the template sensor from your database. For more information how to use includes and ex
```yaml
recorder:
  exclude:
    entities:
      - sensor.cheapest_energy_hour_prices # replace with the actual entity of your template sensor
```

## Blueprint inputs

The following inputs can be used in this blueprint:

### **<ins>entity_id</ins>** <span style="color:grey">_string (default: sensor.cheapest_energy_hour_prices)_</span>
The entity_id which will be used for the template sensor. It is important that the entity_id matches the actual entity_id of the template sensor. So if you change it in the GUI, make sure to change it in the settings for the template sensor as well.
***
### **<ins>source</ins>** <span style="color:grey">_string (default: null, possible options: easyenergy, energyzero, nordpool, tibber)_</span>
The source integration to be used by the blueprint. If no input is given, the blueprint will try to find one of the integrations. 
Note that this can lead to issues if the custom Tibber or custom Nordpool integration is installed. It is advised to select the right integration here.
***
### **<ins>config_entry</ins>** <span style="color:grey">_string (default: null)_</span>
The config entry id for the integration to be used by the blueprint. The blueprint will try to find this based on the source, but as it takes the first config entry id it can find, it can be advised to enter it yourself if you have multiple instances of the same integraton. To find it the easiest method is to go to [Developer tools > Action](<https://my.home-assistant.io/redirect/developer_services/>) and use one of the actions provided by the integration in GUI mode, select the config entry and then switch to YAML mode.
***
### **<ins>resolution</ins>** <span style="color:grey">_integer (default: 15, possible options: 15, 30, 60)_</span>
This setting is only used for Nordpool. By default 15 minute prices are fetched from Norpool, but you can set this to 30 or 60 to get the prices for those time periods. If you set it to any other value than 15, 30 or 60, then 15 minute resolution will be used.
***
### **<ins>add_vat</ins>** <span style="color:grey">_float (default: 0)_</span>
VAT perecentage which will be added to the prices
***
### **<ins>add_fixed</ins>** <span style="color:grey">_float (default: 0)_</span>
Fixed price which will be added to the prices. This can be used to add the uplift from your energy provider in case you use the Nordpool integration.
***
### **<ins>price_factor</ins>** <span style="color:grey">_float (default: 1 or 0.001)_</span>
All prices will be multiplied with this value. This will be applied before adding VAT or a fixed value. For most integrations this is set to 1 by default, but for Nordpool this is set to 0.001 as the prices provided by the Nordpool integration are for MWh instead of kWh.


## Examples

#### EASYENERGY

```yaml
- use_blueprint:
    path: TheFes/energy_price_sensor.yaml
    input:
      entity_id: sensor.easyenergy_ceh_prices
      source: easyenergy 
      add_vat: 21
  name: EasyEnergy Cheapest Energy Hours
  unique_id: 9aedf25f-cfa7-4603-bcff-3f0c22a59fa1
```

#### ENERGYZERO AND EASYENERGY

```yaml
- use_blueprint:
    path: TheFes/energy_price_sensor.yaml
    input:
      entity_id: sensor.energyzero_ceh_prices
      source: energyzero
      add_vat: 21
  name: EnergyZero Cheapest Energy Hours
  unique_id: 9aedf25f-cfa7-4603-bcff-3f0c22a59fa1
```

#### NORDPOOL
```yaml
- use_blueprint:
    path: TheFes/energy_price_sensor.yaml
    input:
      entity_id: sensor.nordpool_ceh_prices
      source: nordpool
      resolution: 60 # this will give hourly prices, remove the line or set to 15 for quarter-hourly prices
      add_vat: 21
      add_fixed: 0.023 # the fixed price added by your energy provider
  name: Nordpool Cheapest Energy Hours
  unique_id: 881b6558-26c6-44bb-81c5-d86c05451bd4
```

#### TIBBER
```yaml
- use_blueprint:
    path: TheFes/energy_price_sensor.yaml
    input:
      entity_id: sensor.tibber_ceh_prices
      source: tibber
  name: Tibber Cheapest Energy Hours
  unique_id: 2fc0bc4c-10c0-4844-8c12-ff50a80d44c8
```
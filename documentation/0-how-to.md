# HOW TO USE THIS MACRO

The information below explains how to use the macro in several sections, each section explains how the different related parameters of the macro work.

## 🚨 IMPORTANT NOTE 🚨

* The macro doesn't automatically update. If you use it in a template sensor for example, it will only update on changes of the source sensor (which usually happens at midnight, when tomorrow becomes today, and when the prices for tomorrow become available). To make sure it updates on the right interval you can create a [trigger based template sensor](https://www.home-assistant.io/integrations/template/#trigger-based-template-binary-sensors-buttons-images-numbers-selects-and-sensors) and choose when it should update by adding the right triggers, or add a line with `{% set n = now() %}` in your template to make it update each minute.


## CONTENTS
1. [Source sensor](./1-source_sensor.md)
2. [Basic data selection](2-basic_data.md)
3. [Advanced data selection (using weight factors)](./3-advanced_data.md)
4. [Data output](4-data_output.md)
5. [Error handling](5-error_handling.md)
6. [Examples](./6-examples.md)

### NAVIGATION
[NEXT: SOURCE SENSOR](./1-source_sensor.md)
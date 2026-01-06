<p align="center">
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/github/v/release/TheFes/cheapest-energy-hours)
[![Buy me a coffe](https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white)](https://www.buymeacoffee.com/TheFes)
[![Paypal](https://img.shields.io/badge/PayPal-00457C?&color=00457c&logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/thefes)
</p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="/logo/TheFesCasa_logo_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="/logo/TheFesCasa_logo_light.png">
  <img alt="Shows a black thefes.casa logo in light color mode and a white one in dark color mode." src="/logo/TheFesCasa_logo_light.png">
</picture>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/logo/dark_logo.png">
    <source media="(prefers-color-scheme: light)" srcset="/logo/logo.png">
    <img alt="Shows a black logo Cheapest Energy hours logo in light color mode and a white one in dark color mode." src="/logo/dark_logo.png">
  </picture>
</p>

A jinja macro to easily find the cheapest block of hours to know when to turn on your dryer (and much more)

# Why this macro

If your energy provider uses dynamic pricing, you might want to know when to turn on devices which consume a lot of power. It is relatively easy to find the lowest price on the day, but if it takes 3 hours for your dryer to complete, you might want to find the cheapest block of hours. It could be that the cheapest hour is not even in that block.
This macro comes to the rescue!

Funny note 😄 I don't have a dynamic price contract myself. It started as a challenge to myself to get it working, and gradually expanded to what it is now. I do have the Nordpool and ENTSOE integrations installed to test, but I don't have real life scenario's implemented, so I'm also depending on your feedback to improve the macro even further. So please keep sending in issues/questions/other feedback.

In case you are able to reduce your energy bill by using this macro, please consider to buy me a cup of coffee ☕

# What does it do?
Installing this macro will not create any entities in Home Assistant. It will only provide you with a custom template which can be used in Jinja templating to create template sensors or template binary sesnors yourself. In documentation you will find more information on how to do this, and some examples of real life configurations.

# What does it need?
To find the lowest price, basically the only thing the macro needs are the prices itself. Those can be provided in a sensor, like e.g. the custom Nordpool integration, using an action with a action response, like with the core Nordpool integration, or maybe from a csv-file.

# How to install
You need to have Home Assistant 2023.11 or higher installed to use this custom template.

This custom template is compatible with [HACS](https://hacs.xyz/), which means that you can easily download and manage updates for it. Custom templates are available for download in HACS 2.0 and up, and on earlier versions in case experimental features are enabled. When you are on HACS 2.0 or higher or experimental features are enabled you can click the button below to add it to your HACS installation:
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TheFes&repository=cheapest-energy-hours&category=template)

For a manual install you can copy the contents of `cheapest_energy_hours.jinja` to a jinja file in your `custom_templates` folder.
Run the `homeassistant.reload_custom_templates` service call to load the file.

# How to use
See the separate [documentation](./documentation/0-how-to.md) on how to use the macro

# Thanks to
* [@rrozema](https://github.com/rrozema) for testing and providing feedback on the blueprint for the energy price sensor
* [@basbruss](https://github.com/basbruss) for providing the output mode and a lot of other additions!
* [@hmmbob](https://github.com/hmmbob) for reviewing the 5.0.0 documentation
* All users of the macro, especially those who provide valuable feedback in questions, issue reports or feature requests


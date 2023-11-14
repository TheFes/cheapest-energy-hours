[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/github/v/release/TheFes/cheapest-energy-hours)
[![Buy me a coffe](https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white)](https://www.buymeacoffee.com/TheFes)
[![Paypal](https://img.shields.io/badge/PayPal-00457C?&color=00457c&logo=paypal&logoColor=white)]()


A jinja macro to easily find the cheapest block of hours to know when to turn on your dryer

# Why this macro

If your energy provider uses dynamic pricing, you might want to know when to turn on devices which consume a lot of power. It is relatively easy to find the lowest price on the day, but if it takes 3 hours for your dryer to complete, you might want to find the cheapest block of hours. It could be that the cheapest hour is not even in that block.
This macro comes to the rescue!

# How to install
You need to have Home Assistant 2023.11 or higher installed to use this custom template.

This custom template is compatible with [HACS](https://hacs.xyz/), which means that you can easily download and manage updates for it. Custom templates are currently only available in HACS when you enable experimental features. Make sure to enable it in the HACS settings, which you can access from Settings > [Devices & Services](https://my.home-assistant.io/create-link/?redirect=integrations) > HACS When experimental features are enabled you click the button below to add it to your HACS installation,
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TheFes&repository=cheapest-energy-hours&category=template)


For a manual install you can copy the contents of `cheapest_energy_hours.jinja` to a jinja file in your `custom_templates` folder.
Run the `homeassistant.reload_custom_templates` service call to load the file.

# How to use
See the separate [documentation](./documentation/0-how-to.md) on how to use the macro

# Thanks to
* [@basbruss](https://github.com/basbruss) for providing the output mode and a lot of other additions!


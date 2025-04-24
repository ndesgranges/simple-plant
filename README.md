
![Simple Plant Icon](custom_components/simple_plant/brands/icon/icon.png)
# Simple Plant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

Simple plant aims to provide a very simple integration to help you list and take care of your plants without any external service or sensor.

## Context

Over the years, I've acquired a lot of plants. It became hard to remember when to water my plants.

I've been testing a lot of services just to help me with this task, but the integration in home assistant was not great. Even Home assistant itself provide a plant integration that I find somewhat useless if you don't have "plant" sensor (those ones you put in the ground).

Simple plant aims to fix this.

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ndesgranges&repository=simple-plant&category=integration)

OR

1. Install HACS if you don't have it already
2. Open HACS in Home Assistant
3. On the top right side, click the three dot and click `Custom repositories`
4. Where asked for a URL, paste the link of this repository:
https://github.com/ndesgranges/simple-plant
5. Where asked for a type, select `integration`
4. Click the download button. ⬇️


## Entities

This integration provides the following entities

> NOTE: \
> In the following table, `@` represent the name of the device, for example, If I've got a device called "Foo" `test_@` would be `test_foo`

| Entity                                           | Description                                                                                                                         |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| binary_sensor.simple_plant_**todo**_@            | `true` if the plant needs to be watered                                                                                             |
| binary_sensor.simple_plant_**problem**_@         | `true` (and labelled as problem) if the plant "water date" is overdue                                                               |
| button.simple_plant_**mark_watered**_@           | Mark the plant as watered                                                                                                           |
| date.simple_plant_**last_watered**_@             | Last time the plant has been marked as watered. In Theory it should not need to be changed manually, but it's there for flexibility |
| image.simple_plant_**picture**_@                 | Just a picture of your plant to show in your dashboard                                                                              |
| number.simple_plant_**days_between_waterings**_@ | Amount of days to wait before each watering before notifying                                                                        |
| select.simple_plant_**health**_@                 | A manual dumb selector just to note the current health of your plant, it doesn't do anything else                                   |

## TODO

  - [ ] Better linking of the internal name given through config flow and name given through home assistant "rename" [#3](https://github.com/ndesgranges/simple-plant/issues/3)
  - [ ] Ability to change image See [#4](https://github.com/ndesgranges/simple-plant/issues/4)
  - [x] Add a dashboard widget or give an example [#5](https://github.com/ndesgranges/simple-plant/issues/5)
  - [ ] Investigate state colors [#7](https://github.com/ndesgranges/simple-plant/issues/7)
  - [x] Add a sensor entity with a date value: the date when the watering "is due" [#8](https://github.com/ndesgranges/simple-plant/issues/8)
  - [ ] Slugify the name where its used as device id

## Credits


Even though it is not so much alike anymore, this project has been started using [ludeeus/integration_blueprint](https://github.com/ludeeus/integration_blueprint) template

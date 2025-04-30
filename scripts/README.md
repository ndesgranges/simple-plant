# Scripts

## Setup

This repository features a ready-to-dev environment using vscode `.devcontainer.json`
This allows creating a docker container with everything ready for development

At container creation, the script `scripts/setup` is ran.

## Develop

The script `scripts/develop` launches Home Assistant

## Copy

The script `scripts/cp` allows copying the card in the `config/` directory of Home Assistant
so it can be accessed in there. With option `--all` it also copies the
integration

## Faketime

During setup (see [§setup](#setup)), libfaketime is installed, this allows controlling the time and
date inside the container for testing purpose. This date/time can be changed
by exporting the variable `FAKETIME` before launching Home Assistant.

Example :

```sh
export FAKETIME='@2025-12-30 23:55:00'
```

or to set it to the current date/time :
```sh
export FAKETIME="+0d"
```

Sometimes, this might create errors in Home assistant, so removing
temporarily `LD_PRELOAD` in `.devocontainer` and rebooting the container
when stuck on a issue can be a good thing to try !
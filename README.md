<!-- omit in toc -->
# synadm - the Synapse Admin CLI

- [About](#about)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Getting an Admin Token](#getting-an-admin-token)
  - [The configurator](#the-configurator)
  - [matrix-docker-ansible-deploy](#matrix-docker-ansible-deploy)
- [Usage](#usage)
  - [Command Line Reference](#command-line-reference)
  - [Advanced Usage](#advanced-usage)
- [Update](#update)
  - [Update PyPI Package](#update-pypi-package)
  - [Update git Installation](#update-git-installation)
- [Implementation Status / Commands List](#implementation-status--commands-list)
- [Get in Touch](#get-in-touch)
- [Contributing](#contributing)


## About

A CLI tool to help admins of [Matrix-Synapse homeservers](https://github.com/matrix-org/synapse) conveniently issue commands available via its [Admin API](https://element-hq.github.io/synapse/develop/usage/administration/admin_api/index.html#the-admin-api).


## Prerequisites

- Python 3.6+
- a running Synapse instance
- an admin-enabled user on the instance
- the admin user's access token

`synadm` is designed to run either directly on the host running the Synapse instance or on a remote machine able to access Synapse's API port. Synapse's default Admin API endpoint address usually is http://localhost:8008/_synapse/admin or https://localhost:8448/_synapse/admin.


## Installation

If `pipx` is available on your operating system, it is the recommended method for installation:

`pipx install synadm`

Alternatively, regular `pip` can also be used:

`pip3 install synadm`

To install the latest version from Git to a Python virtual environment [see the chapter in the contributing docs](https://synadm.readthedocs.io/en/latest/contributing.html#getting-the-source-and-installing).


## Configuration

`synadm` stores its configuration inside the executing user's home directory in `~/.config/synadm.yaml` and is handled by [the synadm configurator](#the-configurator). Usually it's not required to edit it manually.

### Getting an Admin Token

To find out your admin user's token in Element-Web: _Login as this user - "Click User Avatar" - "All Settings" - "Help & About" - Scroll down - "Advanced" - "Access Token"_

Or use synadm to fetch a token already. Use the fully qualified Matrix ID of the admin user:

```
synadm matrix login @admin_username:yourdomain.org
Password:
```

If you issue this command in a fresh `synadm` installation, [the configurator](#the-configurator) will launch anyway.

- Answer the questions.
- Set token to "invalid" at first, to convience `synadm` to launch the `matrix login` command (otherwise you'd get a "Configuration incomplete" error).
- After successfully entering your admin password you will be presented a token which you can finally set by re-launching the configurator as described below.


### The configurator

`synadm` asks for necessary configuration items on first launch automatically. Also whenever new mandatory configuration items where added (eg after an update), the user will be prompted for missing items automatically.

Configuration can be changed any time by launching the configurator directly:

```
synadm config
```

Configuration will be saved in `~/.config/synadm.yaml`

*Note: Be aware that once you configured `synadm`, your admin user's token is saved in the configuration file. On Posix compatible systems permissions are set to mode 0600, on other OS's it is your responsibilty to change permissions accordingly.*

### matrix-docker-ansible-deploy

To use `synadm` with Synapse homeservers that were installed using [matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy) you have two options.

Access the Synapse Admin API's "via the public endpoint" similar to a Matrix client.

- In [vars.yaml](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/configuring-playbook.md#configuring-the-ansible-playbook) set `matrix_nginx_proxy_proxy_matrix_client_api_forwarded_location_synapse_admin_api_enabled: true`.
- The API's are accessible on the Client-Server API port, at `https://matrix.DOMAIN`.
- Install `synadm` on your Docker host or on a separate machine.
- Configure `synadm` to access at `https://matrix.DOMAIN:443/_synapse/admin`

Alternatively, you can access the API's on the container network `matrix`.

- Synapse is accessible via the hostname `matrix-synapse` resolved by the internal Docker DNS server.
- The containers are connected internally via a network named `matrix` by default.
- Start a container on that same network and install `synadm` into it.
- Configure `synadm` to access at `http://matrix-synapse:8008/_synapse/admin` (http here, not https).

Find some more details about the topic in [this issue post on the matrix-docker-ansible-deploy repo](https://github.com/spantaleev/matrix-docker-ansible-deploy/issues/1846#issuecomment-1135516112).

_Note that currently `synadm` is using a part of the Server-Server (Federation) API (`keys/v2/server`) to retrieve "its own homeserver name". This affects some of the `media` management commands. By default and also as the Matrix spec recommends, this API is not accessible via the Client-Server API port. We are working on a better solution to retrieve the own servername but as a workaround the `key` API's can be exposed by setting `matrix_synapse_http_listener_resource_names: ["client","keys"]` in [vars.yaml](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/configuring-playbook.md#configuring-the-ansible-playbook)._

Find more details about the topic [here](https://github.com/spantaleev/matrix-docker-ansible-deploy/issues/1761#issuecomment-1101170229).


## Usage

Use the online help of the main command:

```
synadm -h
```

and of the available subcommands:

```
synadm version -h
synadm user -h
synadm room -h
```

You even can spare the `-h` option, `synadm` will show some abbreviated help for the executed subcommand anyway. For example:

```
synadm user
```
or
```
synadm user details
```

will show essential help for the particular subcommand right away.

*Note: A list of currently available commands is found in chapter [implementation status / commands list](#implementation-status--commands-list)* as well as in the following chapter.

### Command Line Reference

A detailed [Command Line Reference](https://synadm.readthedocs.io/en/latest/index_cli_reference.html) can be found in `synadm's` readthedocs documentation.

### Advanced Usage

Examples of how `synadm` can be used in shell scripts and oneliners is
provided in the
[Scripting Examples](https://synadm.readthedocs.io/en/latest/examples.html)
docs chapter.


## Update

### Update PyPI Package

```
pip3 install synadm --upgrade
```

### Update git Installation

To update `synadm` to the latest development state, just update your git repo and reinstall:

```
cd synadm
git pull
pip install .
```

*Note: If you installed it to a Python venv, [activate it](CONTRIBUTING.md#3-set-up-a-python3-virtual-environment).*

*Note: If you installed it in [editable mode](CONTRIBUTING.md#4-install-in-editable-mode) (or for development), you can spare the `pip install .` command - just `git pull` and you're done.*



## Implementation Status / Commands List

The [API to CLI Mapping](https://synadm.readthedocs.io/en/latest/features.html) section of our documentation provides an overview of what `synadm` can do.


## Get in Touch

If you need advice on using synadm, have a feature idea or would like to discuss anything else around `synadm`, get in touch via Matrix!

We are hanging around in the official support room for Synapse, [#synapse:matrix.org](https://matrix.to/#/#synapse:matrix.org). Usually you'll find `synadm` users there that might answer your questions already. If not, mentioning `synadm` will ping us with the help of Element's keyword notify feature and we'll try to get in touch.

The most direct way to reach synadm maintainers as well as seasoned users and Synapse admins is by joining [#synadm:peek-a-boo.at](https://matrix.to/#/#synadm:peek-a-boo.at).

If you are sure you've found a bug that was not already reported, certainly directly [opening an issue](https://codeberg.org/synadm/synadm/issues) is a valid option too. If unsure, ask in [#synadm:peek-a-boo.at](https://matrix.to/#/#synadm:peek-a-boo.at) first.



## Contributing

First of all, thanks for your interest in contributing to `synadm`! We appreciate any help, no matter if you are a programmer or a user. Both groups can do valuable things for the `synadm` project. We love providing a useful tool to fellow Synapse sysadmins but rely on contribution from the Synapse and Matrix community to keep `synadm` useful, current and stable.

Please review the [contributing docs](https://synadm.readthedocs.io/en/latest/contributing.html) for guidelines and help around the topic!

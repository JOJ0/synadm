<!-- omit in toc -->
# synadm - the Matrix-Synapse admin CLI

- [About](#about)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Install from PyPI](#install-from-pypi)
  - [Install from git](#install-from-git)
- [Configuration](#configuration)
  - [Getting an admin token](#getting-an-admin-token)
  - [The configurator](#the-configurator)
  - [matrix-docker-ansible-deploy](#matrix-docker-ansible-deploy)
- [Usage](#usage)
- [Update](#update)
  - [Update PyPI package](#update-pypi-package)
  - [Update git installation](#update-git-installation)
- [Implementation status / commands list](#implementation-status--commands-list)
- [Get in touch / feedback / support](#get-in-touch--feedback--support)
- [Contribution](#contribution)
  - [How can I help?](#how-can-i-help)
  - [Install to virtual environment](#install-to-virtual-environment)
  - [Install in development mode](#install-in-development-mode)
  - [Implementation examples](#implementation-examples)
  - [Developer's documentation](#developers-documentation)




## About

A CLI tool to help admins of [Matrix-Synapse homeservers](https://github.com/matrix-org/synapse) conveniently issue commands available via its [admin API](https://matrix-org.github.io/synapse/develop/usage/administration/admin_api/index.html#the-admin-api).



## Prerequisites

- Python 3.6+
- a running Synapse instance
- an admin-enabled user on the instance
- the admin user's access token

`synadm` is designed to run either directly on the host running the Synapse instance or on a remote machine able to access Synapse's API port. Synapse's default admin API endpoint address usually is http://localhost:8008/_synapse/admin or https://localhost:8448/_synapse/admin.




## Installation

### Install from PyPI

`pip3 install synadm`

### Install from git

<!-- omit in toc -->
#### 1. Check Python version

`python3 --version` should show at least v3.6.x

<!-- omit in toc -->
#### 2. Clone repo:

```
git clone https://github.com/joj0/synadm
```

<!-- omit in toc -->
#### 3. Install package globally

This will install `synadm` and all dependent Python packages to your system's global Python site-packages directory:

```
cd synadm
sudo python3 setup.py install
```

*Note: If you get an import error for setuptools, make sure the package is installed. Debian based systems: `sudo apt install python3-setuptools`, RedHat based: `sudo yum install python3-setuptools`* 

<!-- omit in toc -->
#### 4. Run

`synadm` should now run fine without having to add a path in front of it:

```
synadm -h
```

*Note: Usually setuptools installs a command wrapper to `/usr/local/bin/synadm`, but that depends on your system.*

*Note: In case you don't want `synadm` to be installed to a global system directory see chapter [install to virtual environment](#install-to-virtual-environment).*

*Note: synadm is multi-user aware - it stores its configuration inside the executing user's home directory. See chapter [configuration](#configuration).*



## Configuration

### Getting an admin token

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

A detailed [Command Line Reference](https://synadm.readthedocs.io/en/latest/index_cli_reference.html) can be found in `synadm's` readthedocs documentation.

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

*Note: A complete list of currently available commands is found in in chapter [implementation status / commands list](#implementation-status--commands-list)*

## Update

### Update PyPI package

```
pip3 install synadm --upgrade
```

### Update git installation

To update `synadm` to the latest development state, just update your git repo and reinstall:

```
cd synadm
git pull
python3 setup.py install
```

*Note: If you installed to a Python venv, first load it as described in [install to virtual environment](#install-to-virtual-environment).*

*Note: If you installed in [development mode](#install-in-development-mode) you can spare the `python3 setup.py install` command - just `git pull` any you're done.*



## Implementation status / commands list

[Follow this link to the official Synapse Admin API docs](https://matrix-org.github.io/synapse/develop/usage/administration/admin_api/index.html) - direct links to the specific API documentation pages are provided in the list below.

*Note: Most commands have several optional arguments available. Put -h after any of the below listed commands to view them or have a look at the [Command Line Reference](https://synadm.readthedocs.io/en/latest/index_cli_reference.html).*


* [ ] [Account Validity](https://matrix-org.github.io/synapse/develop/admin_api/account_validity.html)
* [x] [Delete Group](https://matrix-org.github.io/synapse/develop/admin_api/delete_group.html) (delete community)
* [ ] [Event Reports](https://matrix-org.github.io/synapse/develop/admin_api/event_reports.html)
* [x] [Media Admin](https://matrix-org.github.io/synapse/develop/admin_api/media_admin_api.html)
  * [x] `media list -r <room id>`
  * [x] `media list -u <user id>` (alias of `user media <user id>`)
  * [x] `media quarantine -s <server name> -i <media id>`
  * [x] `media quarantine -r <room id>`
  * [x] `media quarantine -u <room id>`
  * [x] `media protect <media id>`
  * [x] `media delete -s <server name> -i <media id>`
  * [x] `media delete -s <server name> --before <date> --size 1024`
  * [x] `media purge --before <date>` (purge remote media API)
* [x] [Purge History](https://matrix-org.github.io/synapse/develop/admin_api/purge_history_api.html)
  * [x] `history purge <room id>`
  * [x] `history purge-status <purge id>`
* [x] ~~[Purge Rooms](https://matrix-org.github.io/synapse/develop/admin_api/purge_room.html)~~ (DEPRECATED, covered by `room delete`)
* [ ] [Register Users](https://matrix-org.github.io/synapse/develop/admin_api/register_api.html)
* [x] [Manipulate Room Membership](https://matrix-org.github.io/synapse/develop/admin_api/room_membership.html)
  * [x] `room join`
* [x] [Rooms](https://matrix-org.github.io/synapse/develop/admin_api/rooms.html)
  * [x] `room list`
  * [x] `room details <room id>`
  * [x] `room members <room id>`
  * [x] `room delete <room id>`
  * [x] `room make-admin <room id> <user id>`
  * [x] `room state <room id>`
  * [ ] Additional commands and aliases around room management
    * [x] `room search <search-term>` (alias of `room list -n <search-term>`)
    * [x] `room resolve <room alias>`
    * [x] `room power-levels`
    * [ ] `room count`
    * [ ] `room top-complexity`
    * [ ] `room top-members`
* [x] [Server Notices](https://matrix-org.github.io/synapse/develop/admin_api/server_notices.html)
* [x] ~~[Shutdown Room](https://matrix-org.github.io/synapse/develop/admin_api/shutdown_room.html)~~ (DEPRECATED, covered by `room delete`)
* [ ] [Statistics](https://matrix-org.github.io/synapse/develop/admin_api/statistics.html)
* [x] [Users](https://matrix-org.github.io/synapse/develop/admin_api/user_admin_api.html)
  * [x] `user details <user id>`
  * [x] `user modify <user id>` (also used for user creation)
  * [x] `user list`
  * [x] `user deactivate <user id>` (including GDPR erase)
  * [x] `user password <user id>`
  * [x] `user membership <user id>`
  * [x] `user whois <user id>`
  * [x] `user shadow-ban <user id>`
  * [x] `user media -u <user id>` (also available as `media list -u <user id>`)
  * [x] `user login <user id>`
  * [ ] Additional commands and aliases around user management
      * [x] `user search <search-term>` (shortcut to `user list -d -g -n <search-term>`)
      * [ ] `user create <user id>` (alias of `user modify ...`)
      * [x] `user prune-devices <user id>`
* [x] [Server Version](https://matrix-org.github.io/synapse/develop/admin_api/version_api.html)
  * [x] `version`
* [x] [Registration Tokens](https://matrix-org.github.io/synapse/latest/usage/administration/admin_api/registration_tokens.html)
  * [x] `regtok list`
  * [x] `regtok details <registration token>`
  * [x] `regtok new`
  * [x] `regtok update <registration token>`
  * [x] `regtok delete <registration token>`




## Get in touch / feedback / support

If you need help with installing, usage or contribution or have anything else on your mind, just join public matrix room [#synadm:peek-a-boo.at](https://matrix.to/#/#synadm:peek-a-boo.at) and get in touch. I am also hanging around on [#matrix-dev:matrix.org](https://matrix.to/#/#matrix-dev:matrix.org) and [#synapse:matrix.org](https://matrix.to/#/#synapse:matrix.org) regularily. Just ask for a jojo ;-)




## Contribution

### How can I help?

* Install `synadm` and report back whether or not the installation process worked on the OS you're running.
* Read the [Synapse admin API docs](https://github.com/matrix-org/synapse/tree/master/docs/admin_api), pick a feature, implement it and send a pull-request - see [implementation examples chapter](#implementation-examples), it really isn't hard, take a look!
* If you don't code, you can still help me prioritize what to code next: Pick a feature from the docs just mentioned, open a github issue in this repo and tell me what it is. Alternatively just catch me on [#synadm:peek-a-boo.at](https://matrix.to/#/#synadm:peek-a-boo.at) or [#matrix-dev:matrix.org](https://matrix.to/#/#matrix-dev:matrix.org).

Thanks in advance for any help! I can't do this without you!


### Install to virtual environment

If you'd rather prefer to install `synadm` into its own private virtual Python environment or even would like to help code it, this is a much cleaner approach compared to the steps descibed in the [main installation chapter](#installation)

<!-- omit in toc -->
#### 1. Check Python version

`python3 --version` should show at least v3.6.x

<!-- omit in toc -->
#### 2. Clone repo:

```
git clone https://github.com/joj0/synadm
```

<!-- omit in toc -->
#### 3. Setup and load a new Python3 virtual environment


Create and activate a virtual environment using the python3 venv module:

```
python3 -m venv ~/.venvs/synadm
source ~/.venvs/synadm/bin/activate
```

Once your Python virtual environment is loaded and your prompt looks similar to `(synadm) ....  $ `, install directly into the environment:


<!-- omit in toc -->
#### 4. Install

```
cd synadm
python3 setup.py install
```

*Note: Don't forget to activate the venv when coming back to using `synadm` after a fresh login: `source ~/.venvs/synadm/bin/activate`*

<!-- omit in toc -->
#### 5. Run

As long as your venv is loaded `synadm` should run fine without having to add a path in front of it

```
synadm -h
```




### Install in development mode

If you'd like to contribute to synadm's development, it's recommended to use a venv as described above, and also use a slightly different installation command:

```
cd synadm
python3 setup.py develop
```

*Note: When installed like this, code-changes inside the repo dir will immediately be available when executing `synadm`. This could also be used as a quick way to just stay on top of synadm's development.*


### Implementation examples

Without much talk, have a look at this method: https://github.com/JOJ0/synadm/blob/107d34b38de71d6d21d78141e78a1b19d3dd5379/synadm/cli/user.py#L185

and this one: https://github.com/JOJ0/synadm/blob/107d34b38de71d6d21d78141e78a1b19d3dd5379/synadm/api.py#L80

That's all it needs to implement command `synadm user details <user_id>`.

And another example, this time using a POST based API endpoint. It implements command `synadm user password <user_id>`. This is the CLI-level method: https://github.com/JOJ0/synadm/blob/0af918fdeee40bc1d3df7b734a46e76bb31148b9/synadm/cli/user.py#L114

and again it needs a backend method in api.py:
https://github.com/JOJ0/synadm/blob/107d34b38de71d6d21d78141e78a1b19d3dd5379/synadm/api.py#L72

### Developer's documentation

Have a look at [synadm's module documentation pages on readthedocs](https://synadm.readthedocs.io/en/latest/index_modules.html)

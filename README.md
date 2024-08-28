<!-- omit in toc -->
# synadm - the Matrix-Synapse admin CLI

- [About](#about)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Update](#update)
- [Configuration](#configuration)
  - [The configurator](#the-configurator)
  - [Getting an Admin Token](#getting-an-admin-token)
  - [matrix-docker-ansible-deploy](#matrix-docker-ansible-deploy)
- [Usage](#usage)
  - [Command Line Reference](#command-line-reference)
  - [Advanced Usage](#advanced-usage)
- [Implementation Status / Commands List](#implementation-status--commands-list)
- [Support](#support)
- [Contributing](#contributing)

## About

A CLI tool for the [Synapse Admin API](https://element-hq.github.io/synapse/develop/usage/administration/admin_api/index.html#the-admin-api).

## Prerequisites

- Python 3.6+
- a running Synapse instance
- an admin-enabled user on the instance
- the admin user's access token

`synadm` is designed to run either directly on the host running the Synapse instance or on a remote machine able to access Synapse's API port. Synapse's default Admin API endpoint address usually is `http://localhost:8008/_synapse/admin` or `https://localhost:8448/_synapse/admin`.

## Installation

To install synadm from PyPI, run the following command:

`pip3 install synadm`

Other installation methods: [Install via Git](https://github.com/JOJ0/synadm/blob/master/CONTRIBUTING.md#getting-the-source--installing)

## Update

If you already have synadm installed from the PyPI, run this to upgrade synadm to a new release:

```
pip3 install synadm --upgrade
```

## Configuration

### The configurator

`synadm` asks for necessary configuration items on first launch automatically. Also whenever new mandatory configuration items where added (eg after an update), the user will be prompted for missing items automatically.

Configuration can be changed any time by launching the configurator directly:

```
synadm config
```

Configuration will be saved in `~/.config/synadm.yaml`

*Note: Be aware that once you configured `synadm`, your admin user's token is saved in the configuration file. On Posix compatible systems permissions are set to mode 0600, on other OS's it is your responsibilty to change permissions accordingly.*

### Getting an Admin Token

To find out your admin user's token in Element-Web: _Login as this user - "Click User Avatar" - "All Settings" - "Help & About" - Scroll down - "Advanced" - "Access Token"_

You can also use synadm to fetch a token by logging in. Use the fully qualified Matrix ID of the admin user:

```
synadm matrix login @admin_username:yourdomain.org
Password:
```

If you issue this command in a fresh `synadm` installation, [the configurator](#the-configurator) will launch anyway.

- Answer the questions.
- Set token to "invalid" at first, to convience `synadm` to launch the `matrix login` command (otherwise you'd get a "Configuration incomplete" error).
- After successfully entering your admin password you will be presented a token which you can finally set by re-launching the configurator as described below.

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

Get help information for the top level commands by running:

```
synadm -h
```

Similar to subcommands:

```
synadm version -h
synadm user -h
synadm room -h
```

For commands with subcommands, help will be shown by default when running
something like:
```
synadm user
```
or
```
synadm user details
```

*Note: A list of currently available commands is found in chapter [implementation status / commands list](#implementation-status--commands-list)* as well as in the following chapter.

### Command Line Reference

A detailed [Command Line Reference](https://synadm.readthedocs.io/en/latest/index_cli_reference.html) can be found in `synadm's` readthedocs documentation.

### Advanced Usage

Examples of how `synadm` can be used in shell scripts and oneliners is
provided in the
[Scripting Examples](https://synadm.readthedocs.io/en/latest/examples.html)
docs chapter.

## Implementation Status / Commands List

[Follow this link to the official Synapse Admin API docs](https://element-hq.github.io/synapse/develop/usage/administration/admin_api/index.html) - direct links to the specific API documentation pages are provided in the list below.

*Note: Most commands have several optional arguments available. Put -h after any of the below listed commands to view them or have a look at the [Command Line Reference](https://synadm.readthedocs.io/en/latest/index_cli_reference.html).*

* [ ] [Account Validity](https://element-hq.github.io/synapse/develop/admin_api/account_validity.html)
* [x] [Delete Group](https://element-hq.github.io/synapse/develop/admin_api/delete_group.html) (delete community)
* [ ] [Event Reports](https://element-hq.github.io/synapse/develop/admin_api/event_reports.html)
* [x] [Media Admin](https://element-hq.github.io/synapse/develop/admin_api/media_admin_api.html)
  * [x] `media list -r <room id>`
  * [x] `media list -u <user id>` (alias of `user media <user id>`)
  * [x] `media quarantine -s <server name> -i <media id>`
  * [x] `media quarantine -r <room id>`
  * [x] `media quarantine -u <room id>`
  * [x] `media protect <media id>`
  * [x] `media delete -s <server name> -i <media id>`
  * [x] `media delete -s <server name> --before <date> --size 1024`
  * [x] `media purge --before <date>` (purge remote media API)
* [x] [Purge History](https://element-hq.github.io/synapse/develop/admin_api/purge_history_api.html)
  * [x] `history purge <room id>`
  * [x] `history purge-status <purge id>`
* [x] ~~[Purge Rooms](https://element-hq.github.io/synapse/develop/admin_api/purge_room.html)~~ (DEPRECATED, covered by `room delete`)
* [ ] [Register Users](https://element-hq.github.io/synapse/develop/admin_api/register_api.html)
* [x] [Manipulate Room Membership](https://element-hq.github.io/synapse/develop/admin_api/room_membership.html)
  * [x] `room join`
* [x] [Rooms](https://element-hq.github.io/synapse/develop/admin_api/rooms.html)
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
    * [x] `room block`
    * [x] `room block-status`
* [x] [Server Notices](https://element-hq.github.io/synapse/develop/admin_api/server_notices.html)
* [x] ~~[Shutdown Room](https://element-hq.github.io/synapse/develop/admin_api/shutdown_room.html)~~ (DEPRECATED, covered by `room delete`)
* [ ] [Statistics](https://element-hq.github.io/synapse/develop/admin_api/statistics.html)
  * [ ] `synadm media user-stats`
  * [ ] `synadm room largest`
* [x] [Users](https://element-hq.github.io/synapse/develop/admin_api/user_admin_api.html)
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
* [x] [Server Version](https://element-hq.github.io/synapse/develop/admin_api/version_api.html)
  * [x] `version`
* [x] [Registration Tokens](https://element-hq.github.io/synapse/latest/usage/administration/admin_api/registration_tokens.html)
  * [x] `regtok list`
  * [x] `regtok details <registration token>`
  * [x] `regtok new`
  * [x] `regtok update <registration token>`
  * [x] `regtok delete <registration token>`

## Support

If you need help with using `synadm`, have a feature idea or would like to discuss anything else around `synadm`, get in touch via [our Matrix room][synadmroom]!

If you have questions about Synapse (the homeserver), you should join [the room for Synapse](https://matrix.to/#/#synapse:matrix.org). That room should help you better answer Synapse questions.

If you are sure you've found a bug that was not already reported, opening an [issue on GitHub](https://github.com/JOJ0/synadm/issues) is a valid option too. If unsure, ask in [#synadm:peek-a-boo.at][synadmroom] first.

[synadmroom]:https://matrix.to/#/#synadm:peek-a-boo.at

## Contributing

First of all, thanks for your interest in contributing to `synadm`! We appreciate any help, no matter if you are a programmer or a user.

Please review the [contributing docs](CONTRIBUTING.md) for guidelines and help around the topic!

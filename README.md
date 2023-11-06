<!-- omit in toc -->
# synadm - the Matrix-Synapse admin CLI

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
- [Implementation Status / Commands List](#implementation-status--commands-list)
- [Get in Touch](#get-in-touch)
- [Contributing](#contributing)

## About

A CLI tool for the [Synapse admin
API](https://matrix-org.github.io/synapse/develop/usage/administration/admin_api/index.html#the-admin-api).

## Prerequisites

- Python 3.6+
- a running Synapse instance
- an admin-enabled user on the instance
- the admin user's access token

`synadm` is designed to run either directly on the host running the Synapse
instance or on a remote machine able to access Synapse's API port. Synapse's
default admin API endpoint address usually is
`http://localhost:8008/_synapse/admin` or
`https://localhost:8448/_synapse/admin`.

## Installation

To install synadm from PyPI, run the following command:

`pip3 install synadm`

## Configuration

### Getting an Admin Token

To get your account token in Element-Web: _Login as this user - "Click User
Avatar" - "All Settings" - "Help & About" - Scroll down - "Advanced" -
"Access Token"_

Or use synadm to get a token. Use the fully qualified Matrix ID of the admin
user:

```
synadm matrix login @admin_username:yourdomain.org
Password:
```

If you issue this command in a fresh `synadm` installation, [the
configurator](#the-configurator) will launch anyway.

- Answer the questions.
- Set token to "invalid" at first so `synadm` will run the `matrix login`
  command (otherwise you'd get a "Configuration incomplete" error).
- After successfully entering your admin password you will be presented a
  token which you can finally set by re-launching the configurator as
  described below.

### The configurator

`synadm` asks for necessary configuration items on first launch
automatically. Also whenever new mandatory configuration items where added
(eg after an update), the user will be prompted for missing items
automatically.

Configuration can be changed any time by launching the configurator
directly:

```
synadm config
```

Configuration will be saved in `~/.config/synadm.yaml`

## Usage

You can add `-h` or `--help` to the command to see the help for it:

```
synadm -h
```

and same for subcommands:

```
synadm version -h
synadm user -h
synadm room -h
```

By default, `synadm` will show some abbreviated help for the command. For
example:

```
synadm user
```
or
```
synadm user details
```

will show essential help for the particular subcommand right away.

*Note: A list of currently available commands is found in chapter
[implementation status / commands
list](#implementation-status--commands-list)* as well as in the following
chapter.

### Command Line Reference

A detailed [Command Line
Reference](https://synadm.readthedocs.io/en/latest/index_cli_reference.html)
can be found in `synadm`'s readthedocs documentation.

### Advanced Usage

Examples of how `synadm` can be used in shell scripts and oneliners is
provided in the [Scripting
Examples](https://synadm.readthedocs.io/en/latest/examples.html) docs
chapter.

## Update

For updating an installation done with PyPI:

```
pip3 install synadm --upgrade
```

## Implementation Status / Commands List

[Follow this link to the official Synapse Admin API
docs](https://matrix-org.github.io/synapse/develop/usage/administration/admin_api/index.html).
Direct links to the specific API documentation pages are provided in the
list below.

*Note: Most commands have several optional arguments available. Put -h after
any of the below listed commands to view them or have a look at the [Command
Line
Reference](https://synadm.readthedocs.io/en/latest/index_cli_reference.html).*

* [ ] [Account Validity](https://matrix-org.github.io/synapse/develop/admin_api/account_validity.html)
* [ ] [Event Reports](https://matrix-org.github.io/synapse/develop/admin_api/event_reports.html)
* [ ] [Register Users](https://matrix-org.github.io/synapse/develop/admin_api/register_api.html)
* [ ] [Statistics](https://matrix-org.github.io/synapse/develop/admin_api/statistics.html)
* [x] [Delete Group](https://matrix-org.github.io/synapse/develop/admin_api/delete_group.html) (delete community)
* [x] [Manipulate Room Membership](https://matrix-org.github.io/synapse/develop/admin_api/room_membership.html)
* [x] [Media Admin](https://matrix-org.github.io/synapse/develop/admin_api/media_admin_api.html)
* [x] [Purge History](https://matrix-org.github.io/synapse/develop/admin_api/purge_history_api.html)
* [x] [Registration Tokens](https://matrix-org.github.io/synapse/latest/usage/administration/admin_api/registration_tokens.html)
* [x] [Rooms](https://matrix-org.github.io/synapse/develop/admin_api/rooms.html)
* [x] [Server Notices](https://matrix-org.github.io/synapse/develop/admin_api/server_notices.html)
* [x] [Server Version](https://matrix-org.github.io/synapse/develop/admin_api/version_api.html)
* [x] [Users](https://matrix-org.github.io/synapse/develop/admin_api/user_admin_api.html)

## Support

If you need help with using synadm, have a feature idea or would like to
discuss anything else around `synadm`, get in touch via [our Matrix
room][mroom]!

We are hanging around in [the official support room for
Synapse](https://matrix.to/#/#synapse:matrix.org). Usually you'll find
`synadm` users there that might answer your questions already.

The most direct way to reach synadm maintainers as well as seasoned `synadm`
users and Synapse admins is by joining [#synadm:peek-a-boo.at][mroom].

[mroom]:https://matrix.to/#/#synadm:peek-a-boo.at

If you are sure you've found a bug that was not already reported, opening an
[issue on GitHub](https://github.com/JOJ0/synadm/issues) is a valid option
too. If unsure, ask in
[#synadm:peek-a-boo.at](https://matrix.to/#/#synadm:peek-a-boo.at) first.

## Contributing

First of all, thanks for your interest in contributing to `synadm`! We
appreciate any help, no matter if you are a programmer or a user. Both
groups can do valuable things for the `synadm` project. We love providing a
useful tool to fellow Synapse sysadmins but rely on contribution from the
Synapse and Matrix community to keep `synadm` useful, current and stable.

Please review the [contributing docs](CONTRIBUTING.md) for guidelines and
help around the topic!

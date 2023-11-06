<!-- omit in toc -->
# synadm - the Matrix-Synapse admin CLI

- [About](#about)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Getting an Admin Token](#getting-an-admin-token)
  - [The configurator](#the-configurator)
- [Usage](#usage)
  - [Command Line Reference](#command-line-reference)
  - [Advanced Usage](#advanced-usage)
- [Update](#update)
- [Support](#support)
- [Contributing](#contributing)

## About

A CLI tool for the [Synapse admin
API](https://matrix-org.github.io/synapse/develop/usage/administration/admin_api/index.html#the-admin-api).

## Prerequisites

- Python 3.6+
- a running Synapse instance
- an admin-enabled user on the instance
- the admin user's access token

`synadm` can run either on the Synapse host, or on a remote machine with
access to the Synapse Admin API.

## Installation

To install synadm from PyPI, run the following command:

`pip3 install synadm`

## Configuration

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

1. Answer the questions.
2. Set token to "invalid" at first so `synadm` will run the `matrix login`
   command (otherwise you'd get a "Configuration incomplete" error).
3. After successfully entering your admin password you will be presented a
   token which you can finally set by re-launching the configurator as
   described below.

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
appreciate any help, no matter if you are a programmer or a user.

Please review the [contributing docs](CONTRIBUTING.md) for guidelines and
help around the topic!

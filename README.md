<!-- omit in toc -->
# synadm - CLI frontend to Matrix-Synapse admin APIs

- [About](#about)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Update](#update)
- [Implementation status / commands list](#implementation-status--commands-list)
- [Get in touch / feedback / support](#get-in-touch--feedback--support)
- [Contribution](#contribution)
  - [How can I help?](#how-can-i-help)
  - [Install to virtual environment](#install-to-virtual-environment)
  - [Install in development mode](#install-in-development-mode)
  - [Implementation examples](#implementation-examples)
  - [More detailed implementation example](#more-detailed-implementation-example)




## About

A CLI tool to help admins of [Matrix-Synapse homeservers](https://github.com/matrix-org/synapse) conveniently issue commands available via its admin API's (https://github.com/matrix-org/synapse/tree/master/docs/admin_api)




## Prerequisites

- Python 3.6+
- a running Matrix-Synapse instance
- an admin-enabled user on the instance
- the admin user's access token

`synadm` is designed to run either directly on the host running the Synapse instance or on a remote machine able to access Synapse's API port. Synapse's default admin API endpoint address usually is http://localhost:8008/_synapse/admin or https://localhost:8448/_synapse/admin.




## Installation

The installation process is tested on an Ubuntu Bionic (18.04) machine but should work an any more or less *current* Linux machine:


<!-- omit in toc -->
### 1. Check Python version

`python3 --version` should show at least v3.6.x

<!-- omit in toc -->
### 2. Clone repo:

```
git clone https://github.com/joj0/synadm
```

<!-- omit in toc -->
### 3. Install package globally

This will install `synadm` and all dependent Python packages to your system's global Python site-packages directory:

```
cd synadm
sudo python3 setup.py install
```

<!-- omit in toc -->
### 4. Run

`synadm` should now run fine without having to add a path in front of it:

```
synadm -h
```

*Note: Usually setuptools installs a command wrapper to `/usr/local/bin/synadm`, but that depends on your system.*

*Note: In case you don't want `synadm` to be installed to a global system directory see chapter [install to virtual environment](#install-to-virtual-environment).*

*Note: synadm is mutli-user aware - it stores it's configuration inside the executing user's home directory. See chapter [configuration](#configuration).*



## Configuration

`synadm` asks for necessary configuration items on first launch automatically. Also whenever new configuration items where added (eg after an update), the user will be prompted for missing items automatically.

Configuration can be changed any time by launching the configurator directly:

```
synadm config
```

Configuration will be saved in `~/.config/synadm.yaml`

*Note: To find out your admin user's token in Element-Web: Login as this user - "Click User Avatar" - "All Settings" - "Help & About" - Scroll down - "Advanced" - "Access Token"*

*Note: Be aware that once you configured `synadm`, your admin user's token is saved in the configuration file. On Posix compatible systems permissions are set to mode 0600, on other OS's it is your responsibilty to change permissions accordingly.*

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

You even can spare the `-h` option, `synadm` will show help for the executed subcommand anyway. For example:

```
synadm user
```
or
```
synadm user detail
```

will show help for the particular subcommand right away. 

*Note: A complete list of currently available commands is found in in chapter [implementation status / commands list](#implementation-status--commands-list)*

## Update

To update `synadm` to the latest development state, just update your git repo and reinstall:

```
cd synadm
git pull
python3 setup.py install
```

*Note: If you installed to a Python venv, first load it as described in [install to virtual environment](#install-to-virtual-environment).*

*Note: If you installed in [development mode](#install-in-development-mode) you can spare the `python3 setup.py install` command - just `git pull` any you're done.*



## Implementation status / commands list

[Synapse Admin API docs main page](https://github.com/matrix-org/synapse/tree/master/docs/admin_api) - direct links to the specific API documentation pages are provided in the list below.

*Note: Most commands have several optional arguments available. Put -h after any of the below listed commands to view them.*

* [ ] [Account validity API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/account_validity.rst)
* [ ] [Delete group API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/delete_group.md)
* [ ] [Event reports API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/event_reports.md)
* [ ] [Media admin API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/media_admin_api.md)
  * [ ] `room media list <room id>`
  * [ ] `media quarantine <server name> <media id>`
  * [ ] `room media quarantine <room id>`
  * [ ] `user media quarantine <room id>`
  * [ ] `media delete <server name> <media id>`
* [ ] [Purge history API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/purge_history_api.rst)
  * [ ] `room history purge <room id>`
  * [ ] `room history purge_status <purge id>`
* [ ] [Purge remote media API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/purge_remote_media.rst)
* [x] ~~[Purge room API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/purge_room.md)~~ (covered by `room delete` already)
* [ ] [Register API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/register_api.rst)
* [ ] [Room membership API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/room_membership.md)
  * [ ] `room join`
* [ ] [Rooms API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/rooms.md)
  * [x] `room list`
  * [x] `room search <search-term>` (shortcut to `room list -n <search-term>`)
  * [x] `room details <room id>`
  * [x] `room members <room id>`
  * [x] `room delete <room id>`
  * [ ] `room count`
  * [ ] `room top-complexity`
  * [ ] `room top-members`
* [ ] [Server notices API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/server_notices.md)
* [x] ~~[Shutdown room API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/shutdown_room.md)~~ (covered by `room delete` already)
* [ ] [Statistics API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/statistics.md)
* [ ] [User admin API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/user_admin_api.rst)
  * [x] `user details <user id>`
  * [ ] `user query <user id>` (alias of `user details`)
  * [x] `user modify <user id>`
  * [ ] `user create <user id>` (alias of `user create`)
  * [x] `user list`
  * [x] `user deactivate <user id>`
  * [x] `user password <user id>`
  * [x] `user membership <user id>`
  * [x] `user search <search-term>` (shortcut to `user list -d -g -n <search-term>`)
* [x] [Version API](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/version_api.rst)
  * [x] `version`




## Get in touch / feedback / support

If you need help with installing, usage or contribution or have anything else on your mind, just join public matrix room #synadm:peek-a-boo.at and get in touch. I am also hanging around on #matrix-dev:matrix.org and #synapse:matrix.org regularily. Just ask for a jojo ;-)




## Contribution

### How can I help?

* Install `synadm` and report back whether or not the installation process worked on the OS you're running.
* Read the [Synapse admin API docs](https://github.com/matrix-org/synapse/tree/master/docs/admin_api), pick a feature, implement it and send a pull-request - see [implementation examples chapter](#implementation-examples), it really isn't hard, take a look!
* If you don't code, you can still help me prioritize what to code next: Pick a feature from the docs just mentioned, open a github issue in this repo and tell me what it is. Alternatively just catch me on #synadm:peek-a-boo.at or #matrix-dev:matrix.org.

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

Without much talk, have a look at this commit: https://github.com/JOJ0/synadm/commit/4978794751aaad23369988da66ccc8e87bc638c4#diff-a676a1667b53bcb8aad4097acb601e227a6b60a6168625e364d250ed47bf7619

It implements command `synadm room details <room_id>`. Pretty straight forward, right? Help me out and code such a little feature! Thanks! :-)

And another one, this time using a POST based API endpoint. It implements command `synadm user password <user_id>`: https://github.com/JOJ0/synadm/commit/274f6bf50ceaa175313aab25da4699ea745ee2ea#diff-a676a1667b53bcb8aad4097acb601e227a6b60a6168625e364d250ed47bf7619


### More detailed implementation example

A feature based on a GET request is quite easy to implement. It needs two things

- A method in the Synapse_admin class. Generation of the url as described in the above mentioned docs, and the actual execution of the GET request (using the Python *requests* module) happens here.
- A "decorated" function that creates the necessary command line arguments and options (using the Python *Click* module)

Let's have a look on a particular example. Take the following command:

```
synadm user list --deactivated --no-guests
```

- The method [user_list() in Synapse_admin class](https://github.com/JOJ0/synadm/blob/31e1b0f1dab4272452fe8772d683a1b420247e6e/synadm.py#L110-L120) has to be written first. It just builds a urlpart together to fit the need of the [user admin API docs](https://github.com/matrix-org/synapse/blob/master/docs/admin_api/user_admin_api.rst#list-accounts). It then passes the urlpart to the [_get() method](https://github.com/JOJ0/synadm/blob/31e1b0f1dab4272452fe8772d683a1b420247e6e/synadm.py#L54-L80) to execute the request. Most of network/http error handling happens here and you don't have to take care about it.
- The cli part works like this: [This method named "list" (plus it's @decorators)](https://github.com/JOJ0/synadm/blob/31e1b0f1dab4272452fe8772d683a1b420247e6e/synadm.py#L390-L411) is all the magic behind the `... list --deactivated --no-guests` part of the command. If you take a closer look at [this decorator](https://github.com/JOJ0/synadm/blob/31e1b0f1dab4272452fe8772d683a1b420247e6e/synadm.py#L374) you see that it is a "subelement" of the click.group "user". The ["user-group" is defined here](https://github.com/JOJ0/synadm/blob/31e1b0f1dab4272452fe8772d683a1b420247e6e/synadm.py#L365-L370) .... and is responsible to make the `synadm user ...` part of the command happen.

So to further clarify things: *Click* works with *command groups* and *commands*. At the time of writing this tutorial synadm consists of the following:

main *group* **synadm** -> *subgroups* **user** and **room** -> each of those *subgroups* contains a *command* named **list**
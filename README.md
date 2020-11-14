<!-- omit in toc -->
# synadm - a CLI frontend to the Synapse admin API's

- [About](#about)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Install systemwide](#install-systemwide)
  - [Install to virtual environment](#install-to-virtual-environment)
- [Configuration](#configuration)
- [Usage](#usage)
- [Update](#update)
- [Contribution](#contribution)
    - [Install in development mode](#install-in-development-mode)
    - [How can I help?](#how-can-i-help)
    - [Example of implementing a feature](#example-of-implementing-a-feature)
    - [Further implementation examples](#further-implementation-examples)
    - [Get in touch / feedback / support](#get-in-touch--feedback--support)
- [Implementation status](#implementation-status)

## About

A CLI tool to help admins of Matrix-Synapse homeservers conveniently issue commands available via its admin API's (https://github.com/matrix-org/synapse/tree/master/docs/admin_api)

## Prerequisites

- Python 3.6+
- a running Matrix-Synapse instance
- an admin-enabled user on the instance
- the admin user's access token

Synadm is designed to run either directly on the host running the Synapse instance or on a machine able to access Synapse's API port (usually 8008) on a remote network interface (not recommended). So usually the API endpoint address is http://localhost:8008 and this also is synadm's default configuration.

## Installation

The installation process is tested on an Ubuntu Bionic (18.04) machine but should work an any more or less *current* Linux machine:

### Install systemwide


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

This will install synadm and all dependent Python packages to your system's global Python site-packages directory:

```
cd synadm
sudo python3 setup.py install
```

<!-- omit in toc -->
#### 4. Run

synadm should run fine without having to add a path in front of it

```
synadm --help
```

### Install to virtual environment

<!-- omit in toc -->
#### 3. Setup and load a new Python3 virtual environment]

If you'd rather prefer to install synadm into its own private virtual Python environment or even would like to help code it, this is a much cleaner approach.

Assuming you did steps 1 and 2 as described above, create and activate a virtual environment using the python3 venv module:

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

*Note: Don't forget to activate the venv when coming back to using synadm after a fresh login: `source ~/.venvs/synadm/bin/activate`*

<!-- omit in toc -->
#### 5. Run

As long as your venv is loaded synadm should run fine without having to add a path in front of it

```
synadm --help
```

## Configuration

Execute the configuration command - you will be prompted for host, port, user, token and weather your API port is en SSL endpoint or not:

```
synadm config
```

Configuration will be saved in `~/.config/synadm.yaml`

*Note: To find out your admin user's token in Element-Web: Login as this user - "Click User Avatar" - "All Settings" - "Help & About" - Scroll down - "Advanced" - "Access Token"*

## Usage

Use the online help of the main command:

```
synadm --help
```

and of the available subcommands, eg.

```
synadm version --help
synadm user --help
synadm room --help
```

## Update

To update synadm to the latest development state, just update your git repo:

```
cd synadm
git pull
python3 setup.py install
```

*Note: If you installed to a Python venv, first load it as described above.*
*Note: If you installed in development mode you can spare the `python3 setup.py install` command - just `git pull` any you're done.*

## Contribution

#### Install in development mode

If you'd like to contribute to synadm's development, it's recommended to use a venv as described above, and also use a slightly different installation command:

```
cd synadm
python3 setup.py develop
```

*Note: When installed like this, code-changes inside the repo dir will immediately be available when executing `synadm`. This could also be used as a quick way to just stay on top of synadm's development.*


#### How can I help?

* Install synadm and report back weather the installation process worked on the OS you're running.
* Read the [docs about the Synapse admin API's possibilities](https://github.com/matrix-org/synapse/tree/master/docs/admin_api), pick a feature, implement it and send a pull-request.
* If you really have no idea of coding at all, you can still help me prioritize what to code next: Pick a feature from the docs just mentioned, open a github issue in this repo and tell me what it is.

Thanks in advance for any help! I can't do this without you!

#### Example of implementing a feature

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

#### Further implementation examples

Without much talk, have a look at this commit: https://github.com/JOJ0/synadm/commit/4978794751aaad23369988da66ccc8e87bc638c4#diff-a676a1667b53bcb8aad4097acb601e227a6b60a6168625e364d250ed47bf7619

It implements command `synadm room details <room_id>`. Pretty straight forward, right? Help me out and code such a little feature! Thanks! :-)

And another one, this time using a POST based API endpoint. It implements command `synadm user password <user_id>`: https://github.com/JOJ0/synadm/commit/274f6bf50ceaa175313aab25da4699ea745ee2ea#diff-a676a1667b53bcb8aad4097acb601e227a6b60a6168625e364d250ed47bf7619


#### Get in touch / feedback / support

If you have anything on your mind and think a github issue or pull-request is not the right way, just join public matrix room #synadm:peek-a-boo.at and let's talk about it. I am also hanging around on #matrix-dev:matrix.org and #synapse:mastrix.org regularily. Catch me there! My matrix ID is jojo:peek-a-boo.at

## Implementation status

(https://github.com/matrix-org/synapse/tree/master/docs/admin_api)

*Note: Most commands have several optional arguments available. Try putting --help after the commands below to get to know them*

* [ ] account_validity
* [ ] delete_group
* [ ] media_admin_api
* [ ] purge_history_api
* [ ] purge_remote_media
* ~~[x] purge_room~~
  * [x] ~~`room purge <room id>`~~ (covered by `room delete` already)
  * [ ] `room garbage-collect`
* [ ] register_api
* [ ] room_membership
* [ ] rooms
  * [ ] `room count`
  * [x] `room delete <room id>`
  * [x] `room details <room id>`
  * [x] `room list`
  * [x] `room members`
  * [ ] `room top-complexity`
  * [ ] `room top-members`
  * [x] `room search <search-term>` (shortcut to `room list -n <search-term>`)
* [ ] server_notices
* ~~[x] shutdown_room~~
  * [x] ~~`room shutdown <room id>`~~ (covered by `room delete` already)
* [ ] user_admin_api
  * [x] `user list`
  * [ ] `user query <user id>`
  * [x] `user deactivate <user id>`
  * [x] `user password <user id>`
  * [x] `user membership <user id>` 
  * [x] `user search <search-term>` (shortcut to `user list -n <search-term>`)
* [x] version_api
  * [x] `version`
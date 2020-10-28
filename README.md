# synadm - a CLI frontend to the Synapse admin API's

- [synadm - a CLI frontend to the Synapse admin API's](#synadm---a-cli-frontend-to-the-synapse-admin-apis)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Install systemwide](#install-systemwide)
    - [Install to virtual environment](#install-to-virtual-environment)
  - [Configuration](#configuration)
  - [Usage](#usage)
  - [Update](#update)
  - [Contribution](#contribution)
      - [Install in development mode](#install-in-development-mode)

## Prerequisites

- Python 3.6+
- a running Matrix-Synapse instance
- an admin-enabled user on the instance
- the admin user's access token

Synadm is designed to run either directly on the host running the Synapse instance or is able to access Synapse's API port (usually 8008) on a remote network interface (not recommended). So usually the API endpoint address is http://localhost:8008 and this also is synadm's default configuration. 

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

If you'd rather prefer to install synadm into its own private virtual Python environment or even would like to help code it, this is a cleaner approach:

<!-- omit in toc -->
#### 1. Set up and load a new Python3 virtual environment

```
python -m ~/.venvs/synadm
source ~/.venvs/synadm/bin/activate
```

Once your Python virtual environment is loaded and your prompt looks similar to `(synadm) ....  $ `, install directly into the environment:


<!-- omit in toc -->
#### 2. Install

```
cd synadm
python3 setup.py install
```

*Note: Don't forget to activate the venv when coming back to using synadm after a fresh login: `source ~/.venvs/synadm/bin/activate`*

<!-- omit in toc -->
#### 4. Run

As long as your venv is loaded synadm should run fine without having to add a path in front of it

```
synadm --help
```

## Configuration

Execute the configuration command - you will be prompted for host, port, user and token:

```
synadm config
```

Configuration will be saved in a yaml file called `~/.synadm`

## Usage

Use the online help of the main command:

```
synadm --help
```

and of the available subcommands, eg.

```
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

*Note: When installed like this, code changes inside the repo dir will immediately be available when executing `synadm`. This could also be used as a quick way to just stay on top of synadm's development.*

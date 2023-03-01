<!-- omit in toc -->
# Contributing

- [Types of Contribution](#types-of-contribution)
  - [Non-Programming](#non-programming)
  - [Programming](#programming)
- [Submitting Your Work](#submitting-your-work)
- [Expectations Regarding Timelines](#expectations-regarding-timelines)
- [Discuss \& Design First](#discuss--design-first)
- [Getting the Source \& Installing](#getting-the-source--installing)
  - [Install into a Virtual Python Environment](#install-into-a-virtual-python-environment)
  - [Install in Editable Mode](#install-in-editable-mode)
- [Command Design](#command-design)
  - [Implementation Examples](#implementation-examples)
  - [Helpers \& Utilities](#helpers--utilities)
  - [Logging](#logging)
  - [Code Documentation](#code-documentation)
  - [Code Style](#code-style)
- [Maintainers Notes](#maintainers-notes)
- [Maintainership](#maintainership)


## Types of Contribution

No matter if you're a programmer or not there are many ways to contribute to the `synadm` project.

### Non-Programming

* [Set up synadm](README.md#installation) and report whether the installation, configuration and update processes work as described or could be improved. We don't have the resources to test on many operating systems, thus a quick GitHub issue telling us: "It even works on Fancy-OS" would help already.
* Help keeping the [Implementation Status / Commands List](README.md#implementation-status--commands-list) chapter up to date. The Synapse project is steadily releasing new features for the _Synapse Admin API_. We can't keep up with updating this list but still think it is a handy overview of what's supported and what isn't.
* Help prioritizing what to code next: Pick a feature from the list you find in the [Implementation Status / Commands List](README.md#implementation-status--commands-list) chapter, open a GitHub issue and tell us what it is. If you don't find the feature in the list, please add it!
* Improve the docs: The end-user documentation is almost entirely realised with the typical online help of unix commands, an option named`--help/-h`. We believe that a top-priority in designing CLI tools is getting this information right. Spelling, wording and of course technical correctness are equally important. If it's not easily possible to stay brief and technically precise at the same time, we believe it is ok to prioritize precision over shortness. We have automated rendering `--help` to HTML with the _Sphinx documentation generator_, [which can be found here](https://synadm.readthedocs.io/en/latest/index_cli_reference.html).

### Programming

* Pick an open issue on GitHub or an unticked feature from the [Implementation Status / Commands List](README.md#implementation-status--commands-list) chapter, start implementing and submit a pull-request when you are ready to receive our feedback.
  * If you'd like to receive "early feedback" even though you think your code is not ready yet, submit your PR already and set it to draft state. Ping us using @mention.
  * It's ok to open a Draft PR even if you don't want our feedback yet but it helps you in any way. We won't bother you until you ping us.
* Read the [Synapse Admin API docs](https://github.com/matrix-org/synapse/tree/master/docs/admin_api), pick a feature, implement it and send a pull-request. Don't forget to check if the feature is listed in the [Implementation Status / Commands List](README.md#implementation-status--commands-list) chapter already. if not, please include the addition to the list in your PR (separate commit if possible).


## Submitting Your Work

Several ways to submit FIXME

- PR
- Inline edit

## Expectations Regarding Timelines

Spare time but dedicated.

- PR time to review estimate
- PR considered abandoned estimate, friendly reminder, taking over.
- Releaseing, as often as possible, please ask if not happening.


## Discuss & Design First

It proved to be useful in the past if loose (feature) ideas would be discussed in #synadm:peek-a-boo.at first, which helps forming a more concrete idea that can than further be summarized into a well written github issue.

 and finally be implemented by a `synadm` contributor or a `synadm` maintainer.


## Getting the Source & Installing

### Install into a Virtual Python Environment

To install `synadm` into its own private virtual Python environment, FIXME

<!-- omit in toc -->
#### 1. Check Python Version

`python3 --version` should show at least v3.6.x

<!-- omit in toc -->
#### 2. Clone Repo:

```
git clone https://github.com/joj0/synadm
```

<!-- omit in toc -->
#### 3. Set up a Python3 Virtual Environment


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
pip install .
```

*Note: Don't forget to activate the venv when coming back to using `synadm` after a fresh login: `source ~/.venvs/synadm/bin/activate`*

<!-- omit in toc -->
#### 5. Run

As long as your venv is loaded `synadm` should run fine without having to add a path in front of it

```
synadm -h
```


### Install in Editable Mode

To be able to instantly be able to test the code you've been working on it makes sense to install from your git clone in _editable mode_

```
cd synadm
pip install -e .
```

*Note: When installed like this, code-changes inside the repo dir will immediately be available when executing `synadm`. This could also be used as a quick way to just stay on top of synadm's development.*

## Command Design

The general design of a synadm subcommand is simple. You would usually have:

- A method in the _backend module_, which is located in the file [synadm/api.py](https://github.com/JOJ0/synadm/blob/master/synadm/api.py).
- A definition of the CLI frontend. We are using Click as the underlying framework. It's easy to learn and usually rather self-explanatory. Just copy and paste an existing command and work from there.
- 
_Note: If you are not familiar with Python code, don't let yourself get distracted with the unusual @statements that define argumentes and options. They are so called decorators that "plug in" those options into your commands function. You don't need to understand why this concept of decorators is used by the Click library._

### Implementation Examples

Have a look at this method: https://github.com/JOJ0/synadm/blob/107d34b38de71d6d21d78141e78a1b19d3dd5379/synadm/cli/user.py#L185

and this one: https://github.com/JOJ0/synadm/blob/107d34b38de71d6d21d78141e78a1b19d3dd5379/synadm/api.py#L80

That's all it needs to implement command `synadm user details <user_id>`.

And another example, this time using a POST based API endpoint. It implements command `synadm user password <user_id>`. This is the CLI-level method: https://github.com/JOJ0/synadm/blob/0af918fdeee40bc1d3df7b734a46e76bb31148b9/synadm/cli/user.py#L114

and again it needs a backend method in api.py:
https://github.com/JOJ0/synadm/blob/107d34b38de71d6d21d78141e78a1b19d3dd5379/synadm/api.py#L72

### Helpers & Utilities

You'll find a couple of helpers & utilities [near the top of the api module's code](https://github.com/JOJ0/synadm/blob/master/synadm/api.py#L125), right below the `query()` method. For example we already provide methods to translate unix timestamps to human readable formats and vice versa. 

If you need to to defer code to a helper function because you require reusing it or otherwise think it's a cleaner approach put it where you need it: Either as a subfunction in your backend method in the `synadm/api` module or in the frontend function in `synadm/cmd/yourcommand`. If you think you've wrote a function that is very generic and might be useful to other `synadm/api` methods as well, put it next to _.

### Logging

Simply use `self.log.warn()` (or `.error/.debug/.info`) within the `synadm/api` module.

From a command's frontend code in the `synadm/cmd` package, logging is available via the `helper` object that usually should be passed to subcommand function: `helper.log.warn()`.

### Code Documentation

We provide an auto-generated [developer's documentation](https://synadm.readthedocs.io/en/latest/index_modules.html) generated with the help of the Sphinx library. This requires that code is documented by developers by a certain format in the docstrings of functions, classes and methods.

We use the google docstring format to achieve because we believe it provides the best human-readability when compared to other docstring formats that Sphinx supports for auto-generating package documentation.

FIXME link to google docstring docs.


### Code Style

We try to follow Python's PEP8 guidlines as good as possible. We have an
automatic linter in place in our Github Actions CI workflow. You can use flake8 before submitting on CLI. FIXME

Summary of style-related things we consider most helpful:

- Line length 79
- Pythonic
- Stay approachable to Python beginners?

Suggesting changes via gh feature or we ask for permission to push to submitters feature branch.


## Maintainers Notes

This section is a checklist for maintainers of the `synadm` project. Still there might be helpful information applying to contributors as well, thus we made it public.

- dev branch shared usage
- PR "owner"
- release helper scripts
- documentation version activation


## Maintainership

If you feel like you would like to support the `synadm` project on a regular basis, consider applying for maintainership. We  believe in Open Source software and think no matter if you are a programmer or not, there is plenty of room for improvement. Contact either via #synadm:peek-a-boo.at or private message to @jojo:....
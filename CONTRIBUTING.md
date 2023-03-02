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
  - [Release process](#release-process)
- [Maintainership](#maintainership)


## Types of Contribution

No matter if you're a programmer or not there are many ways to contribute to the `synadm` project.

### Non-Programming

* [Set up synadm](README.md#installation) and report whether the installation, configuration and update processes work as described or could be improved. We don't have the resources to test on many operating systems, thus a quick GitHub issue telling us: "It even works on Fancy-OS" would help already.
* Help keeping the [Implementation Status / Commands List](README.md#implementation-status--commands-list) chapter up to date. The Synapse project is steadily releasing new features for the _Synapse Admin API_. We can't keep up with updating this list but still think it is a handy overview of what's supported and what isn't.
* Help prioritizing what to code next: Pick a feature from the list you find in the [Implementation Status / Commands List](README.md#implementation-status--commands-list) chapter, open a GitHub issue and tell us what it is. If you don't find the feature in the list, please add it!
* Improve the docs: The end-user documentation is entirely realised with the typical online help of unix commands, an option named`--help/-h`. We believe that a top-priority in designing CLI tools is getting this information right. Spelling, wording and of course technical correctness are equally important. If it's not easily possible to stay brief and technically precise at the same time, we believe it is ok to prioritize precision over shortness. We have automated rendering `--help` to HTML with the _Sphinx documentation generator_, [which can be found here](https://synadm.readthedocs.io/en/latest/index_cli_reference.html).

### Programming

* Pick an open issue on GitHub or an unticked feature from the [Implementation Status / Commands List](README.md#implementation-status--commands-list) chapter, start implementing and submit a pull-request when you are ready to receive our feedback.
  * If you'd like to receive "early feedback" even though you think your code is not ready yet, submit your PR already and set it to draft state. Ping us using @mention.
  * It's ok to open a Draft PR even if you don't want our feedback yet but it helps you in any way. We won't bother you until you ping us.
* Read the [Synapse Admin API docs](https://github.com/matrix-org/synapse/tree/master/docs/admin_api), pick a feature, implement it and send a pull-request. Don't forget to check if the feature is listed in the [Implementation Status / Commands List](README.md#implementation-status--commands-list) chapter already. if not, please include the addition to the list in your PR (separate commit if possible).


## Submitting Your Work

There are several ways to submit your work.

- Clone the repo, create a feature branch and submit a pull-request.
  - Consider enabling the [Allow edits from maintainers](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork) option. We will deal with this permission responsibly. It proved to be a useful option for working together in the past and might even speed up getting a PR merged.
- If you're not familiar with using git or just want to submit a smaller change (like a correction to the docs), use the “Edit file” button in the upper-right while viewing a file directly on the GitHub web interface. You can automatically send us a pull request for your changes.
- Next to the "Edit file" button you'll find another option called "Open with github.dev" which opens a "Visual Studio Code" editor within your browser.


## Expectations Regarding Timelines

We are maintaining `synadm` in our spare time and currently are not sponsored by a company to do that. Nevertheless we try to be responsive to contributors and try to release new features as soon as they are merged.

- We try to give a first review to your submitted pull-requests **within a week**, often you'll get an answer much faster though.
- We don't expect you to finish the PR / submit the changes we suggested "in time" but would like to ask you to **communicate your personal timeline**.
- Usually it's not critical for a feature to be finished within a time frame. If you inform us that you will be able to finish your work within a month, but not right now, it's fine, **please just let us know**!
- If it's a serious bug we might ask you for permission to take over your branch and continue the work ourselves.
- Unfortunately we often see contributors submitting PR's, correcting a few of our suggested changes but then dissapear. Please don't do that! If you realise you won't find the time at all to continue your work, **please just let us know**. It's perfectly fine and there won't be hard feelings. If we consider your feature useful we might even take over and finish it ourselves.
- We try to release merged features as soon as possible. Even the tiniest feature deserves a release. Sometimes we just can't make it soon enough because we don't find the time or we wait for something else because it makes sense to be released together. If a feature you submitted is merged and you'd need it urgently to be available on PyPi, **please kindly remind us** and we'll try to find the time.


## Discuss & Design First

It proved to be useful in the past if loose (feature) ideas would be discussed in #synadm:peek-a-boo.at first, which helps forming a more concrete idea that can than further be summarized into a well written github issue and finally be implemented by a `synadm` contributor or a `synadm` maintainer.

- If you'd like someone else to pick up your feature idea because you are not able to code it yourself, open a detailed GitHub issue describing the feature.
- If you'd like to code it yourself, a separate issus is not required, just describe your feature within the PR.


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
- A definition of the CLI frontend. The Python package [Click](https://click.palletsprojects.com) is the command-line library in use. It's easy to learn and usually rather self-explanatory. Just copy and paste an existing command and work from there. The frontend code is found in the directory [synadm/cli](https://github.com/JOJ0/synadm/blob/master/synadm/cli/)

_Note: If you are not familiar with Python code, don't let yourself get distracted with the unusual @statements that define argumentes and options. They are so called decorators that "plug in" those options into your commands function. You don't actually need to understand why this concept of decorators is used by the Click library._


### Implementation Examples

Have a look at this method: https://github.com/JOJ0/synadm/blob/107d34b38de71d6d21d78141e78a1b19d3dd5379/synadm/cli/user.py#L185

and this one: https://github.com/JOJ0/synadm/blob/107d34b38de71d6d21d78141e78a1b19d3dd5379/synadm/api.py#L80

That's all it needs to implement command `synadm user details <user_id>`.

And another example, this time using a POST based API endpoint. It implements command `synadm user password <user_id>`. This is the CLI-level method: https://github.com/JOJ0/synadm/blob/0af918fdeee40bc1d3df7b734a46e76bb31148b9/synadm/cli/user.py#L114

and again it needs a backend method in `api.py`:
https://github.com/JOJ0/synadm/blob/107d34b38de71d6d21d78141e78a1b19d3dd5379/synadm/api.py#L72


### Helpers & Utilities

You'll find a couple of helpers & utilities [near the top of the api module's code](https://github.com/JOJ0/synadm/blob/master/synadm/api.py#L125), right below the `query()` method, within the `ApiRequest` class. For example we already provide methods to translate unix timestamps to human readable formats and vice versa.

If you need to defer code to a helper function because you require reusing it or otherwise think it's a cleaner approach, put it where you need it: Either as a subfunction in your backend method in the `synadm/api` module or in the frontend function in `synadm/cli/yourcommand`. If you think you've wrote a function that is very generic and might be useful to other `synadm/api` methods as well, put it next to the helpers in the `ApiRequest` class and tell us about it in a PR-comment.

### Logging

Simply use `self.log.warn()` (or `.error/.debug/.info`) within the `synadm/api` module.

From a command's frontend code in the `synadm/cmd` package, logging is available via the `helper` object that is available to every subcommand function, for example use `helper.log.warn()`.

### Code Documentation

We provide an auto-generated [Python package documentation](https://synadm.readthedocs.io/en/latest/index_modules.html) generated with the help of the _autodoc_ feature of the _Sphinx documentation generator_. This requires that code is documented through properly formatted docstrings of functions, classes and methods.

We use the [google docstring format](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

_Not all parts of `synadm` are populated with such docstrings yet but we require it for newly written code._

### Code Style

We try to follow Python's [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines as good as possible. We have an
automatic linter in place in our CI pipeline which runs whenever code is pushed to a branch. You'll notice a check going green or red at the very bottom when viewing your open PR. The check is called "Lint with flake8". If after a `git push` you notice the check gone red, click on it and you'll see details of what the linter detected you should correct.

`flake8` can be used directly on your code as well. Install it to your dev-environment:

```
pip install flake8
```

Run with:

`flake8 the_file_being_worked_on.py`

or leave out the filename to run it on all files and subdirectories.

Some more style and coding requirements:

- Pythonism: `synadm` is a Python project and as such tries to use some of the very handy features of the language. Some  of those might not be familiar to you since often we realise that contributors are professional programmers used to other languages or even are admins who are rather at home on the shell than in Python code. That is certainly all fine and we are trying to support you with refactoring your code to become more pythonic.
- That said, we would still like `synadm` to stay approachable to Python beginners and would encourage contributors to try not to overcomplicate things.
- We require a line length of 79 characters in Python code.
  - Some editors have handy commands to quickly reformat multi-line text (e.g help texts of options). For example in `vim`, lines can be marked using `shift+V` and then reformatted by typing `gq`
  - For code passages, staying within this boundary and at the same time keeping code well readable, this can be achieved using PEP8's many [line continuation suggestions](https://peps.python.org/pep-0008/#code-lay-out).
- We don't require a maximum line length in Markdown files, for example _this document_ or `README.md`. Please omit line-breaks in sentences, paragraphs, and so on, when editing these docs.
- If you'd like to tidy up your commits or reduce commit count we welcome the use of `git commit --amend` and `git rebase`. If you'd like us to test your code or work together within your feature branch, be aware of that force pushing might complicate things and should rather be omitted in that case.


## Maintainers Notes

This section is a checklist for maintainers of the `synadm` project. Still there might be helpful information applying to contributors as well, thus we made it public.

- We keep a branch named `dev` consistently existing that may be used for random things. If this branch is in use because a PR was openend from it, it's occupied and can't be used by others.
- Speaking of branches, we are not required to create branches in our own forks, we can just create them directly within the `synadm` repo. Checking out branches for e.g testing a feature in development is much easier than cloning and checking out from another maintainers fork.
- One person should be the "owner" of PR's openend by contributors and should request assitance by other maintainers if required. The ultimate decision to merge should be with the "PR owner". Who the owner is can be arrangend in the _synadm maintainers chatroom_ but usually would be the person who initially reviews the submission.


### Release process

Releasing a new version of `synadm` requires the following steps:

- Increase the version in all required files using the `bump.sh` script. `pip install bump2version` to your dev-environment to install the required tool. The final step to push to the master branch will be suggested by the script ('git push --follow-tags`).
- Following this push command the _release CI pipeline_ will be triggered and a tag and release draft be created on GitHub.
- Edit the generated draft and add release notes with the help of the "Generate release notes" button, but reformat into sections to be consistent with prior releases. If things were added without a PR, add those manually to the list of new features or fixes.
- Once the release notes are fine, make them public. The package can now be pushed to PyPi using the script `pypi.sh`
- Activate a new documentation version via [https://readthedocs.org/projects/synadm/versions/](https://readthedocs.org/projects/synadm/versions/), thus we provide a version of the online documentation consistent with the content of to the newly released `synadm` package.
- Spread the news in #synadm.peek-a-boo.at.


## Maintainership

If you feel like supporting the `synadm` project on a regular basis, consider applying for maintainership. We believe in Open Source software and think no matter if you are a programmer or not, there is plenty of things to do and still a lot of room for improvement. Contact either via #synadm:peek-a-boo.at or private message to @jojo:peek-a-boo.at.

<!-- omit in toc -->
# Contributing

- [Types of Contribution](#types-of-contribution)
  - [Non-Programming](#non-programming)
  - [Programming](#programming)
- [Submitting Your Work](#submitting-your-work)
- [Expectations Regarding Timelines](#expectations-regarding-timelines)
- [Feature Coverage Documentation](#feature-coverage-documentation)
- [Discuss \& Design First](#discuss--design-first)
- [Getting the Source \& Installing](#getting-the-source-installing)
- [Command Design](#command-design)
  - [Implementation Examples](#implementation-examples)
  - [Sending requests \& URL encoding](#sending-requests-url-encoding)
  - [Helpers \& Utilities](#helpers-utilities)
  - [Logging](#logging)
  - [Code Documentation](#code-documentation)
  - [Code Style](#code-style)
- [Maintainers Notes](#maintainers-notes)
  - [Release process](#release-process)
- [Maintainership](#maintainership)


## Types of Contribution

No matter if you're a programmer or not there are many ways to contribute to the `synadm` project.

### Non-Programming

* [Set up synadm](https://github.com/JOJ0/synadm/blob/master/README.md#installation) and report whether the installation, configuration and update processes work as described or could be improved. We don't have the resources to test on many operating systems, but you can [let us know](https://matrix.to/#/%23synadm%3Apeek-a-boo.at?via=jacksonchen666.com&via=maclemon.at&via=matrix.org&via=raim.ist) if it does work.
* Help keep the features list on [API to CLI Mapping](https://synadm.readthedocs.io/en/latest/features.html) up to date.
* Improve the docs: The end-user documentation is entirely realized with the typical online help of Unix commands, an option named`--help/-h`. We believe that a top-priority in designing CLI tools is getting this information right. Spelling, wording and of course technical correctness are equally important. If it's not easily possible to stay brief and technically precise at the same time, we believe it is OK to prioritize precision over shortness. We also have documentation made with _Sphinx_ [available online](https://synadm.readthedocs.io/en/latest/index_cli_reference.html).


### Programming

* Pick an [open issue on GitHub](https://github.com/JOJ0/synadm/issues) or a not yet implemented [Synapse Admin API](https://synadm.readthedocs.io/en/latest/features.html) (see [API to CLI Mapping](https://synadm.readthedocs.io/en/latest/features.html)) and start implementing it, then submit a pull-request when you are ready.
  * If you'd like to receive "early feedback" even though you think your code is not ready yet, submit your PR already and set it to draft state. You can then mention us (`@` then followed by a GitHub username).
  * It's ok to open a Draft PR even if you don't want our feedback yet but it helps you in any way. We won't bother you until you ping us.
* Don't forget to check if the feature you are submitting is listed on [API to CLI Mapping](https://synadm.readthedocs.io/en/latest/features.html) already. If not, please add it to the corresponding table (preferably in a separate commit).


## Submitting Your Work

There are several ways to submit your work.

- Clone the repo, create a feature branch and submit a pull-request.
  - Consider having the [Allow edits from maintainers](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork) option enabled. We will deal with this permission responsibly. It proved to be a useful option for working together in the past and might even speed up getting a PR merged.
- If you're not familiar with using git or just want to submit a smaller change (like a correction to the docs), you can use the “Edit file” button in the upper-right while viewing a file directly on the GitHub web interface.


## Expectations Regarding Timelines

We are maintaining `synadm` in our spare time and currently are not sponsored by a company to do that. Nevertheless we try to be responsive to contributors and try to release new features as soon as they are merged.

- As a rough estimate, we try to give a first response to your submitted pull-request **within a week**. There may be circumstances where this is not possible for us.
- The time required to respond with an actual code review depends on the size and complexity of the submission. We try to **communicate our own schedule and keep you informed**.
- We don't expect you to submit the changes we suggested "in time" but would like to ask you to **communicate when you have time to continue your work**.
- Usually it's not critical for a feature to be finished within a time frame. If you inform us that you will be able to finish your work within a month, but not right now, it's fine, **please just let us know**!
- If it's a serious bug we might ask you for permission to take over your branch and continue the work ourselves.
- Unfortunately we often see contributors submitting PR's, correcting a few of our suggested changes but then disappear, so if you realize you won't find the time at all to continue your work, **please just let us know**.
- We believe that even the tiniest feature deserves a timely release. Sometimes we just can't make it soon enough because we don't find the time or we wait for something else because it makes sense to be released together. If a feature you submitted is merged and you'd need it urgently to be available on PyPi, **please let us know**.

## Feature Coverage Documentation

We keep track of which Synapse Admin API's `synadm` supports in a set of tables on [API to CLI Mapping](https://synadm.readthedocs.io/en/latest/features.html). The structure of this page follows the layout of the official [Synapse Admin API documentation](https://element-hq.github.io/synapse/latest/usage/administration/admin_api/index.html). Each table represents one main chapter of the Synapse documentation.

In our documentation source, the page is defined by [features.rst](https://github.com/JOJ0/synadm/blob/master/doc/source/features.rst), which contains multiple CSV files, each representing a table. To assist with maintaining this page, we offer a [web scraper tool](https://github.com/JOJ0/synadm/blob/master/scrape_docs.py) that pulls data from the Synapse Admin API docs and creates an initial version of such a CSV table. To get started with using the tool, first run this command in the repository:

```
pip install -e '.[scrape_docs]'
```

A basic usage example is:

```
./scrape_docs.py -o csv https://element-hq.github.io/synapse/latest/admin_api/rooms.html
```

which prints a two-column CSV table containing restructuredText formatted hyperlinks in the left column. A corresponding `synadm` command is supposed to be added to the right hand side column manually. For example, you could add the following:

```
:option:`synadm user details USER_ID`
```

This would directly link to the `USER_ID` argument's documentation of that command.

Linking to an option is also possible:

```
:option:`synadm media list -r`
```

If there's no `synadm` command for the corresponding item, leave the right
column empty. If the item is a section has no real API and is nested with
commands (e.g. [delete local media][dellocalmedia]), use the `—` character.

[dellocalmedia]:https://element-hq.github.io/synapse/latest/admin_api/media_admin_api.html#delete-local-media


Due to a shortcoming of Sphinx it is currently not possible to link to a plain command (without any option or argument). Also see `scrape_docs.py --help` and the [existing CSV files](https://github.com/JOJ0/synadm/tree/master/doc/source/features).


## Discuss & Design First

It proved to be useful in the past if loose (feature) ideas would be discussed in [#synadm:peek-a-boo.at](https://matrix.to/#/%23synadm%3Apeek-a-boo.at?via=jacksonchen666.com&via=maclemon.at&via=matrix.org&via=raim.ist) first. Collecting opinions from fellow `synadm` users might help defining a more concrete idea.

- If you'd like **someone else** to pick up your feature idea because you are not able to code it yourself, please **open a detailed GitHub issue** describing the feature.
- **A separate issue is not required**, if you'd like to code it **yourself**. Please include the feature description in your PR.


## Getting the Source & Installing

To install `synadm` into its own private virtual Python environment follow these steps:

<!-- omit in toc -->
### 1. Check Python Version

`python3 --version` should show at least v3.6.x

<!-- omit in toc -->
### 2. Clone Repo:

```
git clone https://github.com/joj0/synadm
```

<!-- omit in toc -->
### 3. Set up a Python3 Virtual Environment


Create and activate a virtual environment using the python3 venv module:

```
python3 -m venv ~/.venvs/synadm
source ~/.venvs/synadm/bin/activate
```

*Note: Some people prefer to host a virtual environment directory named `venv` within the project repo. In that case do `cd synadm; python3 -m venv venv`*


Once your Python virtual environment is loaded and your prompt looks similar to `(synadm) ....  $ `, install directly into the environment:


<!-- omit in toc -->
### 4. Install in "Editable Mode" for development

Execute the install command from the root of the repo directory:

```
cd synadm
pip install -e .
```

*Note: When installed like this, code-changes inside the repo directory will immediately be available when executing `synadm`.*


<!-- omit in toc -->
### 5. Run

As long as your venv is loaded, `synadm` should run fine without having to add a path in front of it.

```
synadm -h
```




## Command Design

The general design of a synadm subcommand is simple. You would usually have:

- A method in the _backend module_, which is located in the file [synadm/api.py](https://github.com/JOJ0/synadm/blob/master/synadm/api.py).
- A definition of the CLI frontend. The Python package [Click](https://click.palletsprojects.com) is the command-line library in use. It's easy to learn and usually rather self-explanatory. Just copy and paste an existing command and work from there. The frontend code is found in the directory [synadm/cli](https://github.com/JOJ0/synadm/blob/master/synadm/cli/)

_Note: If you are not familiar with Python code, don't let yourself get distracted with the unusual @statements that define arguments and options. They are so-called decorators that "plug in" those options into your commands function. You don't actually need to understand why the Click library, makes use of this concept._


### Implementation Examples

Have a look at [this method](https://github.com/JOJ0/synadm/blob/68749391d6a291d2fac229214f59924189c775ac/synadm/cli/user.py#L358-L369) and [this one](https://github.com/JOJ0/synadm/blob/68749391d6a291d2fac229214f59924189c775ac/synadm/api.py#L531-L545).

That's all it needs to implement command `synadm user details <user_id>`.

Another example, this time using a POST based API endpoint: It implements command `synadm user password <user_id>`. [This](https://github.com/JOJ0/synadm/blob/68749391d6a291d2fac229214f59924189c775ac/synadm/cli/user.py#L276-L301) is the CLI-level method, and again it requires [a backend method in `api.py`](https://github.com/JOJ0/synadm/blob/68749391d6a291d2fac229214f59924189c775ac/synadm/api.py#L511-L529).


### Sending requests & URL encoding

Since commit [6874939](https://github.com/JOJ0/synadm/commit/68749391d6a291d2fac229214f59924189c775ac) (released in v0.41.2) `synadm` encodes URL's in a central place - the `query()` method located in the [synadm.api.ApiRequest](https://synadm.readthedocs.io/en/latest/synadm.module.html#synadm.api.ApiRequest) class.

Variables sent as part of the URL are required to be passed to the `query()` method **unaltered**. Do not use f-strings or str.format, let the `query()` method do the sanitizing of the URL.

If we take a look at the `user_password()` example in above's chapter, we have:

```python
self.query("post", "v1/reset_password/{user_id}", data=data, user_id=user_id)
```

- The `data` argument is passed as the request body and expects a Python dictionary.
- The `{user_id}` part of the URL will be replaced by the keyword argument `user_id`. The value of the keyword argument `user_id` will also be URL encoded to ensure [special cases](https://github.com/JOJ0/synadm/issues/96) don't break things.



### Helpers & Utilities

You'll find a couple of helpers & utilities [near the top of the api module's code](https://github.com/JOJ0/synadm/blob/master/synadm/api.py), right below the `query()` method, within the `ApiRequest` class. For example we already provide methods to translate unix timestamps to human readable formats and vice versa.

If you need to defer code to a helper function because you require reusing it or otherwise think it's a cleaner approach, put it where you need it: Either as a subfunction in your backend method in the `synadm/api` module or in the frontend function in `synadm/cli/yourcommand`. If you think you've wrote a function that is very generic and might be useful to other `synadm/api` methods as well, put it next to the helpers in the `ApiRequest` class and tell us about it in a PR-comment.

### Logging

Simply use `self.log.warn()` (or `.error`/`.debug`/`.info`) within the `synadm/api` module.

From a command's frontend code in the `synadm/cmd` package, logging is available via the `helper` object that is available to every subcommand function, for example: `helper.log.warn()`.

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

- Pythonism: `synadm` is a Python project and uses some handy features of the language. They might not be familiar to you since often we realize that contributors are professional programmers used to other languages or even are admins who are rather at home on the shell than in Python code. That is certainly all fine and we will support you with refactoring your code to be more pythonic.
- That said, we would still like `synadm` to stay approachable to Python beginners and would encourage contributors to try not to overcomplicate things.
- We require a line length of 79 characters in Python code.
  - Some editors (e.g. [vim](https://vimhelp.org/change.txt.html#gq)) have handy commands to quickly reformat multi-line text (e.g help texts of options).
  - For code passages, staying within this boundary and at the same time keeping code well readable, this can be achieved using PEP8's many [line continuation suggestions](https://peps.python.org/pep-0008/#code-lay-out).
- We don't require a maximum line length in Markdown files, for example _this document_ or `README.md`. Please omit line-breaks in sentences, paragraphs, and so on, when editing these docs.
- If you'd like to tidy up your commits or reduce commit count we welcome the use of `git commit --amend` and `git rebase`. If you'd like us to test your code or work together within your feature branch, be aware of that force pushing might complicate things and should be avoided in that case.


## Maintainers Notes

This section is a checklist for maintainers of the `synadm` project. This information may be useful for contributors, so we kept it public.

- We keep a branch named `dev` consistently existing that may be used for random things.
  - If a PR is opened from `dev`, it cannot be used by others.
  - If the current "occupier" of the branch demands it though, they can invite other maintainers to submit to that branch.
- Maintainers are not required to create branches in their own fork. Feature branches can be created directly in the [JOJ0/synadm](https://github.com/JOJ0/synadm) repository.
- One person should be the "owner" of each PR, no matter if opened by a contributor or a maintainer. Assistance from other maintainers can be request if desired.
  - Who the "owner" is can be arranged in the _synadm maintainers room_ (private) but usually would be the person who initially reviews the submission.
  - The "assignee" setting available on PR's and issues should be used to mark who the "owner" is.
  - The ultimate decision to merge should be with the "owner".
  - Assistance from other maintainers can be requested via a "review request" _or_ via "mentioning".
- PR's opened by maintainers (not external contributors) often require special attention about responsibilities:
  - Basically the "author" of such a PR is the "owner" as well.
  - The final decision to merge should still stay with the "owner". Requesting reviews from other maintainers should be the tool to responsibly decide when it is time to merge.
  - If a "reviewer" (usually another maintainer) requested changes from the "author" (who is also the "owner"), the reviewer should wait until the "author" re-requests a review.
  - A new commit showing up in the PR's branch might not be the indication that a new review is desired yet.


### Release process

Releasing a new version of `synadm` requires the following steps:

- Increase the version in all required files using the `bump.sh` script. `pip install bump2version` to your dev-environment to install the required tool. The final step to push to the master branch will be suggested by the script ('git push --follow-tags`).
- Following this push command the _release CI pipeline_ will be triggered and a tag and release draft be created on GitHub.
- Edit the generated draft and add release notes with the help of the "Generate release notes" button, but reformat into sections to be consistent with prior releases. If things were added without a PR, add those manually to the list of new features or fixes.
- Once the release notes are fine, make them public. The package can now be pushed to PyPi using the script `pypi.sh`
- Activate a new documentation version via [https://readthedocs.org/projects/synadm/versions/](https://readthedocs.org/projects/synadm/versions/), thus we provide a version of the online documentation consistent with the content of to the newly released `synadm` package.
- Spread the news in #synadm.peek-a-boo.at.


## Maintainership

If you feel like supporting the `synadm` project on a regular basis, consider applying for maintainership. We believe in Open Source software and think no matter if you are a programmer or not, there is plenty of things to do and still a lot of room for improvement. Contact either via [#synadm:peek-a-boo.at](https://matrix.to/#/%23synadm%3Apeek-a-boo.at?via=jacksonchen666.com&via=maclemon.at&via=matrix.org&via=raim.ist) or private message to [@jojo:peek-a-boo.at](https://matrix.to/#/@jojo:peek-a-boo.at).
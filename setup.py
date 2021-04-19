# -*- coding: utf-8 -*-
# synadm
# Copyright (C) 2020-2021 Johannes Tiefenbacher
#
# synadm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# synadm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
with open('README.md') as f:
    long_description = f.read()

setup(
    name="synadm",
    version="0.29",
    author="Johannes Tiefenbacher",
    author_email="jt@peek-a-boo.at",
    description="Command line admin tool for Synapse (Matrix reference homeserver)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joj0/synadm",
    project_urls={
        "Bug Tracker": "https://github.com/joj0/synadm/issues",
        "Documentation": "https://github.com/joj0/synadm",
        "Source Code": "https://github.com/joj0/synadm"
    },
    license="GPLv3+",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: System :: Systems Administration",
        "Topic :: Communications :: Chat",
        "Environment :: Console"
    ],
    packages=find_packages(),
    install_requires=[
        "Click>=7.0,<8.0",
        "requests",
        "tabulate",
        "PyYaml",
        "click-option-group>=0.5.2",
    ],
    entry_points="""
        [console_scripts]
        synadm=synadm.cli:root
    """,
)

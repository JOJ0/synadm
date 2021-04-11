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

setup(
    name='synadm',
    version='0.28',
    packages=find_packages(),
    install_requires=[
        'Click>=7.0,<8.0',
        'requests',
        'tabulate',
        'PyYaml',
        'click-option-group>=0.5.2',
    ],
    entry_points='''
        [console_scripts]
        synadm=synadm.cli:root
    ''',
)

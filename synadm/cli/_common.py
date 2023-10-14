# -*- coding: utf-8 -*-
# synadm
# Copyright (C) 2020-2023 Johannes Tiefenbacher
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
"Common CLI options, option groups, helpers and utilities."

import click

from click_option_group import MutuallyExclusiveOptionGroup


def common_opts_raw_command(function):
    return click.argument(
        "endpoint", type=str
    )(
        click.option(
            "--method", "-m",
            type=click.Choice(["get", "post", "put", "delete"]),
            help="The HTTP method used for the request.",
            default="get", show_default=True
        )(function)
    )


data_group_raw_command = MutuallyExclusiveOptionGroup(
    "Data",
    help=""
)


def data_opts_raw_command(function):
    return data_group_raw_command.option(
            "--data", "-d", type=str, default='{}', show_default=True,
            help="""The JSON string sent in the body of post, put and delete
            requests - provided as a string. Make sure to escape it from shell
            interpretation by using single quotes. E.g '{"key1": "value1",
            "key2": 123}'"""
    )(
        data_group_raw_command.option(
            "--data-file", "-f", type=click.File("rt"),
            show_default=True,
            help="""Read JSON data from file. To read from stdin use "-" as the
            filename argument."""
        )(function)
    )

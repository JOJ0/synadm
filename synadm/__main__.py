# -*- coding: utf-8 -*-
# synadm
# Copyright (C) 2023 Nicolas Peugnet
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

"""Alternative entry point for running synadm

synadm is typically installed via pip, utilizing setuptools-configured entry
points for accessibility as `synadm`.

This file allows execution without formal installation using
`python -m synadm`, which proves useful, for instance, in Debian GNU/Linux
packaging.
"""

from synadm.cli import root

root()

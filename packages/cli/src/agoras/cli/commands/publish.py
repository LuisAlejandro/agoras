# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""agoras.cli.commands.publish module."""

from ..platform_runner import execute_platform_action


def main(**kwargs):
    """Run the publish command for the requested social network."""
    import sys
    import warnings

    network = kwargs.get("network")

    if network == "twitter":
        print("Warning: The 'twitter' network name is deprecated. Use 'x' instead.", file=sys.stderr)
        warnings.warn("The 'twitter' network name is deprecated. Use 'x' instead.", DeprecationWarning, stacklevel=2)

    return execute_platform_action(**kwargs)

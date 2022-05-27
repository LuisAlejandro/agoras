# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2016-2022, Social Actions CLI Developers.

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

"""

sacli.common.utils
===================

This module contains common and low level functions to all modules in sacli.

"""
from collections.abc import Iterable


# Taken from: http://stackoverflow.com/a/2158532
def flatten_list(array=[]):
    """

    Convert a nested list into one combined list.

    :param array: a list object with (optionally) nested list.
    :return: a generator with all nested lists combined.
    :rtype: a generator.

    .. versionadded:: 0.1

    >>> array = [[['1'], [[2, 3, 4], [5, 6, [7]], [8]]], [9, 10, 11, 12]]
    >>> list(flatten_list(array))
    ['1', 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    >>> array = []
    >>> list(flatten_list(array))
    []

    """
    for el in array:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten_list(el)
        else:
            yield el

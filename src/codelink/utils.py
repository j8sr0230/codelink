# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2023 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

from __future__ import annotations
from collections.abc import Iterable
from typing import Callable, Union

import PySide2.QtGui as QtGui


def crop_text(text: str = "Test", width: float = 30, font: QtGui.QFont = QtGui.QFont()) -> str:
    font_metrics: QtGui.QFontMetrics = QtGui.QFontMetrics(font)

    cropped_text: str = "..."
    string_idx: int = 0
    while all([font_metrics.horizontalAdvance(cropped_text) < width - font_metrics.horizontalAdvance("..."),
               string_idx < len(text)]):
        cropped_text = cropped_text[:string_idx] + text[string_idx] + cropped_text[string_idx:]
        string_idx += 1

    if string_idx == len(text):
        cropped_text: str = cropped_text[:len(text)]

    return cropped_text


def _zip_to_template(nested_data_template: list, flat_data: list) -> Union[list, tuple]:
    if type(nested_data_template) != list:
        item_idx: int = flat_data[0].index(nested_data_template)
        zipped_data: list = []
        for flat_list in flat_data:
            zipped_data.append(flat_list[item_idx])
        return tuple(zipped_data)
    else:
        return [_zip_to_template(sub_list, flat_data) for sub_list in nested_data_template]


def zip_nested(*nested_lists: list) -> list:
    nested_data_template: list = nested_lists[0]
    flat_data: list = [flatten(nested_list) for nested_list in nested_lists]
    return _zip_to_template(nested_data_template, flat_data)


def flatten(nested_list: Iterable) -> Iterable:
    """Flattens an arbitrary nested iterable.

    This function flattens an arbitrary nested list by concatenating all nested items.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Flat list
    :rtype: Iterable
    """

    flattened: list = []
    for item in nested_list:
        if isinstance(item, Iterable):
            flattened.extend(flatten(item))
        else:
            flattened.append(item)
    return flattened


def simplify(nested_list: Iterable) -> Iterable:
    """Simplifies an arbitrary nested iterable to the minimal nesting level.

    Flattens an iterable, but it leaves a minimal nesting. This is i.e. for vector sockets, where one usually does
    not want to concatenate coordinates of different vectors into a flat list.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Simplified list of iterables
    :rtype: Iterable
    """

    res: list = []

    copy: list = nested_list[:]
    while copy:
        entry: list = copy.pop()
        if isinstance(entry, Iterable):
            if len(list(entry)) > 0 and not all([isinstance(i, Iterable) for i in entry]):
                res.append(entry)
            else:
                copy.extend(entry)
        else:
            res.append(entry)

    res.reverse()
    return res


def graft(nested_list: Iterable) -> Iterable:
    """Grafts each atomic element into its own list.

    This function adds a level of nesting by inserting each atomic object of an iterable into its own list.
    This function considers vectors with three components as atomic objects, so it encloses each vector into a separate
    iterable.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Grafted list
    :rtype: Iterable
    """

    if isinstance(nested_list, Iterable):
        if len(list(nested_list)) == 3 and all([isinstance(i, float) for i in nested_list]):
            # Vectors with three components
            return [nested_list]
        else:
            temp_list: list = []
            for sub_list in nested_list:
                temp_list.append(graft(sub_list))
            return temp_list
    else:
        # Default atomic item, i.e. int, float, str, ...
        return [nested_list]


def graft_topology(nested_list: Iterable) -> Iterable:
    """Grafts each atomic element (lists of nesting level 1) into its own list.

    This function basically performs a graft operation, that considers lists with a nesting level 1 as atomic objects.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Grafted list
    :rtype: Iterable
    """

    if isinstance(nested_list, Iterable):
        if not all([isinstance(i, Iterable) for i in nested_list]):
            # Nesting level 1
            return [nested_list]
        else:
            temp_list: list = []
            for sub_list in nested_list:
                temp_list.append(graft_topology(sub_list))
            return temp_list
    else:
        # Default atomic item, i.e. int, float, str, ...
        return nested_list


def unwrap(nested_list: Iterable) -> Iterable:
    """Unwraps a nested iterable.

    This function removes one pair of square brackets from a nested list if possible.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Unwrapped list
    :rtype: Iterable
    """

    return list(nested_list)[0] if len(list(nested_list)) == 1 else nested_list


def wrap(nested_list: Iterable) -> Iterable:
    """Wraps a nested iterable.

    This function adds one pair of square brackets to a nested list.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :return: Unwrapped list
    :rtype: Iterable
    """

    return [nested_list]


def map_objects(nested_list: Iterable, object_type: type, callback: Callable) -> Iterable:
    """Applies a callback function to each data_type item of a nested input list.

    This function creates a list with evaluated data_type objects and the nested structure of the input list.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :param object_type: Only elements with this data type are evaluated by the callback function.
    :type object_type: type
    :param callback: Function that performs some action to each data_type element.
    :type callback: 'function'
    :return: Nested list with evaluated data_type objects.
    :rtype: Iterable
    """

    if isinstance(nested_list, list):
        temp_list: list = []
        for sub_list in nested_list:
            temp_list.append(map_objects(sub_list, object_type, callback))
        return temp_list
    else:
        if isinstance(nested_list, object_type):
            return callback(nested_list)


def map_last_level(nested_list: Iterable, object_type: type, callback: Callable) -> Iterable:
    """Applies a callback function to every penultimate level of a nested list.

    This function evaluates every penultimate level of a list containing only object_type elements with the specified
    callback function and returns a list with the nested structure of the input list.

    :param nested_list: Arbitrary nested input (data structure)
    :type nested_list: Iterable
    :param object_type: Only penultimate list levels contain object_type items are evaluated
    :type object_type: type
    :param callback: Function that performs some action to each penultimate list level
    :type callback: 'function'
    :return: Nested list with evaluated penultimate list levels
    :rtype: Iterable
    """

    if isinstance(nested_list, list):
        if all([isinstance(elem, object_type) for elem in nested_list]):
            return callback(nested_list)
        else:
            temp_list: list = []
            for sub_list in nested_list:
                temp_list.append(map_last_level(sub_list, object_type, callback))
            return temp_list

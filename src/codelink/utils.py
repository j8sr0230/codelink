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
from typing import Callable, Any, cast

import numpy as np
import awkward as ak

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


# noinspection PyUnusedLocal
def global_index(layout: ak.contents.Content, **kwargs) -> ak.contents.Content:
    if layout.is_numpy:
        layout: np.ndarray = cast(np.ndarray, layout)
        # noinspection PyTypeChecker
        return ak.contents.NumpyArray(
            np.arange(0, layout.data.size)
        )


def flatten(nested_list):
    result = []
    stack = [iter(nested_list)]

    while stack:
        for item in stack[-1]:
            if isinstance(item, list):
                stack.append(iter(item))
                break
            else:
                result.append(item)
        else:  # no break
            stack.pop()

    return result


def simplify(nested_list: list[Any]) -> list[Any]:
    result: list[Any] = []
    stack: list[Any] = nested_list[:]

    while stack:
        current: Any = stack.pop()
        if isinstance(current, list):
            if not all([isinstance(i, list) for i in current]):
                result.append(current)
            else:
                stack.extend(current)
        else:
            result.append(current)

    return result[::-1]


def simplify_ak(nested_array: ak.Array) -> ak.Array:
    min_max_depth: tuple[int, int] = nested_array.layout.minmax_depth
    reversed_nesting_axes: np.ndarray = np.arange(1, min_max_depth[0] - 1)[::-1]
    for nesting_axis in reversed_nesting_axes:
        nested_array = ak.flatten(nested_array, axis=nesting_axis)
    return nested_array


def graft(nested_list: list[Any]) -> list[Any]:
    return [graft(item) if isinstance(item, list) else [item] for item in nested_list]


def unwrap(nested_list: list[Any]) -> list[Any]:
    return list(nested_list)[0] if len(list(nested_list)) == 1 else nested_list


def wrap(nested_list: list[Any]) -> list[Any]:
    return [nested_list]


def map_value(callback: Callable, nested_list: list[Any]) -> list[Any]:
    if isinstance(nested_list, list):
        return [map_value(callback, item) for item in nested_list]
    else:
        return callback(nested_list)


def map_list(callback: Callable, nested_list: list[Any]) -> list[Any]:
    if isinstance(nested_list, list):
        if all(not isinstance(item, list) for item in nested_list):
            return callback(nested_list)
        else:
            return [map_list(callback, sub_list) for sub_list in nested_list]
    else:
        return nested_list


def map_one_to_many(inputs: list[ak.Array], mapper_function: Callable) -> ak.Array:
    inputs_dict: dict = {str(idx): nested_array for idx, nested_array in enumerate(inputs)}
    broadcasted_param_zip: ak.Array = ak.zip(inputs_dict)

    broadcasted_param_structure: dict[int, int] = {}
    broadcasted_array: ak.Array = broadcasted_param_zip["0"]
    for level in np.arange(1, broadcasted_array.layout.minmax_depth[1])[::-1]:
        broadcasted_param_structure[level] = ak.flatten(ak.num(broadcasted_array, axis=level), axis=None)

    flat_param_zip: ak.Array = ak.zip(
        [ak.flatten(broadcasted_param_zip[k], axis=None) for k in broadcasted_param_zip.fields]
    )

    result: list[np.ndarray] = []
    for param_tuple in flat_param_zip:
        result.append(mapper_function(param_tuple))

    for level_list_length in broadcasted_param_structure.values():
        result: ak.Array = ak.unflatten(result, level_list_length, axis=0)

    return result

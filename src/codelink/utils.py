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
from typing import Callable, Any, Union, cast

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


def vector_structure(nested_vector: ak.Array) -> ak.Array:
    return ak.transform(global_index, nested_vector.x)


def flatten_list(nested_list: list[Any]) -> list[Any]:
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


def flatten_array(nested_array: ak.Array) -> ak.Array:
    return ak.flatten(nested_array, axis=None)


def unflatten_array_like(flat_array: ak.Array, template_array: ak.Array) -> ak.Array:
    depth: int = template_array.layout.minmax_depth[0]
    reversed_nesting_axes: np.ndarray = np.arange(1, depth-1)[::-1]

    print("Depth", depth)
    print("Rev axis", reversed_nesting_axes)

    template_structure: dict[int, int] = {}
    for nesting_axes in reversed_nesting_axes:
        length: Union[int, ak.Array] = ak.num(template_structure, axis=nesting_axes)
        if type(length) is int:
            template_structure[nesting_axes] = length
        else:
            template_structure[nesting_axes] = ak.flatten(length, axis=None)

    print(template_structure)

    # result: ak.Array = ak.copy(flat_array)
    # for length in template_structure.values():
    #     result: ak.Array = ak.unflatten(result, length, axis=0)
    #
    # return result


def flatten_vector(nested_vector: ak.Array, as_tuple: bool = False) -> ak.Array:
    if not as_tuple:
        result: ak.Array = ak.zip({
            "x": ak.flatten(nested_vector.x, axis=None),
            "y": ak.flatten(nested_vector.y, axis=None),
            "z": ak.flatten(nested_vector.z, axis=None)
        })
    else:
        result: ak.Array = ak.zip([
            ak.flatten(nested_vector.x, axis=None),
            ak.flatten(nested_vector.y, axis=None),
            ak.flatten(nested_vector.z, axis=None)
        ])

    return result


def simplify_list(nested_list: list[Any]) -> list[Any]:
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


def simplify_array(nested_array: ak.Array) -> ak.Array:
    depth: int = nested_array.layout.minmax_depth[0]
    reversed_nesting_axes: np.ndarray = np.arange(1, depth - 1)[::-1]

    result: ak.Array = ak.copy(nested_array)
    for nesting_axis in reversed_nesting_axes:
        result = ak.flatten(result, axis=nesting_axis)
    return result


def simplify_vector(nested_vector: ak.Array, as_tuple: bool = False) -> ak.Array:
    result: ak.Array = simplify_array(nested_vector)

    if as_tuple:
        result: ak.Array = ak.zip([result.x, result.y, result.z])

    return result


def graft_list(nested_list: list[Any]) -> list[Any]:
    return [graft_list(item) if isinstance(item, list) else [item] for item in nested_list]


def unwrap_list(nested_list: list[Any]) -> list[Any]:
    return list(nested_list)[0] if len(list(nested_list)) == 1 else nested_list


def wrap_list(nested_list: list[Any]) -> list[Any]:
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


def map_ak_arrays_to_array(inputs: list[ak.Array], enlarger: Callable) -> ak.Array:
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
        result.append(enlarger(param_tuple))

    for level_list_length in broadcasted_param_structure.values():
        result: ak.Array = ak.unflatten(result, level_list_length, axis=0)

    return result

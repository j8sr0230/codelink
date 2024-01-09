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
from typing import Callable, Any, Union, cast, Iterator

import numpy as np
import awkward as ak

# noinspection PyPackageRequirements
from pivy import coin

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


def array_structure(nested_array: ak.Array) -> ak.Array:
    # return ak.transform(global_index, nested_array)

    flat_array: ak.Array = ak.flatten(nested_array, axis=None)
    item_count: int = ak.num(flat_array, axis=0)
    flat_indexes: ak.Array = ak.Array(np.arange(0, item_count))
    nested_index: ak.Array = unflatten_array_like(flat_indexes, nested_array)
    return nested_index


def simplified_array_structure(nested_array: ak.Array) -> Union[int, ak.Array]:
    max_depth: int = nested_array.layout.minmax_depth[1]
    if max_depth > 1:
        return ak.transform(global_index, ak.max(array_structure(nested_array), axis=-1))
    else:
        return 0


def record_structure(nested_record: ak.Array) -> ak.Array:
    return array_structure(nested_record[nested_record.fields[0]])


def simplified_rec_struct(nested_record: ak.Array) -> Union[int, ak.Array]:
    return simplified_array_structure(nested_record[nested_record.fields[0]])


def flatten_list(nested_list: list[Any]) -> list[Any]:
    result: list[Any] = []
    stack: list[Iterator[Any]] = [iter(nested_list)]

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


def unflatten_array_like(flat_array: Union[list, ak.Array], template_array: ak.Array) -> ak.Array:
    max_depth: int = template_array.layout.minmax_depth[1]

    template_structure: dict[int, Union[int, ak.Array]] = {}
    for depth in np.arange(0, max_depth)[::-1]:
        template_structure[depth] = ak.num(template_array, axis=depth)

    result: ak.Array = ak.copy(flat_array)
    for depth, length in template_structure.items():
        if depth > 0:
            result: ak.Array = ak.unflatten(result, ak.flatten(length, axis=None), axis=0)

    return result


def flatten_record(nested_record: ak.Array, as_tuple: bool = False) -> ak.Array:
    if not as_tuple:
        result: ak.Array = ak.zip(
            {k: ak.flatten(nested_record[k], axis=None) for k in nested_record.fields}, right_broadcast=True
        )
    else:
        result: ak.Array = ak.zip(
            [ak.flatten(nested_record[k], axis=None) for k in nested_record.fields], right_broadcast=True
        )
    return result


def unflatten_record_like(flat_record: ak.Array, template_record: ak.Array) -> ak.Array:
    return ak.zip(
        {k: unflatten_array_like(flat_record[k], template_record[k]) for k in flat_record.fields}, right_broadcast=True
    )


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
    max_depth: int = nested_array.layout.minmax_depth[1]
    reversed_nesting_axes: np.ndarray = np.arange(1, max_depth - 1)[::-1]

    result: ak.Array = ak.copy(nested_array)
    for nesting_axis in reversed_nesting_axes:
        result = ak.flatten(result, axis=nesting_axis)
    return result


def simplify_record(nested_record: ak.Array, as_tuple: bool = False) -> ak.Array:
    result: ak.Array = simplify_array(nested_record)

    if as_tuple:
        result: ak.Array = ak.zip([result[k] for k in result.fields], right_broadcast=True)

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


def mass_zip_to_array(nested_array: ak.Array) -> ak.Array:
    indexes: np.ndarray = np.arange(0, ak.num(nested_array, axis=0))
    zipped_tuples: ak.Array = ak.zip(list(nested_array[indexes]), right_broadcast=True)
    grafted_tuples: ak.Array = ak.unflatten(zipped_tuples, counts=1, axis=-1)
    return ak.concatenate(ak.unzip(grafted_tuples), axis=-1)


def shift_array_leafs(nested_array: ak.Array, offset: int) -> ak.Array:
    locale_idx: ak.Array = ak.local_index(nested_array)
    leaf_length: ak.Array = ak.num(nested_array, axis=-1)
    shifted_index: ak.Array = (locale_idx + offset) % leaf_length
    # return ak.Array(ak.to_list(nested_array[shifted_index]))
    return nested_array[shifted_index]


def flip_array_leafs(nested_array: ak.Array) -> ak.Array:
    local_idx: ak.Array = ak.local_index(nested_array)
    flipped_index: ak.Array = -1 * (local_idx - ak.max(local_idx))
    print(ak.type(nested_array))
    print(ak.type(flipped_index))
    # return ak.Array(ak.to_list(nested_array[flipped_index]))
    return nested_array[flipped_index]


def reorder_list(flat_list: list[Any], target_structure: ak.Array) -> list:
    flat_data_in: np.ndarray = np.array(flat_list, dtype="object")
    result: [Any] = []

    simple_structure: list = ak.to_list(simplify_array(target_structure))
    for simple_ids in simple_structure:
        if type(simple_ids) == int:
            result.append(flat_data_in[simple_ids])
        else:
            result.extend(flat_data_in[simple_ids])

    return result


def populate_coin_scene(child: coin.SoVRMLGroup, pivot: np.ndarray, axis: int,
                        parent: Union[coin.SoSeparator, coin.SoVRMLGroup]) -> coin.SoRotationXYZ:
    so_reverse_transformation: coin.SoTranslation = coin.SoTranslation()
    so_reverse_transformation.translation.setValue(pivot)
    so_rotation: coin.SoRotationXYZ = coin.SoRotationXYZ()
    so_rotation.axis = axis
    so_forward_transformation: coin.SoTranslation = coin.SoTranslation()
    so_forward_transformation.translation.setValue(-pivot)
    parent.addChild(so_reverse_transformation)
    parent.addChild(so_rotation)
    parent.addChild(so_forward_transformation)
    parent.addChild(child)

    return so_rotation

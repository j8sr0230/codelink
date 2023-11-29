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
from typing import TYPE_CHECKING, Optional, Any
import warnings
import inspect

import Part
import awkward as ak

import PySide2.QtWidgets as QtWidgets
import numpy as np

from utils import map_value, global_index
from nested_data import NestedData
from node_item import NodeItem
from sockets.vector_none import VectorNone
from sockets.shape_none import ShapeNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class ShapeContent(NodeItem):
    REG_NAME: str = "Shape Content"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name=REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Shape", content_value="<No Input>", is_input=True,
                      parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Solid", content_value="<No Input>", is_input=False,
                      parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Shell", content_value="<No Input>", is_input=False,
                      parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Face", content_value="<No Input>", is_input=False,
                      parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Wire", content_value="<No Input>", is_input=False,
                      parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Edge", content_value="<No Input>", is_input=False,
                      parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Vector", content_value="<No Input>", is_input=False,
                       parent_node=self)
        ]

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> list:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        nested_data: NestedData = self.input_data(0, args)

                        len_data: list[int] = []
                        flat_data: list[Part.Shape] = []
                        for shp in nested_data.data:
                            len_data.append(len(shp.Solids))
                            flat_data.extend(shp.Solids)

                        if len(flat_data) > 0:
                            data_structure: ak.Array = ak.Array(
                                map_value(lambda idx: np.arange(0, len_data[idx]), ak.to_list(nested_data.structure))
                            )
                            data_structure: ak.Array = ak.transform(global_index, data_structure)
                        else:
                            data_structure: ak.Array = ak.Array([[0]])

                        result: NestedData = NestedData(data=flat_data, structure=ak.flatten(data_structure, axis=-1))

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)
                        print("Content solid executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)
        return self._cache[cache_idx]

    def eval_1(self, *args) -> list:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        nested_data: NestedData = self.input_data(0, args)

                        len_data: list[int] = []
                        flat_data: list[Part.Shape] = []
                        for shp in nested_data.data:
                            len_data.append(len(shp.Shells))
                            flat_data.extend(shp.Shells)

                        if len(flat_data) > 0:
                            data_structure: ak.Array = ak.Array(
                                map_value(lambda idx: np.arange(0, len_data[idx]), ak.to_list(nested_data.structure))
                            )
                            data_structure: ak.Array = ak.transform(global_index, data_structure)
                        else:
                            data_structure: ak.Array = ak.Array([[0]])

                        result: NestedData = NestedData(data=flat_data, structure=ak.flatten(data_structure, axis=-1))

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(1, result)
                        print("Content shell executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)
        return self._cache[cache_idx]

    def eval_2(self, *args) -> list:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        nested_data: NestedData = self.input_data(0, args)

                        len_data: list[int] = []
                        flat_data: list[Part.Shape] = []
                        for shp in nested_data.data:
                            len_data.append(len(shp.Faces))
                            flat_data.extend(shp.Faces)

                        if len(flat_data) > 0:
                            data_structure: ak.Array = ak.Array(
                                map_value(lambda idx: np.arange(0, len_data[idx]), ak.to_list(nested_data.structure))
                            )
                            data_structure: ak.Array = ak.transform(global_index, data_structure)
                        else:
                            data_structure: ak.Array = ak.Array([[0]])

                        result: NestedData = NestedData(data=flat_data, structure=ak.flatten(data_structure, axis=-1))

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(2, result)
                        print("Content Face executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)
        return self._cache[cache_idx]

    def eval_3(self, *args) -> list:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        nested_data: NestedData = self.input_data(0, args)

                        len_data: list[int] = []
                        flat_data: list[Part.Shape] = []
                        for shp in nested_data.data:
                            len_data.append(len(shp.Wires))
                            flat_data.extend(shp.Wires)

                        if len(flat_data) > 0:
                            data_structure: ak.Array = ak.Array(
                                map_value(lambda idx: np.arange(0, len_data[idx]), ak.to_list(nested_data.structure))
                            )
                            data_structure: ak.Array = ak.transform(global_index, data_structure)
                        else:
                            data_structure: ak.Array = ak.Array([[0]])

                        result: NestedData = NestedData(data=flat_data, structure=ak.flatten(data_structure, axis=-1))

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(3, result)
                        print("Content wire executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)
        return self._cache[cache_idx]

    def eval_4(self, *args) -> list:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        nested_data: NestedData = self.input_data(0, args)

                        len_data: list[int] = []
                        flat_data: list[Part.Shape] = []
                        for shp in nested_data.data:
                            len_data.append(len(shp.Edges))
                            flat_data.extend(shp.Edges)

                        if len(flat_data) > 0:
                            data_structure: ak.Array = ak.Array(
                                map_value(lambda idx: np.arange(0, len_data[idx]), ak.to_list(nested_data.structure))
                            )
                            data_structure: ak.Array = ak.transform(global_index, data_structure)
                        else:
                            data_structure: ak.Array = ak.Array([[0]])

                        result: NestedData = NestedData(data=flat_data, structure=ak.flatten(data_structure, axis=-1))

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(4, result)
                        print("Content edge executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)
        return self._cache[cache_idx]

    def eval_5(self, *args) -> ak.Array:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        nested_data: NestedData = self.input_data(0, args)

                        vertexes: list[Any] = map_value(
                            lambda idx: nested_data.data[idx].Vertexes, ak.to_list(nested_data.structure)
                        )
                        vectors: ak.Array = ak.Array(
                            map_value(lambda v: {"x": v.Point[0], "y": v.Point[1], "z": v.Point[2]}, vertexes)
                        )

                        result: ak.Array = ak.flatten(vectors, axis=-1)

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(5, result)
                        print("Content vector executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)
        return self._cache[cache_idx]

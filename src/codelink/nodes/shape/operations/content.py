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
from typing import TYPE_CHECKING, Optional
import warnings
import inspect
import time

import Part
import awkward as ak

import PySide2.QtWidgets as QtWidgets

from utils import unflatten_array_like, global_index
from nested_data import NestedData
from node_item import NodeItem
from sockets.vector_none import VectorNone
from sockets.shape_none import ShapeNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = True


class Content(NodeItem):
    REG_NAME: str = "Content"

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

                        if DEBUG:
                            a: float = time.time()

                        len_data: list[list[int]] = []
                        flat_data: list[Part.Shape] = []
                        for shp in nested_data.data:
                            len_data.append(list(range(len(shp.Solids))))
                            flat_data.extend(shp.Solids)

                        len_data: ak.Array = ak.transform(global_index, len_data)
                        result: NestedData = NestedData(
                            data=flat_data, structure=unflatten_array_like(len_data, nested_data.structure)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            b: float = time.time()
                            print("Shape Content executed in", "{number:.{digits}f}".format(number=1000 * (b - a),
                                                                                            digits=2), "ms")

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

                        len_data: list[list[int]] = []
                        flat_data: list[Part.Shape] = []
                        for shp in nested_data.data:
                            len_data.append(list(range(len(shp.Shells))))
                            flat_data.extend(shp.Shells)

                        len_data: ak.Array = ak.transform(global_index, len_data)
                        result: NestedData = NestedData(
                            data=flat_data, structure=unflatten_array_like(len_data, nested_data.structure)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(1, result)

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

                        len_data: list[list[int]] = []
                        flat_data: list[Part.Shape] = []
                        for shp in nested_data.data:
                            len_data.append(list(range(len(shp.Faces))))
                            flat_data.extend(shp.Faces)

                        len_data: ak.Array = ak.transform(global_index, len_data)
                        result: NestedData = NestedData(
                            data=flat_data, structure=unflatten_array_like(len_data, nested_data.structure)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(2, result)

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

                        len_data: list[list[int]] = []
                        flat_data: list[Part.Shape] = []
                        for shp in nested_data.data:
                            len_data.append(list(range(len(shp.Wires))))
                            flat_data.extend(shp.Wires)

                        len_data: ak.Array = ak.transform(global_index, len_data)
                        result: NestedData = NestedData(
                            data=flat_data, structure=unflatten_array_like(len_data, nested_data.structure)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(3, result)

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

                        len_data: list[list[int]] = []
                        flat_data: list[Part.Shape] = []
                        for shp in nested_data.data:
                            len_data.append(list(range(len(shp.Edges))))
                            flat_data.extend(shp.Edges)

                        len_data: ak.Array = ak.transform(global_index, len_data)
                        result: NestedData = NestedData(
                            data=flat_data, structure=unflatten_array_like(len_data, nested_data.structure)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(4, result)

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
                        flat_data: list = []
                        for shp in nested_data.data:
                            vertexes: list[Part.Vertex] = shp.Vertexes
                            if len(vertexes) == 0:
                                continue

                            # noinspection PyUnresolvedReferences
                            vectors: ak.Array = ak.Array([{"x": v.Point[0], "y": v.Point[1], "z": v.Point[2]}
                                                          for v in vertexes])
                            flat_data.append(vectors)

                        flat_data: ak.Array = ak.Array(flat_data)

                        if len(flat_data.fields) == 0:
                            return ak.Array([{"x": 0, "y": 0, "z": 0}])

                        result_x: ak.Array = unflatten_array_like(flat_data.x, nested_data.structure)
                        result_y: ak.Array = unflatten_array_like(flat_data.y, nested_data.structure)
                        result_z: ak.Array = unflatten_array_like(flat_data.z, nested_data.structure)
                        result: ak.Array = ak.zip({"x": result_x, "y": result_y, "z": result_z})

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(5, result)

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)
        return self._cache[cache_idx]

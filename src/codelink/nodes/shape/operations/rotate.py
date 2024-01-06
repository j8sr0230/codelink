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

import awkward as ak

# noinspection PyUnresolvedReferences
import FreeCAD
import Part
import Points  # noqa

import PySide2.QtWidgets as QtWidgets

from utils import record_structure, flatten_record
from nested_data import NestedData
from node_item import NodeItem
from sockets.vector_none import VectorNone
from sockets.value_line import ValueLine
from sockets.shape_none import ShapeNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = True


class Rotate(NodeItem):
    REG_NAME: str = "Rotate"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Shape", content_value="<No Input>", is_input=True,
                      parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Pivot", content_value="<No Input>", is_input=True,
                       parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Axis", content_value="<No Input>", is_input=True,
                       parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Angle", content_value=0., is_input=True, parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Shape", content_value="<No Input>", is_input=False,
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
                        shape: NestedData = self.input_data(0, args)
                        rot_pivot: ak.Array = self.input_data(1, args)
                        rot_axis: ak.Array = self.input_data(2, args)
                        rot_angle: ak.Array = self.input_data(3, args)

                        if DEBUG:
                            a: float = time.time()

                        flat_pivot, struct_pivot = (ak.to_list(flatten_record(rot_pivot, True)),
                                                    record_structure(rot_pivot))
                        flat_axis, struct_axis = (ak.to_list(flatten_record(rot_axis, True)),
                                                  record_structure(rot_axis))

                        broadcasted_params: ak.Array = ak.zip(
                            {"shape": shape.structure, "pivot": struct_pivot, "axis": struct_axis, "angle": rot_angle}
                        )
                        flat_params: ak.Array = flatten_record(nested_record=broadcasted_params, as_tuple=True)

                        flat_data: list[Part.Shape] = []
                        for param_tuple in flat_params:
                            copy: Part.Shape = Part.Shape(shape.data[param_tuple["0"]])
                            copy.rotate(flat_pivot[param_tuple["1"]], flat_axis[param_tuple["2"]], param_tuple["3"])
                            flat_data.append(copy)

                        result: NestedData = NestedData(
                            data=flat_data,
                            structure=record_structure(broadcasted_params)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            b: float = time.time()
                            print("Rotate executed in", "{number:.{digits}f}".format(number=1000 * (b - a), digits=2),
                                  "ms")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

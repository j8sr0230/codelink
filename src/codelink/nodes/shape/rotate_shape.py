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

import awkward as ak

# noinspection PyUnresolvedReferences
import FreeCAD
import Part
import Points  # noqa

import PySide2.QtWidgets as QtWidgets

from utils import global_index
from nested_data import NestedData
from node_item import NodeItem
from sockets.vector_none_ak import VectorNoneAk
from sockets.shape_none import ShapeNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class RotateShape(NodeItem):
    REG_NAME: str = "Rotate Shape"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Shape", content_value="<No Input>", is_input=True,
                      parent_node=self),
            VectorNoneAk(undo_stack=self._undo_stack, name="Rotation", content_value="<No Input>", is_input=True,
                         parent_node=self),
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
                        rotation: ak.Array = self.input_data(1, args)

                        flat_rotation: ak.Array = ak.zip([ak.flatten(rotation.x, axis=None),
                                                          ak.flatten(rotation.y, axis=None),
                                                          ak.flatten(rotation.z, axis=None)])
                        flat_rotation_list: list[tuple[float, float, float]] = ak.to_list(flat_rotation)
                        axis: Points.Points = Points.Points()
                        axis.addPoints(flat_rotation_list)
                        nested_rotation: NestedData = NestedData(
                            data=axis.Points,
                            structure=ak.transform(global_index, ak.ones_like(rotation.x))
                        )

                        nested_params: ak.Array = ak.zip({
                            "shape": shape.structure,
                            "rotation": nested_rotation.structure
                        })
                        flat_params: ak.Array = ak.zip([
                            ak.flatten(nested_params.shape, axis=None),
                            ak.flatten(nested_params.rotation, axis=None)
                        ])
                        flat_params_list: list[tuple[int, int]] = ak.to_list(flat_params)

                        data_structure: ak.Array = ak.transform(global_index, ak.ones_like(nested_params.shape))
                        flat_data: list[Part.Shape] = []
                        for param in flat_params_list:
                            copy: Part.Shape = Part.Shape(shape.data[param[0]])
                            copy.rotate(copy.CenterOfGravity, nested_rotation.data[param[1]], 45)
                            flat_data.append(copy)

                        result: NestedData = NestedData(
                            data=flat_data,
                            structure=ak.transform(global_index, data_structure)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)
                        print("Rotation executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

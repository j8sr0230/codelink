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

import PySide2.QtWidgets as QtWidgets

from utils import global_index
from nested_data import NestedData
from node_item import NodeItem
from sockets.value_line import ValueLine
from sockets.shape_none import ShapeNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class Box(NodeItem):
    REG_NAME: str = "Box"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ValueLine(undo_stack=self._undo_stack, name="L", content_value=10., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="W", content_value=10., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="H", content_value=10., is_input=True, parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Box", content_value="<No Input>", is_input=False,
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
                        length: ak.Array = self.input_data(0, args)
                        width: ak.Array = self.input_data(1, args)
                        height: ak.Array = self.input_data(2, args)

                        nested_params: ak.Array = ak.zip({"length": length, "width": width, "height": height})
                        flat_param_tuples: ak.Array = ak.zip([ak.flatten(nested_params.length, axis=None),
                                                              ak.flatten(nested_params.width, axis=None),
                                                              ak.flatten(nested_params.height, axis=None)])
                        flat_param_list: list[tuple[float, float, float]] = ak.to_list(flat_param_tuples)

                        data_structure: ak.Array = ak.ones_like(nested_params.length)
                        flat_data: list[Part.Shape] = []
                        for param in flat_param_list:
                            flat_data.append(Part.makeBox(param[0], param[1], param[2]))

                        result: NestedData = NestedData(
                            data=flat_data,
                            structure=ak.transform(global_index, data_structure)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)
                        print("Box executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

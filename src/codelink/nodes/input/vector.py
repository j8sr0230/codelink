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

import FreeCAD
import awkward as ak

import PySide2.QtWidgets as QtWidgets

from utils import map_re
from node_item import NodeItem
from sockets.value_line import ValueLine
from sockets.vector_none import VectorNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class Vector(NodeItem):
    REG_NAME: str = "Vector"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name=REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ValueLine(undo_stack=self._undo_stack, name="X", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Y", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Z", content_value=0., is_input=True, parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Vector", content_value="<No Input>", is_input=False,
                       parent_node=self)
        ]

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> ak.Array:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        x: list[Any] = self.input_data(0, args)
                        y: list[Any] = self.input_data(1, args)
                        z: list[Any] = self.input_data(2, args)

                        zipped_input: ak.Array = ak.zip([x, y, z])
                        result: list = map_re(FreeCAD.Vector, zipped_input.to_list())

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)
                        print("Vector executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

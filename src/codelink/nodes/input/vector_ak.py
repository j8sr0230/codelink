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

import awkward as ak

import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem
from sockets.value_line import ValueLine
from sockets.vector_none_ak import VectorNoneAk

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class VectorAk(NodeItem):
    REG_NAME: str = "Vector Ak"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name=REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ValueLine(undo_stack=self._undo_stack, name="X", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Y", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Z", content_value=0., is_input=True, parent_node=self),
            VectorNoneAk(undo_stack=self._undo_stack, name="Vector", content_value="<No Input>", is_input=False,
                         parent_node=self)
        ]

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> list:
        result: ak.Array = ak.Array([{"x": 0, "y": 0, "z": 0}])

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    x: list = self.input_data(0, args)
                    y: list = self.input_data(1, args)
                    z: list = self.input_data(2, args)

                    zipped_input: ak.Array = ak.zip({"x": x, "y": y, "z": z})
                    result: ak.Array = ak.Array(zipped_input)

                    self._is_dirty: bool = False

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

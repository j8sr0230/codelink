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

# noinspection PyUnresolvedReferences
import FreeCAD
import Part

import PySide2.QtWidgets as QtWidgets

from utils import map_objects, broadcast_data_tree
from node_item import NodeItem
from value_line import ValueLine
from shape_none import ShapeNone

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
            ShapeNone(undo_stack=self._undo_stack, name="Box", content_value="<No Input>", is_input=False, parent_node=self)
        ]
        for widget in self._socket_widgets:
            self._content_widget.hide()
            self._content_layout.addWidget(widget)
            self._content_widget.show()

        self.update_all()

        # Socket-wise node eval methods
        self._evals: list[object] = [self.eval_socket_0]

    # --------------- Node eval methods ---------------

    @staticmethod
    def make_box(parameter_zip: tuple) -> Part.Shape:
        width: float = parameter_zip[0]
        length: float = parameter_zip[1]
        height: float = parameter_zip[2]
        return Part.makeBox(width, length, height)

    def eval_socket_0(self, *args) -> list:
        result: list = [Part.Shape()]

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    length: list = self.input_data(0, args)
                    width: list = self.input_data(1, args)
                    height: list = self.input_data(2, args)

                    data_tree: list = list(broadcast_data_tree(length, width, height))
                    result: list = list(map_objects(data_tree, tuple, self.make_box))

                    self._is_dirty: bool = False

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

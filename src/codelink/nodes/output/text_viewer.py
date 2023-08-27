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

import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem
from any_none import AnyNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class TextViewer(NodeItem):
    REG_NAME: str = "Text Viewer"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            AnyNone(undo_stack=self._undo_stack, name="In", content_value="<No Input>", is_input=True,
                    parent_node=self),
            AnyNone(undo_stack=self._undo_stack, name="Out", content_value="<No Input>", is_input=False,
                    parent_node=self)
        ]
        self.register_sockets()
        self.update_all()

        # Socket-wise node eval methods
        self._evals: list[object] = [self.eval_socket_0]

    # --------------- Node eval methods ---------------

    def eval_socket_0(self, *args) -> list:
        result: list = []

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    result: list = self.input_data(0, args)
                    print([str(input_item) for input_item in self.input_data(0, args)])
                    self._is_dirty: bool = False

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

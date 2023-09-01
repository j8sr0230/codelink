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
from sockets.vector_none_ak import VectorNoneAk

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class AwkwardViewer(NodeItem):
    REG_NAME: str = "Awkward Viewer"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            VectorNoneAk(undo_stack=self._undo_stack, name="In", content_value="<No Input>", is_input=True,
                         parent_node=self),
            VectorNoneAk(undo_stack=self._undo_stack, name="Out", content_value="<No Input>", is_input=False,
                         parent_node=self)
        ]

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> ak.Array:
        result: ak.Array = ak.Array([{"x": 0, "y": 0, "z": 0}])

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    result: ak.Array = ak.Array(self.input_data(0, args))
                    result.show(limit_rows=100, limit_cols=100)
                    self._is_dirty: bool = False

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return ak.Array(self.output_data(0, result))

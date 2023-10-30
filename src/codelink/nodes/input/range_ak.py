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

import numpy as np
import awkward as ak

import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem
from sockets.value_line_ak import ValueLineAk

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class RangeAk(NodeItem):
    REG_NAME: str = "RangeAk"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ValueLineAk(undo_stack=self._undo_stack, name="Start", content_value=0., is_input=True, parent_node=self),
            ValueLineAk(undo_stack=self._undo_stack, name="Stop", content_value=10., is_input=True, parent_node=self),
            ValueLineAk(undo_stack=self._undo_stack, name="Step", content_value=1., is_input=True, parent_node=self),
            ValueLineAk(undo_stack=self._undo_stack, name="Range", content_value="<No Input>", is_input=False,
                        parent_node=self)
        ]

        ak.behavior[np.absolute, "range_param"] = self.make_range

    # --------------- Node eval methods ---------------

    @staticmethod
    def make_range(range_params):
        print(range_params.start)
        rr = np.arange(range_params.start, range_params.stop, range_params.step)
        print(rr)
        return ak.to_layout(rr)

    def eval_socket_0(self, *args) -> list:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            result: ak.Array = ak.Array([0.])

            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        start: ak.Array = self.input_data(0, args)
                        stop: ak.Array = self.input_data(1, args)
                        step: ak.Array = self.input_data(2, args)

                        input_data: ak.Array = ak.zip({"start": start, "stop": stop, "step": step},
                                                      with_name="range_param")

                        result: ak.Array = np.absolute(input_data)

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

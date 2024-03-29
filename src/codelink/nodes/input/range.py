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

import numpy as np
import awkward as ak

import PySide2.QtWidgets as QtWidgets

from utils import flatten_record, unflatten_array_like
from node_item import NodeItem
from sockets.value_line import ValueLine

if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG: bool = True


class Range(NodeItem):
    REG_NAME: str = "Range"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ValueLine(undo_stack=self._undo_stack, name="Start", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Stop", content_value=10., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Step", content_value=1., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Range", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]

    # --------------- Node eval methods ---------------

    @staticmethod
    def make_range(parameter_zip: ak.Array) -> np.ndarray:
        return np.arange(parameter_zip["0"], parameter_zip["1"], parameter_zip["2"])

    def eval_socket_0(self, *args) -> ak.Array:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        start: ak.Array = self.input_data(0, args)
                        stop: ak.Array = self.input_data(1, args)
                        step: ak.Array = self.input_data(2, args)

                        if DEBUG:
                            a: float = time.time()

                        broadcasted_params: ak.Array = ak.zip(
                            {"start": start, "stop": stop, "step": step}, right_broadcast=True
                        )
                        flat_params: ak.Array = flatten_record(nested_record=broadcasted_params, as_tuple=True)

                        result: list[np.ndarray] = []
                        for param_tuple in flat_params:
                            result.append(self.make_range(param_tuple))

                        result: ak.Array = unflatten_array_like(result, broadcasted_params)

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0,  ak.flatten(result, axis=-1))

                        if DEBUG:
                            b: float = time.time()
                            print("Range executed in", "{number:.{digits}f}".format(number=1000 * (b - a), digits=2),
                                  "ms")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

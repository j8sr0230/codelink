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

from node_item import NodeItem
from sockets.value_line import ValueLine

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class RangeIt(NodeItem):
    REG_NAME: str = "Range It"

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

                        a: float = time.time()

                        nested_param_zip: ak.Array = ak.zip({"start": start, "stop": stop, "step": step})

                        nested_param_structure: dict[int, int] = {}
                        nested_array: ak.Array = nested_param_zip.start
                        for level in np.arange(1, nested_array.layout.minmax_depth[1])[::-1]:
                            nested_param_structure[level] = ak.flatten(ak.num(nested_array, axis=level), axis=None)

                        flat_param_zip: ak.Array = ak.zip([ak.flatten(nested_param_zip.start, axis=None),
                                                           ak.flatten(nested_param_zip.stop, axis=None),
                                                           ak.flatten(nested_param_zip.step, axis=None)
                                                           ])

                        flat_result: list[np.ndarray] = []
                        for param_tuple in flat_param_zip:
                            flat_result.append(np.arange(param_tuple["0"], param_tuple["1"], param_tuple["2"]))

                        for level_list_length in nested_param_structure.values():
                            flat_result: ak.Array = ak.unflatten(flat_result, level_list_length, axis=0)

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0,  ak.flatten(flat_result, axis=-1))

                        b: float = time.time()
                        print("Range It executed")
                        print(1000 * (b - a), "ms")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

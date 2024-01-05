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

# noinspection PyUnresolvedReferences
import FreeCAD
import Part
import Points  # noqa

import PySide2.QtWidgets as QtWidgets

from nested_data import NestedData
from utils import record_structure, flatten_record
from node_item import NodeItem
from sockets.shape_none import ShapeNone
from sockets.value_line import ValueLine

if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG: bool = True


class RegularPolygon(NodeItem):
    REG_NAME: str = "Regular Polygon"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ValueLine(undo_stack=self._undo_stack, name="Radius", content_value=1., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Sides", content_value=5., is_input=True, parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Regular Polygon", content_value="<No Input>", is_input=False,
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
                        radius: ak.Array = self.input_data(0, args)
                        sides: ak.Array = self.input_data(1, args)

                        if DEBUG:
                            a: float = time.time()

                        broadcasted_params: ak.Array = ak.zip({"radius": radius, "sides": sides})
                        flat_params: ak.Array = flatten_record(nested_record=broadcasted_params, as_tuple=True)

                        flat_data: list[Part.Shape] = []
                        for param_tuple in flat_params:
                            phi: np.ndarray = np.arange(0, 2 * np.pi, 2 * np.pi / int(param_tuple["1"]))
                            vectors = ak.zip([param_tuple["0"] * np.cos(phi), param_tuple["0"] * np.sin(phi), 0])

                            ctrl_pts: Points.Points = Points.Points()
                            ctrl_pts.addPoints(ak.to_list(vectors))
                            flat_data.append(Part.makePolygon(ctrl_pts.Points, True))

                        result: NestedData = NestedData(
                            data=flat_data,
                            structure=record_structure(broadcasted_params)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            b: float = time.time()
                            print("Regular Polygon executed in", "{number:.{digits}f}".format(number=1000 * (b - a),
                                                                                              digits=2), "ms")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

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

import awkward as ak

# noinspection PyUnresolvedReferences
import FreeCAD
import Part
import Points  # noqa

import PySide2.QtWidgets as QtWidgets

from utils import simplify_array, simplified_array_structure
from nested_data import NestedData
from node_item import NodeItem
from sockets.shape_none import ShapeNone


if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = True


class FaceFromCurve(NodeItem):
    REG_NAME: str = "Face from Curve"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Curve", content_value="<No Input>", is_input=True,
                      parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Face", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> NestedData:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        curves: NestedData = self.input_data(0, args)

                        if DEBUG:
                            a: float = time.time()

                        simple_crv, struct_crv = (simplify_array(curves.structure),
                                                  simplified_array_structure(curves.structure))

                        flat_data: list[Part.Shape] = []
                        if type(struct_crv) is int:
                            flat_data.append(Part.makeFace(curves.data, "Part::FaceMakerBullseye"))
                        else:
                            for crv_idx_set in simple_crv:
                                crv_set: list[Part.Edge] = [curves.data[idx] for idx in crv_idx_set]
                                flat_data.append(Part.makeFace(crv_set, "Part::FaceMakerBullseye"))

                        result: NestedData = NestedData(
                            data=flat_data,
                            structure=struct_crv if type(struct_crv) == ak.Array else ak.Array([0])
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            b: float = time.time()
                            print("Face from Curve executed in", "{number:.{digits}f}".format(number=1000 * (b - a),
                                                                                              digits=2), "ms")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

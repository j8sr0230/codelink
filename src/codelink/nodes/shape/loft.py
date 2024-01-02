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

import PySide2.QtWidgets as QtWidgets

from nested_data import NestedData
from utils import simplified_array_structure, simplify_array, flatten_record, record_structure
from node_item import NodeItem
from sockets.shape_none import ShapeNone
from sockets.bool_checkbox import BoolCheckBox


if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = True


class Loft(NodeItem):
    REG_NAME: str = "Loft"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Sections", content_value="<No Input>", is_input=True,
                      parent_node=self),
            BoolCheckBox(undo_stack=self._undo_stack, name="Solid", content_value=False, is_input=True,
                         parent_node=self),
            BoolCheckBox(undo_stack=self._undo_stack, name="Ruled", content_value=False, is_input=True,
                         parent_node=self),
            BoolCheckBox(undo_stack=self._undo_stack, name="Closed", content_value=False, is_input=True,
                         parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Loft", content_value="<No Input>", is_input=False,
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
                        sections: NestedData = self.input_data(0, args)
                        solid: ak.Array = self.input_data(1, args)
                        ruled: ak.Array = self.input_data(2, args)
                        closed: ak.Array = self.input_data(3, args)

                        if DEBUG:
                            a: float = time.time()

                        simple_sections, struct_sections = (simplify_array(sections.structure),
                                                            simplified_array_structure(sections.structure))

                        broadcasted_params: ak.Array = ak.zip(
                            {"sections": struct_sections, "solid": solid, "ruled": ruled, "closed": closed},
                            right_broadcast=True)

                        flat_params: ak.Array = flatten_record(nested_record=broadcasted_params, as_tuple=True)

                        flat_data: list[Part.Shape] = []
                        for param_tuple in flat_params:
                            if type(struct_sections) is int:
                                flat_data.append(Part.makeLoft(
                                    sections.data,
                                    bool(param_tuple["1"]), bool(param_tuple["2"]), bool(param_tuple["3"])
                                ))

                            else:
                                sub_sections: list[Part.Shape] = [
                                    sections.data[idx] for idx in simple_sections[param_tuple["0"]]
                                ]
                                flat_data.append(Part.makeLoft(
                                    sub_sections,
                                    bool(param_tuple["1"]), bool(param_tuple["2"]), bool(param_tuple["3"])
                                ))

                        result: NestedData = NestedData(
                            data=flat_data,
                            structure=record_structure(broadcasted_params)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            b: float = time.time()
                            print("Loft executed in", "{number:.{digits}f}".format(number=1000 * (b - a), digits=2),
                                  "ms")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

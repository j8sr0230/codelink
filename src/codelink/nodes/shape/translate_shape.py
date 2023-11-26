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

import awkward as ak

# noinspection PyUnresolvedReferences
import FreeCAD
import Part
import Points  # noqa

import PySide2.QtWidgets as QtWidgets

from utils import global_index
from nested_data import NestedData
from node_item import NodeItem
from sockets.vector_none import VectorNone
from sockets.shape_none import ShapeNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class TranslateShape(NodeItem):
    REG_NAME: str = "Translate Shape"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Shape", content_value="<No Input>", is_input=True,
                      parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Translation", content_value="<No Input>", is_input=True,
                       parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Shape", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> list:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        shape: NestedData = self.input_data(0, args)
                        translation: ak.Array = self.input_data(1, args)

                        flat_translations: ak.Array = ak.zip([ak.flatten(translation.x, axis=None),
                                                              ak.flatten(translation.y, axis=None),
                                                              ak.flatten(translation.z, axis=None)])
                        flat_translation_list: list[tuple[float, float, float]] = ak.to_list(flat_translations)
                        pts: Points.Points = Points.Points()
                        pts.addPoints(flat_translation_list)
                        nested_translation: NestedData = NestedData(
                            data=pts.Points,
                            structure=ak.transform(global_index, translation.x)
                        )

                        nested_params: ak.Array = ak.zip({
                            "shape": shape.structure,
                            "translation": nested_translation.structure
                        })
                        flat_params: ak.Array = ak.zip([
                            ak.flatten(nested_params.shape, axis=None),
                            ak.flatten(nested_params.translation, axis=None)
                        ])
                        flat_params_list: list[tuple[int, int]] = ak.to_list(flat_params)

                        data_structure: ak.Array = ak.transform(global_index, ak.ones_like(nested_params.shape))
                        flat_data: list[Part.Shape] = []
                        for param in flat_params_list:
                            copy: Part.Shape = Part.Shape(shape.data[param[0]])
                            copy.translate(nested_translation.data[param[1]])
                            flat_data.append(copy)

                        result: NestedData = NestedData(
                            data=flat_data,
                            structure=ak.transform(global_index, data_structure)
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)
                        print("Translation executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

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

from utils import simplify_array, simplified_array_structure, flatten_record, record_structure
from nested_data import NestedData
from node_item import NodeItem
from sockets.shape_none import ShapeNone
from sockets.value_line import ValueLine


if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = True


class Thickness(NodeItem):
    REG_NAME: str = "Thickness"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Solid", content_value="<No Input>", is_input=True,
                      parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Cutout Id", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Thickness", content_value=1., is_input=True, parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Solid", content_value="<No Input>", is_input=False,
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
                        solid: NestedData = self.input_data(0, args)
                        cutout_id: ak.Array = self.input_data(1, args)
                        thickness: ak.Array = self.input_data(2, args)

                        if DEBUG:
                            a: float = time.time()

                        simple_cutout, struct_cutout = (ak.to_list(simplify_array(cutout_id)),
                                                        simplified_array_structure(cutout_id))

                        broadcasted_params: ak.Array = ak.zip(
                            {"solid": solid.structure, "cutout": struct_cutout, "thickness": thickness}
                        )
                        flat_params: ak.Array = flatten_record(nested_record=broadcasted_params, as_tuple=True)
                        flat_data: list[Part.Shape] = []
                        for param_tuple in flat_params:
                            target: Part.Solid = solid.data[param_tuple["0"]]
                            if len(target.Solids) > 0 and len(target.Vertexes) > 0:
                                if type(struct_cutout) == int:
                                    faces: list[Part.Face] = [
                                        target.Faces[int(idx)]
                                        if int(idx) in range(len(target.Faces)) else None for idx in simple_cutout
                                    ]
                                else:
                                    faces: list[Part.Face] = [
                                        target.Faces[int(idx)]
                                        if int(idx) in range(len(target.Faces)) else None
                                        for idx in simple_cutout[param_tuple["1"]]
                                    ]

                                flat_data.append(target.makeThickness(faces, param_tuple["2"], 0.1))

                                # target_obj: FreeCAD.DocumentObject = Part.show(target)
                                # result_obj: FreeCAD.DocumentObject = FreeCAD.activeDocument().addObject(
                                #     "Part::Thickness", "Thickness"
                                # )
                                #
                                # if type(struct_cutout) == int:
                                # face_names: list[str] = ["Face" + str(int(face_idx)) for face_idx in simple_cutout]
                                # else:
                                #     face_names: list[str] = ["Face" + str(int(face_idx))
                                #                              for face_idx in simple_cutout[param_tuple["1"]]]
                                # result_obj.Faces = (target_obj, face_names) if face_names[0] != "Face0"
                                # else target_obj
                                # result_obj.Mode = 0
                                # result_obj.Join = 2
                                # result_obj.Value = param_tuple["2"]
                                # FreeCAD.activeDocument().recompute()
                                #
                                # # noinspection PyUnresolvedReferences
                                # flat_data.append(result_obj.Shape)
                                #
                                # FreeCAD.activeDocument().removeObject(target_obj.Name)
                                # FreeCAD.activeDocument().removeObject(result_obj.Name)

                            result: NestedData = NestedData(
                                data=flat_data,
                                structure=record_structure(broadcasted_params)
                            )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            b: float = time.time()
                            print("Thickness executed in", "{number:.{digits}f}".format(number=1000 * (b - a),
                                                                                        digits=2), "ms")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

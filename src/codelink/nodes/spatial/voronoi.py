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
from typing import TYPE_CHECKING, Optional, Union, cast
from collections import defaultdict
from math import fabs
import importlib
import warnings
import inspect
import itertools

import numpy as np
from scipy.spatial import Voronoi
import awkward as ak

# noinspection PyUnresolvedReferences
import FreeCAD
import Part
import Points  # noqa

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from nested_data import NestedData
from utils import simplify_ak, global_index, map_last_level
from node_item import NodeItem
from input_widgets import OptionBoxWidget
from sockets.shape_none import ShapeNone
from sockets.value_line import ValueLine
from sockets.vector_none import VectorNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class VoronoiNode(NodeItem):
    REG_NAME: str = "Voronoi"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget()
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Face", "Solid"])
        for option_idx in range(self._option_box.count()):
            self._option_box.model().setData(self._option_box.model().index(option_idx, 0), QtCore.QSize(160, 24),
                                             QtCore.Qt.SizeHintRole)

        item_list_view: QtWidgets.QListView = cast(QtWidgets.QListView, self._option_box.view())
        item_list_view.setSpacing(2)
        self._content_widget.hide()
        self._content_layout.addWidget(self._option_box)
        self._content_widget.show()

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Shape", content_value="<No Input>", is_input=True,
                      parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Position", content_value="<No Input>", is_input=True,
                       parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Scale", content_value=1., is_input=True,
                      parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Voronoi", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    def update_socket_widgets(self) -> None:
        # Hack to prevent cyclic imports
        set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")
        execute_dag_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "EmitDagChangedCommand")

        last_option_index: int = self._option_box.last_index
        current_option_index: int = self._option_box.currentIndex()

        self._undo_stack.beginMacro("Changes option box")
        self._undo_stack.push(execute_dag_cmd_cls(self.scene(), self))
        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )
        self._undo_stack.push(execute_dag_cmd_cls(self.scene(), self, on_redo=True))
        self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    @staticmethod
    def voronoi_on_surface(parameter_zip: tuple) -> Part.Shape:
        target: Part.Face = parameter_zip[0]
        points: list = parameter_zip[1]
        scale: float = parameter_zip[2]

        if len(target.Faces) > 0 and len(target.Vertexes) > 0:
            target: Part.Face = Part.Face(target.Faces[0])

            uvs: np.array = np.array([target.Surface.parameter(FreeCAD.Vector(v[0], v[1], v[2])) for v in points])

            u_min, u_max = np.min(uvs[0]), np.max(uvs[0])
            v_min, v_max = np.min(uvs[1]), np.max(uvs[1])
            u_offset, v_offset = fabs(u_max - u_min), fabs(v_max - v_min)
            bounds = list(itertools.product([u_min - u_offset, u_max + u_offset], [v_min - v_offset, v_max + v_offset]))
            all_points: np.ndarray = np.vstack((uvs, bounds))

            uv_vor: Voronoi = Voronoi(all_points)

            vor_vertices_uv = np.array([target.valueAt(uv[0], uv[1]) for uv in uv_vor.vertices])
            vor_regions_uv = [vor_vertices_uv[region].tolist() for region in uv_vor.regions
                              if all([-1 not in region]) and len(region) > 2]
            vor_regions_vector = map_last_level(vor_regions_uv, float, lambda v: FreeCAD.Vector(v[0], v[1], v[2]))

            vor_wires: list[Part.Shape] = [Part.makePolygon(region, True) for region in vor_regions_vector]
            vor_faces: list[Part.Shape] = [Part.Face(wire) for wire in vor_wires]
            vor_scaled_faces: list[Part.Shape] = [face.scale(scale, face.CenterOfGravity) for face in vor_faces]

            result: Part.Shape = Part.makeCompound(vor_scaled_faces)
            return result
        else:
            return Part.Shape()

    @staticmethod
    def voronoi_on_solid(parameter_zip: tuple) -> Part.Shape:
        target: Part.Shape = parameter_zip[0]
        points: list[tuple[float, float, float]] = parameter_zip[1]
        scale: float = parameter_zip[2]

        if len(target.Solids) > 0 and len(target.Vertexes) > 0:
            target: Part.Solid = Part.Solid(target.Solids[0])

            ###################################################################################
            # Based on https://github.com/nortikin/sverchok/blob/master/utils/voronoi3d.py
            box = target.BoundBox
            x_min, x_max = box.XMin, box.XMax
            y_min, y_max = box.YMin, box.YMax
            z_min, z_max = box.ZMin, box.ZMax
            x_offset, y_offset, z_offset = fabs(x_max - x_min), fabs(y_max - y_min), fabs(z_max - z_min)
            bounds = list(itertools.product([x_min - x_offset, x_max + x_offset], [y_min - y_offset, y_max + y_offset],
                                            [z_min - z_offset, z_max + z_offset]))

            all_points: np.ndarray = np.vstack((points, bounds))
            vor: Voronoi = Voronoi(all_points)
            faces_per_solid = defaultdict(list)
            n_ridges = len(vor.ridge_points)

            for ridge_idx in range(n_ridges):
                site_idx_1, site_idx_2 = vor.ridge_points[ridge_idx]
                face = vor.ridge_vertices[ridge_idx]
                if -1 not in face:
                    faces_per_solid[site_idx_1].append(face)
                    faces_per_solid[site_idx_2].append(face)

            vor_solids: list = []
            for solid_idx in sorted(faces_per_solid.keys()):
                vor_faces: list = []
                for face in faces_per_solid[solid_idx]:
                    face_vertices: list = vor.vertices[face].tolist()
                    face_vectors: list = [FreeCAD.Vector(v[0], v[1], v[2]) for v in face_vertices]

            ###################################################################################

                    vor_faces.append(Part.Face(Part.makePolygon(face_vectors, True)))

                vor_solid: Part.Shape = Part.Solid(Part.Shell(vor_faces))
                if vor_solid.isValid():
                    vor_solids.append(vor_solid)

            # Inner voronoi solids
            vor_solids: list[Part.Shape] = [solid.scale(scale, solid.CenterOfGravity) for solid in vor_solids]

            return target.common(Part.makeCompound(vor_solids))

        else:
            return Part.Shape()

    def eval_0(self, *args) -> ak.Array:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        shape: NestedData = self.input_data(0, args)
                        position: ak.Array = self.input_data(1, args)
                        scale: ak.Array = self.input_data(2, args)

                        pos_struct: Union[ak.Array, float] = ak.max(ak.ones_like(position.x), axis=-1)
                        pos_struct: ak.Array = (ak.transform(global_index, pos_struct) if type(pos_struct) == ak.Array
                                                else ak.Array([0]))

                        nested_params: ak.Array = ak.zip({"shape": shape.structure, "pos": pos_struct, "scale": scale},
                                                         right_broadcast=True)
                        simple_params: ak.Array = ak.zip([
                            ak.flatten(nested_params.shape, axis=None),
                            ak.flatten(nested_params.pos, axis=None),
                            ak.flatten(nested_params.scale, axis=None)
                        ])
                        simple_params_list: ak.Array = ak.to_list(simple_params)

                        simple_pos_tuple: ak.Array = simplify_ak(ak.zip([position.x, position.y, position.z]))
                        simple_pos_depth: tuple[int, int] = simple_pos_tuple.layout.minmax_depth
                        simple_pos_list: list[tuple[float, float, float]] = ak.to_list(simple_pos_tuple)

                        flat_data: list[Part.Shape] = []
                        if self._option_box.currentText() == "Face":
                            for param in simple_params_list:
                                if simple_pos_depth[0] == 1:
                                    param: tuple = (shape.data[param[0]], simple_pos_list, param[2])
                                else:
                                    param: tuple = (shape.data[param[0]], simple_pos_list[param[1]], param[2])
                                flat_data.append(self.voronoi_on_surface(param))

                        elif self._option_box.currentText() == "Solid":
                            for param in simple_params_list:
                                if simple_pos_depth[0] == 1:
                                    param: tuple = (shape.data[param[0]], simple_pos_list, param[2])
                                else:
                                    param: tuple = (shape.data[param[0]], simple_pos_list[param[1]], param[2])
                                flat_data.append(self.voronoi_on_solid(param))

                        data_structure: ak.Array = ak.transform(global_index, nested_params.shape)
                        result: NestedData = NestedData(
                            data=flat_data,
                            structure=data_structure
                        )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)
                        print("Voronoi executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

# --------------- Serialization ---------------

    def __getstate__(self) -> dict:
        data_dict: dict = super().__getstate__()
        data_dict["Option Idx"] = self._option_box.currentIndex()
        return data_dict

    def __setstate__(self, state: dict):
        super().__setstate__(state)
        self._option_box.blockSignals(True)
        self._option_box.setCurrentIndex(state["Option Idx"])
        self._option_box.blockSignals(False)
        self.update()

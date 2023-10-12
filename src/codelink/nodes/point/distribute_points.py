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
from typing import TYPE_CHECKING, Optional, cast
import importlib
import warnings

import numpy as np

import FreeCAD
import Part

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from utils import flatten, map_objects
from node_item import NodeItem
from input_widgets import OptionBoxWidget
from sockets.shape_none import ShapeNone
from sockets.value_line import ValueLine
from sockets.vector_none import VectorNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = False
BATCH_SIZE = 100
MAX_ITERATIONS = 1000


class DistributePoints(NodeItem):
    REG_NAME: str = "Distribute Points"

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
            ValueLine(undo_stack=self._undo_stack, name="Count", content_value=10., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Distance", content_value=1., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Seed", content_value=0., is_input=True, parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Position", content_value="<No Input>", is_input=False,
                       parent_node=self)
        ]

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    def update_socket_widgets(self) -> None:
        # Hack to prevent cyclic imports
        set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")
        execute_dag_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "ExecuteDagCommand")

        last_option_index: int = self._option_box.last_index
        current_option_index: int = self._option_box.currentIndex()

        self._undo_stack.beginMacro("Changes option box")
        self._undo_stack.push(execute_dag_cmd_cls(self.scene(), self))
        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )
        self._undo_stack.push(execute_dag_cmd_cls(self.scene(), self, on_redo=True))
        self._undo_stack.endMacro()

    # Based on https://github.com/nortikin/sverchok/blob/master/utils/field/probe.py
    @staticmethod
    def check_min_radius(new_position: list, old_positions: list, min_radius: float) -> bool:
        if not old_positions:
            return True

        new_position: np.array = np.array(new_position)
        old_positions: np.array = np.array(old_positions)
        distances: np.array = np.linalg.norm(old_positions - new_position, axis=1)
        ok: bool = (min_radius < distances).all()

        return ok

    def populate_positions_solid(self, target: Part.Shape, count: int = 10, distance: float = 10.) -> list:
        if isinstance(target, Part.Solid):
            box = target.BoundBox
            bbox = ((box.XMin, box.YMin, box.ZMin), (box.XMax, box.YMax, box.ZMax))
            b1, b2 = bbox
            x_min, y_min, z_min = b1
            x_max, y_max, z_max = b2

            done: int = 0
            iterations: int = 0
            generated_positions: list = []

            while done < count:
                iterations += 1

                if DEBUG:
                    print("Iteration no.:", iterations)

                if iterations > MAX_ITERATIONS:
                    raise ValueError("Maximum number of iterations reached.", MAX_ITERATIONS)

                left: int = count - done
                batch_size: int = min(BATCH_SIZE, left)

                batch_x: list = list(np.random.uniform(low=x_min, high=x_max, size=batch_size))
                batch_y: list = list(np.random.uniform(low=y_min, high=y_max, size=batch_size))
                batch_z: list = list(np.random.uniform(low=z_min, high=z_max, size=batch_size))
                batch: list = list(zip(batch_x, batch_y, batch_z))

                candidates: list = [
                    coordinate for coordinate in batch if target.isInside(FreeCAD.Vector(coordinate), 0.1, True)
                ]

                if len(candidates) > 0:
                    if distance == 0:
                        good_positions: list = candidates
                    else:
                        good_positions: list = []
                        for candidate in candidates:
                            if self.check_min_radius(candidate, generated_positions + good_positions, distance):
                                good_positions.append(candidate)

                    generated_positions.extend(good_positions)
                    done += len(good_positions)

            return [FreeCAD.Vector(coordinates) for coordinates in generated_positions]

        else:
            return [FreeCAD.Vector(0, 0, 0)]

    def populate_positions_face(self, target: Part.Shape, count: int = 10, distance: float = 10.) -> list:
        if isinstance(target, Part.Face):
            done: int = 0
            iterations: int = 0
            generated_positions: list = []

            u_range: list = np.array(target.ParameterRange)[:2]
            v_range: list = np.array(target.ParameterRange)[2:]

            while done < count:
                iterations += 1

                if DEBUG:
                    print("Iteration no.:", iterations)

                if iterations > MAX_ITERATIONS:
                    raise ValueError("Maximum number of iterations reached.", MAX_ITERATIONS)

                left: int = count - done
                batch_size: int = min(BATCH_SIZE, left)

                batch_us: list = list(np.random.uniform(low=u_range[0], high=u_range[1], size=batch_size))
                batch_vs: list = list(np.random.uniform(low=v_range[0], high=v_range[1], size=batch_size))
                batch_uvs: list = list(zip(batch_us, batch_vs))

                batch_positions: list = [target.valueAt(uv[0], uv[1]) for uv in batch_uvs if
                                         target.isInside(target.valueAt(uv[0], uv[1]), 0.1, True)]
                candidates: list = [[v[0], v[1], v[2]] for v in batch_positions]

                if len(candidates) > 0:
                    if distance == 0:
                        good_positions: list = candidates
                    else:
                        good_positions: list = []
                        for candidate in candidates:
                            if self.check_min_radius(candidate, generated_positions + good_positions, distance):
                                good_positions.append(candidate)

                    generated_positions.extend(good_positions)
                    done += len(good_positions)

            return [FreeCAD.Vector(coordinates) for coordinates in generated_positions]

        elif isinstance(target, Part.Solid):
            result: list = []
            for target in target.Faces:
                result.append(self.populate_positions_face(target, count, distance))
            return result
        else:
            return [FreeCAD.Vector(0, 0, 0)]

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> list:
        result: list = [FreeCAD.Vector(0, 0, 0,)]

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    shape: list = self.input_data(0, args)
                    count: int = int(list(flatten(self.input_data(1, args)))[0])
                    distance: float = list(flatten(self.input_data(2, args)))[0]
                    seed: int = int(list(flatten(self.input_data(3, args)))[0])
                    np.random.seed(seed)

                    if self._option_box.currentText() == "Face":
                        result: list = list(
                            map_objects(
                                shape, Part.Shape, lambda target: self.populate_positions_face(target, count, distance)
                            )
                        )

                    elif self._option_box.currentText() == "Solid":
                        result: list = list(
                            map_objects(
                                shape, Part.Shape, lambda target: self.populate_positions_solid(target, count, distance)
                            )
                        )

                    self._is_dirty: bool = False

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

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

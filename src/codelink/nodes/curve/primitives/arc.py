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
import inspect
import time

import awkward as ak

# noinspection PyUnresolvedReferences
import FreeCAD
import Part
import Points  # noqa

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from nested_data import NestedData
from utils import record_structure, flatten_record
from node_item import NodeItem
from input_widgets import OptionBoxWidget
from sockets.shape_none import ShapeNone
from sockets.value_line import ValueLine
from sockets.vector_none import VectorNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG: bool = True


class Arc(NodeItem):
    REG_NAME: str = "Arc"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget(undo_stack)
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Degree", "3 Points"])
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
            ValueLine(undo_stack=self._undo_stack, name="Radius", content_value=10, is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Degree 1", content_value=0, is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Degree 2", content_value=90, is_input=True, parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Arc", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    def update_socket_widgets(self) -> None:
        # Hack to prevent cyclic imports
        add_socket_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "AddSocketCommand")
        remove_socket_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "RemoveSocketCommand")
        remove_edge_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "RemoveEdgeCommand")
        set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")
        emit_dag_changed_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "EmitDagChangedCommand")

        last_option_index: int = self._option_box.last_index
        current_option_name: str = self._option_box.currentText()
        current_option_index: int = self._option_box.currentIndex()
        input_widget_count: int = len(self.input_socket_widgets)

        self._undo_stack.beginMacro("Changes option box")
        self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self))

        if current_option_name == "3 Points":
            # Remove sockets
            while input_widget_count > 0:
                remove_socket: SocketWidget = self._socket_widgets[0]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
                self._undo_stack.push(remove_socket_cmd_cls(self, 0))
                input_widget_count -= 1

            # Add sockets
            new_first_socket: VectorNone = VectorNone(
                undo_stack=self._undo_stack, name="Point 1", content_value="<No Input>", is_input=True,
                parent_node=self)
            new_second_socket: VectorNone = VectorNone(
                undo_stack=self._undo_stack, name="Point 2", content_value="<No Input>", is_input=True,
                parent_node=self)
            new_third_socket: VectorNone = VectorNone(
                undo_stack=self._undo_stack, name="Point 3", content_value="<No Input>", is_input=True,
                parent_node=self)

            self._undo_stack.push(add_socket_cmd_cls(self, new_first_socket, 0))
            self._undo_stack.push(add_socket_cmd_cls(self, new_second_socket, 1))
            self._undo_stack.push(add_socket_cmd_cls(self, new_third_socket, 2))

        elif current_option_name == "Degree":
            # Remove sockets
            while input_widget_count > 0:
                remove_socket: SocketWidget = self._socket_widgets[0]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
                self._undo_stack.push(remove_socket_cmd_cls(self, 0))
                input_widget_count -= 1

            # Add sockets
            new_first_socket: ValueLine = ValueLine(
                undo_stack=self._undo_stack, name="Radius", content_value=10, is_input=True, parent_node=self)
            new_second_socket: ValueLine = ValueLine(
                undo_stack=self._undo_stack, name="Degree 1", content_value=0, is_input=True, parent_node=self)
            new_third_socket: ValueLine = ValueLine(
                undo_stack=self._undo_stack, name="Degree 2", content_value=90, is_input=True, parent_node=self)

            self._undo_stack.push(add_socket_cmd_cls(self, new_first_socket, 0))
            self._undo_stack.push(add_socket_cmd_cls(self, new_second_socket, 1))
            self._undo_stack.push(add_socket_cmd_cls(self, new_third_socket, 2))

        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )
        self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self, on_redo=True))
        self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> ak.Array:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        a: ak.Array = self.input_data(0, args)
                        b: ak.Array = self.input_data(1, args)
                        c: ak.Array = self.input_data(2, args)

                        if DEBUG:
                            x: float = time.time()

                        if self._option_box.currentText() == "Degree":
                            broadcasted_params: ak.Array = ak.zip({"rad": a, "deg_1": b, "deg_2": c})
                            flat_params: ak.Array = flatten_record(nested_record=broadcasted_params, as_tuple=True)

                            flat_data: list[Part.Shape] = []
                            for param_tuple in flat_params:
                                flat_data.append(Part.makeCircle(
                                    param_tuple["0"], FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1),
                                    param_tuple["1"],
                                    param_tuple["2"]
                                ))

                            result: NestedData = NestedData(
                                data=flat_data,
                                structure=record_structure(broadcasted_params)
                            )

                        elif self._option_box.currentText() == "3 Points":
                            flat_a, struct_a = (ak.to_list(flatten_record(a, True)), record_structure(a))
                            flat_b, struct_b = (ak.to_list(flatten_record(b, True)), record_structure(b))
                            flat_c, struct_c = (ak.to_list(flatten_record(c, True)), record_structure(c))

                            broadcasted_struct: ak.Array = ak.zip({
                                "a": struct_a, "b": struct_b, "c": struct_c}, right_broadcast=True
                            )

                            flat_struct: ak.Array = flatten_record(nested_record=broadcasted_struct, as_tuple=True)

                            flat_data: list[Part.Shape] = []
                            for param_tuple in flat_struct:
                                arc_pts: Points.Points = Points.Points()
                                arc_pts.addPoints(
                                    [flat_a[param_tuple["0"]], flat_b[param_tuple["1"]], flat_c[param_tuple["2"]]]
                                )
                                flat_data.append(Part.Edge(
                                    Part.Arc(arc_pts.Points[0], arc_pts.Points[1], arc_pts.Points[2])
                                ))

                            result: NestedData = NestedData(
                                data=flat_data,
                                structure=record_structure(broadcasted_struct)
                            )

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            y: float = time.time()
                            print("Arc executed in", "{number:.{digits}f}".format(number=1000 * (y - x), digits=2),
                                  "ms")

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

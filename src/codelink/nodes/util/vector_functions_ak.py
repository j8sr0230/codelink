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
import awkward as ak

import FreeCAD

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from utils import map_objects, broadcast_data_tree
from node_item import NodeItem
from input_widgets import OptionBoxWidget
from sockets.vector_none_ak import VectorNoneAk
from sockets.value_line import ValueLine

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class VectorFunctionsAk(NodeItem):
    REG_NAME: str = "Vector Functions Ak"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget()
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Add", "Sub", "Mul", "Div", "Cross", "Dot", "Scale", "Length"])
        item_list_view: QtWidgets.QListView = cast(QtWidgets.QListView, self._option_box.view())
        item_list_view.setSpacing(2)
        self._content_widget.hide()
        self._content_layout.addWidget(self._option_box)
        self._content_widget.show()

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            VectorNoneAk(undo_stack=self._undo_stack, name="A", content_value="<No Input>", is_input=True,
                         parent_node=self),
            VectorNoneAk(undo_stack=self._undo_stack, name="B", content_value="<No Input>", is_input=True,
                         parent_node=self),
            VectorNoneAk(undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
                         parent_node=self)
        ]

        # Overwrite numpy universal functions with awkward behaviors for custom records
        ak.behavior[np.add, "Vector3D", "Vector3D"] = self.vector_add
        ak.behavior[np.subtract, "Vector3D", "Vector3D"] = self.vector_sub

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    def update_socket_widgets(self) -> None:
        # Hack to prevent cyclic imports
        add_socket_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "AddSocketCommand")
        remove_socket_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "RemoveSocketCommand")
        remove_edge_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "RemoveEdgeCommand")
        set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")

        last_option_index: int = self._option_box.last_index
        current_option_name: str = self._option_box.currentText()
        current_option_index: int = self._option_box.currentIndex()

        self._undo_stack.beginMacro("Changes option box")

        if current_option_name == "Dot":
            if len(self.input_socket_widgets) == 2:
                if type(self._socket_widgets[1]) != VectorNoneAk:
                    remove_socket: SocketWidget = self._socket_widgets[1]
                    for edge in remove_socket.pin.edges:
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                    self._undo_stack.push(remove_socket_cmd_cls(self, 1))

                    new_socket_widget: VectorNoneAk = VectorNoneAk(
                        undo_stack=self._undo_stack, name="B", content_value="<No Input>", is_input=True,
                        parent_node=self
                    )
                    self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 1))
            else:
                new_socket_widget: VectorNoneAk = VectorNoneAk(
                    undo_stack=self._undo_stack, name="B", content_value="<No Input>", is_input=True,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 1))

            if type(self._socket_widgets[2]) != ValueLine:
                remove_socket: SocketWidget = self._socket_widgets[2]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                self._undo_stack.push(remove_socket_cmd_cls(self, 2))

                new_socket_widget: ValueLine = ValueLine(
                    undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 2))

        elif current_option_name == "Scale":
            if len(self.input_socket_widgets) == 2:
                if type(self._socket_widgets[1]) != ValueLine:
                    remove_socket: SocketWidget = self._socket_widgets[1]
                    for edge in remove_socket.pin.edges:
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                    self._undo_stack.push(remove_socket_cmd_cls(self, 1))

                    new_socket_widget: ValueLine = ValueLine(
                        undo_stack=self._undo_stack, name="B", content_value=1., is_input=True,
                        parent_node=self
                    )
                    self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 1))
            else:
                new_socket_widget: ValueLine = ValueLine(
                    undo_stack=self._undo_stack, name="B", content_value=1., is_input=True,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 1))

            if len(self.input_socket_widgets) == 2 and type(self._socket_widgets[2]) != VectorNoneAk:
                remove_socket: SocketWidget = self._socket_widgets[2]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                self._undo_stack.push(remove_socket_cmd_cls(self, 2))

                new_socket_widget: VectorNoneAk = VectorNoneAk(
                    undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 2))

        elif current_option_name == "Length":
            if len(self.input_socket_widgets) > 1:
                remove_socket: SocketWidget = self._socket_widgets[1]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                self._undo_stack.push(remove_socket_cmd_cls(self, 1))

            if type(self._socket_widgets[1]) != ValueLine:
                remove_socket: SocketWidget = self._socket_widgets[1]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                self._undo_stack.push(remove_socket_cmd_cls(self, 1))

                new_socket_widget: ValueLine = ValueLine(
                    undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 1))

        else:
            if len(self.input_socket_widgets) == 2:
                if type(self._socket_widgets[1]) != VectorNoneAk:
                    remove_socket: SocketWidget = self._socket_widgets[1]
                    for edge in remove_socket.pin.edges:
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                    self._undo_stack.push(remove_socket_cmd_cls(self, 1))

                    new_socket_widget: VectorNoneAk = VectorNoneAk(
                        undo_stack=self._undo_stack, name="B", content_value="<No Input>", is_input=True,
                        parent_node=self
                    )
                    self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 1))
            else:
                new_socket_widget: VectorNoneAk = VectorNoneAk(
                    undo_stack=self._undo_stack, name="B", content_value="<No Input>", is_input=True,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 1))

            if type(self._socket_widgets[2]) != VectorNoneAk:
                remove_socket: SocketWidget = self._socket_widgets[2]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                self._undo_stack.push(remove_socket_cmd_cls(self, 2))

                new_socket_widget: VectorNoneAk = VectorNoneAk(
                    undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 2))

        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )

        self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    @staticmethod
    def vector_add(a, b):
        return ak.contents.RecordArray(
            [
                ak.to_layout(a["x"] + b["x"]),
                ak.to_layout(a["y"] + b["y"]),
                ak.to_layout(a["z"] + b["z"]),
            ],
            ["x", "y", "z"],
            parameters={"__record__": "Vector3D"},
        )

    @staticmethod
    def vector_sub(a, b):
        return ak.contents.RecordArray(
            [
                ak.to_layout(a["x"] - b["x"]),
                ak.to_layout(a["y"] - b["y"]),
                ak.to_layout(a["z"] - b["z"]),
            ],
            ["x", "y", "z"],
            parameters={"__record__": "Vector3D"},
        )

    @staticmethod
    def mul(parameter_zip: tuple) -> FreeCAD.Vector:
        a: FreeCAD.Vector = parameter_zip[0]
        b: FreeCAD.Vector = parameter_zip[1]
        return FreeCAD.Vector(a.x * b.x, a.y * b.y, a.z * b.z)

    @staticmethod
    def div(parameter_zip: tuple) -> FreeCAD.Vector:
        a: FreeCAD.Vector = parameter_zip[0]
        b: FreeCAD.Vector = parameter_zip[1]
        return FreeCAD.Vector(a.x / b.x, a.y / b.y, a.z / b.z)

    @staticmethod
    def cross(parameter_zip: tuple) -> FreeCAD.Vector:
        a: FreeCAD.Vector = parameter_zip[0]
        b: FreeCAD.Vector = parameter_zip[1]
        return a.cross(b)

    @staticmethod
    def dot(parameter_zip: tuple) -> float:
        a: FreeCAD.Vector = parameter_zip[0]
        b: FreeCAD.Vector = parameter_zip[1]
        return a.dot(b)

    @staticmethod
    def scale_vec(parameter_zip: tuple) -> float:
        a: FreeCAD.Vector = parameter_zip[0]
        b: float = parameter_zip[1]
        return a.scale(b, b, b)

    @staticmethod
    def length(parameter_zip: tuple) -> float:
        a: FreeCAD.Vector = parameter_zip[0]
        return a.Length

    def eval_0(self, *args) -> list:
        result: ak.Record = ak.Record({"x": 0, "y": 0, "z": 0})

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    # TODO: Pass awkward array as input, not list
                    # print("a", type(self.input_data(0, args)[0]))
                    # print(self.input_data(0, args)[0])
                    a: ak.Array = ak.Array(self.input_data(0, args)[0], with_name="Vector3D")

                    if len(args) == 1:
                        if self._option_box.currentText() == "Length":
                            data_tree: list = list(broadcast_data_tree(a))
                            result: list = list(map_objects(data_tree, tuple, self.length))

                    if len(args) == 2:
                        b: ak.Array = ak.Array(self.input_data(1, args)[0], with_name="Vector3D")
                        # print("b", type(self.input_data(1, args)))
                        # print(self.input_data(1, args))

                        if self._option_box.currentText() == "Add":
                            result: ak.Array = a + b

                        elif self._option_box.currentText() == "Sub":
                            result: ak.Array = a - b

                        elif self._option_box.currentText() == "Mul":
                            result: list = list(map_objects(data_tree, tuple, self.mul))

                        elif self._option_box.currentText() == "Div":
                            result: list = list(map_objects(data_tree, tuple, self.div))

                        elif self._option_box.currentText() == "Cross":
                            result: list = list(map_objects(data_tree, tuple, self.cross))

                        elif self._option_box.currentText() == "Dot":
                            result: list = list(map_objects(data_tree, tuple, self.dot))

                        elif self._option_box.currentText() == "Scale":
                            result: list = list(map_objects(data_tree, tuple, self.scale_vec))

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

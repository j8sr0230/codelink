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

import awkward as ak

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import numpy as np

from utils import map_objects, map_last_level
from node_item import NodeItem
from input_widgets import OptionBoxWidget
from sockets.vector_none import VectorNone
from sockets.value_line import ValueLine

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class VectorFunctions(NodeItem):
    REG_NAME: str = "Vector Functions"

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
            VectorNone(undo_stack=self._undo_stack, name="A", content_value="<No Input>", is_input=True,
                       parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="B", content_value="<No Input>", is_input=True,
                       parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
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

        last_option_index: int = self._option_box.last_index
        current_option_name: str = self._option_box.currentText()
        current_option_index: int = self._option_box.currentIndex()

        self._undo_stack.beginMacro("Changes option box")

        if current_option_name == "Dot":
            if len(self.input_socket_widgets) == 2:
                if type(self._socket_widgets[1]) != VectorNone:
                    remove_socket: SocketWidget = self._socket_widgets[1]
                    for edge in remove_socket.pin.edges:
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                    self._undo_stack.push(remove_socket_cmd_cls(self, 1))

                    new_socket_widget: VectorNone = VectorNone(
                        undo_stack=self._undo_stack, name="B", content_value="<No Input>", is_input=True,
                        parent_node=self
                    )
                    self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 1))
            else:
                new_socket_widget: VectorNone = VectorNone(
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

            if len(self.input_socket_widgets) == 2 and type(self._socket_widgets[2]) != VectorNone:
                remove_socket: SocketWidget = self._socket_widgets[2]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                self._undo_stack.push(remove_socket_cmd_cls(self, 2))

                new_socket_widget: VectorNone = VectorNone(
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
                if type(self._socket_widgets[1]) != VectorNone:
                    remove_socket: SocketWidget = self._socket_widgets[1]
                    for edge in remove_socket.pin.edges:
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                    self._undo_stack.push(remove_socket_cmd_cls(self, 1))

                    new_socket_widget: VectorNone = VectorNone(
                        undo_stack=self._undo_stack, name="B", content_value="<No Input>", is_input=True,
                        parent_node=self
                    )
                    self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 1))
            else:
                new_socket_widget: VectorNone = VectorNone(
                    undo_stack=self._undo_stack, name="B", content_value="<No Input>", is_input=True,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 1))

            if type(self._socket_widgets[2]) != VectorNone:
                remove_socket: SocketWidget = self._socket_widgets[2]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))
                self._undo_stack.push(remove_socket_cmd_cls(self, 2))

                new_socket_widget: VectorNone = VectorNone(
                    undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 2))

        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )

        self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    # @staticmethod
    # def length(vector: tuple) -> float:
    #     a: FreeCAD.Vector = parameter_zip[0]
    #     return a.Length
    #
    # @staticmethod
    # def cross(parameter_zip: tuple) -> FreeCAD.Vector:
    #     a: FreeCAD.Vector = parameter_zip[0]
    #     b: FreeCAD.Vector = parameter_zip[1]
    #     return a.cross(b)
    #
    # @staticmethod
    # def dot(parameter_zip: tuple) -> float:
    #     a: FreeCAD.Vector = parameter_zip[0]
    #     b: FreeCAD.Vector = parameter_zip[1]
    #     return a.dot(b)

    def eval_0(self, *args) -> list:
        result: ak.Array = ak.Array([0., 0., 0.])

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    a: list = self.input_data(0, args)
                    if len(args) == 1:
                        if self._option_box.currentText() == "Length":
                            print(np.linalg.norm(a, axis=1))
                            # result: list = list(map_last_level(a, float, self.length))

                    if len(args) == 2:
                        b: list = self.input_data(1, args)

                        if self._option_box.currentText() == "Add":
                            result: ak.Array = ak.Array(a) + ak.Array(b)

                        elif self._option_box.currentText() == "Sub":
                            result: ak.Array = ak.Array(a) - ak.Array(b)

                        elif self._option_box.currentText() == "Mul":
                            result: ak.Array = ak.Array(a) * ak.Array(b)

                        elif self._option_box.currentText() == "Div":
                            result: ak.Array = ak.Array(a) / ak.Array(b)

                        # elif self._option_box.currentText() == "Cross":
                        #     result: list = list(map_objects(data_tree, tuple, self.cross))
                        #
                        # elif self._option_box.currentText() == "Dot":
                        #     result: list = list(map_objects(data_tree, tuple, self.dot))

                        elif self._option_box.currentText() == "Scale":
                            result: ak.Array = ak.Array(a) * b

                    self._is_dirty: bool = False

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result.to_list())

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

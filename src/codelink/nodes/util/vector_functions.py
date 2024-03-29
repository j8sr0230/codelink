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

import numpy as np
import awkward as ak

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem
from input_widgets import OptionBoxWidget
from sockets.vector_none import VectorNone
from sockets.value_line import ValueLine

if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = True


class VectorFunctionsAk(NodeItem):
    REG_NAME: str = "Vector Functions"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget(undo_stack)
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Add", "Sub", "Mul", "Div", "Cross", "Dot", "Scale", "Length"])
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
            VectorNone(undo_stack=self._undo_stack, name="A", content_value="<No Input>", is_input=True,
                       parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="B", content_value="<No Input>", is_input=True,
                       parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
                       parent_node=self)
        ]

        ak.behavior[np.add, "Vector3D", "Vector3D"] = self.vector_add
        ak.behavior[np.subtract, "Vector3D", "Vector3D"] = self.vector_sub
        ak.behavior[np.multiply, "Vector3D", "Vector3D"] = self.vector_mul
        ak.behavior[np.divide, "Vector3D", "Vector3D"] = self.vector_div
        ak.behavior[np.absolute, "Vector3D"] = self.vector_length

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    @staticmethod
    def vector_add(a, b) -> ak.contents.RecordArray:
        return ak.contents.RecordArray(
            [
                ak.to_layout(a.x + b.x),
                ak.to_layout(a.y + b.y),
                ak.to_layout(a.z + b.z),
            ],
            ["x", "y", "z"],
            parameters={"__record__": "Vector3D"},
        )

    @staticmethod
    def vector_sub(a, b) -> ak.contents.RecordArray:
        return ak.contents.RecordArray(
            [
                ak.to_layout(a.x - b.x),
                ak.to_layout(a.y - b.y),
                ak.to_layout(a.z - b.z),
            ],
            ["x", "y", "z"],
            parameters={"__record__": "Vector3D"},
        )

    @staticmethod
    def vector_mul(a, b) -> ak.contents.RecordArray:
        return ak.contents.RecordArray(
            [
                ak.to_layout(a.x * b.x),
                ak.to_layout(a.y * b.y),
                ak.to_layout(a.z * b.z),
            ],
            ["x", "y", "z"],
            parameters={"__record__": "Vector3D"},
        )

    @staticmethod
    def vector_div(a, b) -> ak.contents.RecordArray:
        return ak.contents.RecordArray(
            [
                ak.to_layout(a.x / b.x),
                ak.to_layout(a.y / b.y),
                ak.to_layout(a.z / b.z),
            ],
            ["x", "y", "z"],
            parameters={"__record__": "Vector3D"},
        )

    @staticmethod
    def vector_cross(a, b) -> ak.contents.RecordArray:
        return ak.contents.RecordArray(
            [
                ak.to_layout(a.y * b.z - a.z * b.y),
                ak.to_layout(a.z * b.x - a.x * b.z),
                ak.to_layout(a.x * b.y - a.y * b.x),
            ],
            ["x", "y", "z"],
            parameters={"__record__": "Vector3D"},
        )

    @staticmethod
    def vector_dot(a, b) -> ak.Array:
        return ak.Array(a.x * b.x + a.y * b.y + a.z * b.z)

    @staticmethod
    def vector_length(a) -> np.ndarray:
        return np.sqrt(a.x**2 + a.y**2 + a.z**2)

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

        self._undo_stack.beginMacro("Changes option box")
        self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self))

        if current_option_name == "Dot":
            if len(self.input_socket_widgets) == 2:
                if type(self._socket_widgets[1]) != VectorNone:
                    remove_socket: SocketWidget = self._socket_widgets[1]
                    for edge in remove_socket.pin.edges:
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
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
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
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
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
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
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
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
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
                self._undo_stack.push(remove_socket_cmd_cls(self, 1))

            if type(self._socket_widgets[1]) != ValueLine:
                remove_socket: SocketWidget = self._socket_widgets[1]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
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
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
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
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
                self._undo_stack.push(remove_socket_cmd_cls(self, 2))

                new_socket_widget: VectorNone = VectorNone(
                    undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 2))

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
                        a: ak.Array = ak.Array(self.input_data(0, args), with_name="Vector3D")

                        if DEBUG:
                            x: float = time.time()

                        if len(args) == 1:
                            if self._option_box.currentText() == "Length":
                                result: ak.Array = np.absolute(a)

                        if len(args) == 2:
                            if self._option_box.currentText() in ("Add", "Sub", "Mul", "Div", "Cross", "Dot", ):
                                b: ak.Array = ak.Array(self.input_data(1, args), with_name="Vector3D")

                                if self._option_box.currentText() == "Add":
                                    result: ak.Array = a + b

                                elif self._option_box.currentText() == "Sub":
                                    result: ak.Array = a - b

                                elif self._option_box.currentText() == "Mul":
                                    result: ak.Array = a * b

                                elif self._option_box.currentText() == "Div":
                                    result: ak.Array = a / b

                                elif self._option_box.currentText() == "Cross":
                                    ak.behavior[np.multiply, "Vector3D", "Vector3D"] = self.vector_cross
                                    result: ak.Array = a * b
                                    ak.behavior[np.multiply, "Vector3D", "Vector3D"] = self.vector_mul

                                elif self._option_box.currentText() == "Dot":
                                    ak.behavior[np.multiply, "Vector3D", "Vector3D"] = self.vector_dot
                                    result: ak.Array = a * b
                                    ak.behavior[np.multiply, "Vector3D", "Vector3D"] = self.vector_mul

                            elif self._option_box.currentText() == "Scale":
                                b: ak.Array = self.input_data(1, args)

                                b_vec: ak.Array = ak.zip({"x": b, "y": b, "z": b})
                                b_vec: ak.Array = ak.Array(b_vec, with_name="Vector3D")
                                result: ak.Array = a * b_vec

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            y: float = time.time()
                            print("Vector Functions executed in", "{number:.{digits}f}".format(number=1000 * (y - x),
                                                                                               digits=2), "ms")

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

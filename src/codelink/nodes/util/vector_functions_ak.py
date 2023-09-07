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
import numpy as np

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

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

        # class Vector3DArray(ak.Array):
        #     def vector_add(self, other):
        #         return ak.Array(
        #             {
        #                 "x": ak.to_layout(self["x"] + other["x"]),
        #                 "y": ak.to_layout(self["y"] + other["y"]),
        #                 "z": ak.to_layout(self["z"] + other["z"]),
        #             },
        #             with_name="Vector3D"
        #         )
        #
        #     def vector_sub(self, other):
        #         return ak.Array(
        #             {
        #                 "x": ak.to_layout(self["x"] - other["x"]),
        #                 "y": ak.to_layout(self["y"] - other["y"]),
        #                 "z": ak.to_layout(self["z"] - other["z"]),
        #             },
        #             with_name="Vector3D"
        #         )
        #
        #     def vector_mul(self, other):
        #         return ak.Array(
        #             {
        #                 "x": ak.to_layout(self["x"] * other["x"]),
        #                 "y": ak.to_layout(self["y"] * other["y"]),
        #                 "z": ak.to_layout(self["z"] * other["z"]),
        #             },
        #             with_name="Vector3D"
        #         )
        #
        #     def vector_div(self, other):
        #         return ak.Array(
        #             {
        #                 "x": ak.to_layout(self["x"] / other["x"]),
        #                 "y": ak.to_layout(self["y"] / other["y"]),
        #                 "z": ak.to_layout(self["z"] / other["z"]),
        #             },
        #             with_name="Vector3D"
        #         )
        #
        #     def vector_length(self):
        #         return (self.x ** 2 + self.y ** 2 + self.z ** 2)**0.5
        #
        #     def vector_dot(self, other):
        #         return self.x*other.x + self.y*other.y + self.z*other.z
        #
        #     def vector_cross(self, other):
        #         return ak.Array(
        #             {
        #                 "x": ak.to_layout(self["y"]*other["z"] - self["z"]*other["y"]),
        #                 "y": ak.to_layout(self["z"]*other["x"] - self["x"]*other["z"]),
        #                 "z": ak.to_layout(self["x"]*other["y"] - self["y"]*other["x"]),
        #             },
        #             with_name="Vector3D"
        #         )

        # Awkward behaviors for custom records
        # ak.behavior["*", "Vector3D"] = Vector3DArray

        def vector_add(a, b):
            # print("a in:")
            # a.show(300, 100)
            # print("b in:")
            # b.show(300, 100)
            return ak.contents.RecordArray(
                [
                    ak.to_layout(a.x + b.x),
                    ak.to_layout(a.y + b.y),
                    ak.to_layout(a.z + b.z),
                ],
                ["x", "y", "z"],
                parameters={"__record__": "Vector3D"},
            )

        def vector_sub(a, b):
            return ak.contents.RecordArray(
                [
                    ak.to_layout(a.x - b.x),
                    ak.to_layout(a.y - b.y),
                    ak.to_layout(a.z - b.z),
                ],
                ["x", "y", "z"],
                parameters={"__record__": "Vector3D"},
            )

        ak.behavior[np.add, "Vector3D", "Vector3D"] = vector_add
        ak.behavior[np.subtract, "Vector3D", "Vector3D"] = vector_sub

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    def update_socket_widgets(self) -> None:
        # Hack to prevent cyclic imports
        add_socket_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "AddSocketCommand")
        remove_socket_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "RemoveSocketCommand")
        remove_edge_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "RemoveEdgeCommand")
        set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")
        execute_dag_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "ExecuteDagCommand")

        last_option_index: int = self._option_box.last_index
        current_option_name: str = self._option_box.currentText()
        current_option_index: int = self._option_box.currentIndex()

        self._undo_stack.beginMacro("Changes option box")
        self._undo_stack.push(execute_dag_cmd_cls(self.scene(), self))

        if current_option_name == "Dot":
            if len(self.input_socket_widgets) == 2:
                if type(self._socket_widgets[1]) != VectorNoneAk:
                    remove_socket: SocketWidget = self._socket_widgets[1]
                    for edge in remove_socket.pin.edges:
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
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

            if len(self.input_socket_widgets) == 2 and type(self._socket_widgets[2]) != VectorNoneAk:
                remove_socket: SocketWidget = self._socket_widgets[2]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
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
                if type(self._socket_widgets[1]) != VectorNoneAk:
                    remove_socket: SocketWidget = self._socket_widgets[1]
                    for edge in remove_socket.pin.edges:
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
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
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
                self._undo_stack.push(remove_socket_cmd_cls(self, 2))

                new_socket_widget: VectorNoneAk = VectorNoneAk(
                    undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
                    parent_node=self
                )
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, 2))

        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )
        self._undo_stack.push(execute_dag_cmd_cls(self.scene(), self, on_redo=True))
        self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> ak.Array:
        result: ak.Array = ak.Array([{"x": 0., "y": 0., "z": 0.}], with_name="Vector3D")

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    a: ak.Array = ak.Array(self.input_data(0, args), with_name="Vector3D")

                    if len(args) == 1:
                        if self._option_box.currentText() == "Length":
                            result: ak.Array = a.vector_length()

                    if len(args) == 2:
                        if self._option_box.currentText() in ("Add", "Sub", "Mul", "Div", "Cross", "Dot", ):
                            b: ak.Array = ak.Array(self.input_data(1, args),  with_name="Vector3D")

                            if self._option_box.currentText() == "Add":
                                # comps: ak.Array = a.vector_add(b)
                                # result: ak.Array = ak.zip({"x": comps.x, "y": comps.y, "z": comps.z})
                                result: ak.Array = a + b

                            elif self._option_box.currentText() == "Sub":
                                # comps: ak.Array = a.vector_sub(b)
                                # result: ak.Array = ak.zip({"x": comps.x, "y": comps.y, "z": comps.z})
                                result: ak.Array = a - b

                            elif self._option_box.currentText() == "Mul":
                                comps: ak.Array = a.vector_mul(b)
                                result: ak.Array = ak.zip({"x": comps.x, "y": comps.y, "z": comps.z})

                            elif self._option_box.currentText() == "Div":
                                comps: ak.Array = a.vector_div(b)
                                result: ak.Array = ak.zip({"x": comps.x, "y": comps.y, "z": comps.z})

                            elif self._option_box.currentText() == "Cross":
                                comps: ak.Array = a.vector_cross(b)
                                result: ak.Array = ak.zip({"x": comps.x, "y": comps.y, "z": comps.z})

                            elif self._option_box.currentText() == "Dot":
                                result: ak.Array = a.vector_dot(b)

                        elif self._option_box.currentText() == "Scale":
                            b: list = self.input_data(1, args)
                            # print("b", type(self.input_data(1, args)))

                            b_vec: ak.Array = ak.zip({"x": b, "y": b, "z": b})
                            b_vec: ak.Array = ak.Array(b_vec)

                            comps: ak.Array = a.vector_mul(b_vec)
                            result: ak.Array = ak.zip({"x": comps.x, "y": comps.y, "z": comps.z})

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

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
from typing import TYPE_CHECKING, Any, Optional, Union, cast

import awkward as ak

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from utils import flatten_list, simplify_list, simplify_array, graft_list
from nested_data import NestedData
from property_model import PropertyModel
from pin_item import PinItem

if TYPE_CHECKING:
    from node_item import NodeItem


class SocketWidget(QtWidgets.QWidget):
    def __init__(self, undo_stack: QtWidgets.QUndoStack, name: str = "A", content_value: Any = "<No Input>",
                 is_flatten: bool = False, is_simplify: bool = False, is_graft: bool = False, is_input: bool = True,
                 parent_node: Optional[NodeItem] = None, parent_widget: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent_widget)

        # Persistent data model
        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "Name": name,
                        "Value": content_value,
                        "Flatten": is_flatten,
                        "Simplify": is_simplify,
                        "Graft": is_graft
                        },
            header_left="Socket Property",
            header_right="Value",
            undo_stack=undo_stack
        )
        self._is_input: bool = is_input
        self._link: tuple[str, int] = ("", -1)

        # Non persistent data model
        self._parent_node: Optional[NodeItem] = parent_node

        self._pin_item: PinItem = PinItem(
            pin_type=float,
            color=QtGui.QColor("#00D6A3"),
            socket_widget=self,
            parent_node=parent_node
        )

        # Assets
        self._flatten_img: QtGui.QImage = QtGui.QImage("icon:images_dark-light/down_arrow_light.svg")
        self._flatten_pixmap: QtGui.QPixmap = QtGui.QPixmap(self._flatten_img)
        self._graft_img: QtGui.QImage = QtGui.QImage("icon:images_dark-light/up_arrow_light.svg")
        self._graft_pixmap: QtGui.QPixmap = QtGui.QPixmap(self._graft_img)
        self._simplify_img: QtGui.QImage = QtGui.QImage("icon:images_dark-light/up_arrow_light.svg")
        self._simplify_pixmap: QtGui.QPixmap = QtGui.QPixmap(self._simplify_img)

        # UI
        # Layout
        self._content_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self._content_layout.setMargin(0)
        self._content_layout.setSpacing(0)
        self.setFixedHeight(24)
        self.setLayout(self._content_layout)

        # Socket option icon
        socket_option_icon = QtWidgets.QLabel(self)
        socket_option_icon.setStyleSheet(
            """
            color: #E5E5E5;
            background-color: red;
            min-height: 24px;
            max-height: 24px;
            margin-left: 0px;
            margin-right: 0px;
            margin-top: 0px;
            margin-bottom: 0px;
            padding-left: 10px;
            padding-right: 10px;
            padding-top: 0px;
            padding-bottom: 0px;
            border-top-left-radius: 0px; /*5px;*/
            border-bottom-left-radius: 0px; /*5px;*/
            border-top-right-radius: 0px;
            border-bottom-right-radius: 0px;
            border: 0px
            """
        )
        socket_option_icon.setPixmap(self._flatten_pixmap)

        if self._is_input:
            socket_option_icon.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self._content_layout.addWidget(socket_option_icon)

        # Label
        self._label_widget: QtWidgets.QLabel = QtWidgets.QLabel(self._prop_model.properties["Name"], self)
        self._label_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self._content_layout.addWidget(self._label_widget)

        if not self._is_input:
            socket_option_icon.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self._content_layout.addWidget(socket_option_icon)

        # Input widget placeholder
        self._input_widget: Optional[QtWidgets.QWidget] = None

        # QActions
        self._flatten_action: QtWidgets.QAction = QtWidgets.QAction("Flatten", self)
        self._flatten_action.setCheckable(True)
        self._flatten_action.setChecked(False)
        cast(QtCore.SignalInstance, self._flatten_action.triggered).connect(self.on_socket_action)

        self._simplify_action: QtWidgets.QAction = QtWidgets.QAction("Simplify", self)
        self._simplify_action.setCheckable(True)
        self._simplify_action.setChecked(False)
        cast(QtCore.SignalInstance, self._simplify_action.triggered).connect(self.on_socket_action)

        self._graft_action: QtWidgets.QAction = QtWidgets.QAction("Graft", self)
        self._graft_action.setCheckable(True)
        self._graft_action.setChecked(False)
        cast(QtCore.SignalInstance, self._graft_action.triggered).connect(self.on_socket_action)

        # Listeners
        cast(QtCore.SignalInstance, self._prop_model.dataChanged).connect(lambda: self.update_all())

    @property
    def prop_model(self) -> QtCore.QAbstractTableModel:
        return self._prop_model

    @property
    def name(self) -> str:
        return self._prop_model.properties["Name"]

    @property
    def value(self) -> Any:
        return self._prop_model.properties["Value"]

    @property
    def is_input(self) -> bool:
        return self._is_input

    @is_input.setter
    def is_input(self, value: bool):
        self._is_input: bool = value

    @property
    def link(self) -> tuple[str, int]:
        return self._link

    @link.setter
    def link(self, value: tuple[str, int]) -> None:
        self._link: tuple[str, int] = value

    @property
    def parent_node(self) -> NodeItem:
        return self._parent_node

    @parent_node.setter
    def parent_node(self, value: NodeItem) -> None:
        self._parent_node: NodeItem = value

    @property
    def pin(self) -> PinItem:
        return self._pin_item

    @property
    def input_widget(self) -> QtWidgets.QWidget:
        return self._input_widget

    # --------------- Socket data ---------------

    def socket_actions(self) -> list[QtWidgets.QAction]:
        return [self._flatten_action, self._simplify_action, self._graft_action]

    def socket_options_state(self) -> list[bool]:
        return [action.isChecked() for action in self.socket_actions()]

    def input_data(self) -> list:
        result: list = []
        if self._pin_item.has_edges():
            for edge in self._pin_item.edges:
                pre_node: NodeItem = edge.start_pin.parent_node
                if len(pre_node.sub_scene.nodes) > 0:
                    result.append(pre_node.linked_lowest_socket(edge.start_pin.socket_widget).pin)
                else:
                    result.append(edge.start_pin)
        else:
            linked_highest: SocketWidget = self.parent_node.linked_highest_socket(self)
            if linked_highest != self:
                result.extend(linked_highest.input_data())

        if len(result) == 0:
            result.append(0.)

        return result

    def perform_socket_operation(
            self, input_data: Union[list, NestedData, ak.Array]
    ) -> Union[list, NestedData, ak.Array]:

        if type(input_data) == list:
            if self.socket_options_state()[0]:  # Flatten
                input_data: list = flatten_list(input_data)
            if self.socket_options_state()[1]:  # Simplify
                input_data: list = simplify_list(input_data)
            if self.socket_options_state()[2]:  # Graft
                input_data: list = graft_list(input_data)

        elif type(input_data) == NestedData:
            if self.socket_options_state()[0]:  # Flatten
                input_data: NestedData = NestedData(input_data.data, ak.flatten(input_data.structure, axis=None))
            if self.socket_options_state()[1]:  # Simplify
                input_data: NestedData = NestedData(input_data.data, simplify_array(input_data.structure))
            if self.socket_options_state()[2]:  # Graft
                input_data: NestedData = NestedData(
                    input_data.data, ak.unflatten(input_data.structure, axis=-1, counts=1)
                )

        elif type(input_data) == ak.Array:
            if len(ak.fields(input_data)) == 3:
                if self.socket_options_state()[0]:  # Flatten
                    x: ak.Array = ak.flatten(input_data.x, axis=None)
                    y: ak.Array = ak.flatten(input_data.y, axis=None)
                    z: ak.Array = ak.flatten(input_data.z, axis=None)
                    input_data: ak.Array = ak.zip({"x": x, "y": y, "z": z})

                if self.socket_options_state()[1]:  # Simplify
                    x: ak.Array = simplify_array(input_data.x)
                    y: ak.Array = simplify_array(input_data.y)
                    z: ak.Array = simplify_array(input_data.z)
                    input_data: ak.Array = ak.zip({"x": x, "y": y, "z": z})

                if self.socket_options_state()[2]:  # Graft
                    input_data: ak.Array = ak.unflatten(input_data, axis=-1, counts=1)
            else:
                if self.socket_options_state()[0]:  # Flatten
                    input_data: ak.Array = ak.flatten(input_data, axis=None)

                if self.socket_options_state()[1]:  # Simplify
                    input_data: ak.Array = simplify_array(input_data)

                if self.socket_options_state()[2]:  # Graft
                    input_data: ak.Array = ak.unflatten(input_data, axis=-1, counts=1)

        return input_data

    # --------------- Callbacks ---------------

    def on_socket_action(self) -> None:
        sender: QtWidgets.QAction = self.sender()
        row: int = list(self._prop_model.properties.keys()).index(sender.text())
        self._prop_model.setData(
            self._prop_model.index(row, 1, QtCore.QModelIndex()), sender.isChecked(), 2
        )
        # cast(QtCore.SignalInstance, self.parent_node.scene().dag_changed).emit(self.parent_node, "")

    def update_pin_position(self, is_node_collapsed: bool) -> None:
        if not is_node_collapsed:
            y_pos: float = (self._parent_node.content_y + self.y() + (self.height() - self._pin_item.size) / 2)

            if self._is_input:
                self._pin_item.setPos(-self._pin_item.size / 2, y_pos)
            else:
                self._pin_item.setPos(self._parent_node.boundingRect().width() - self._pin_item.size / 2, y_pos)
            self._pin_item.show()

        else:
            y_pos: float = (self._parent_node.header_height - self._pin_item.size) / 2
            if self._is_input:
                self._pin_item.setPos(-self._pin_item.size / 2, y_pos)
            else:
                self._pin_item.setPos(self._parent_node.boundingRect().width() - self._pin_item.size / 2, y_pos)
            self._pin_item.hide()

    def update_stylesheets(self) -> None:
        if self._is_input:
            self._label_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self._label_widget.setStyleSheet("background-color: transparent")
        else:
            self._label_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self._label_widget.setStyleSheet("background-color: transparent")

    def update_socket_actions(self) -> None:
        self._flatten_action.setChecked(bool(self._prop_model.properties["Flatten"]))
        self._simplify_action.setChecked(bool(self._prop_model.properties["Simplify"]))
        self._graft_action.setChecked(bool(self._prop_model.properties["Graft"]))

    def update_all(self):
        self._label_widget.setText(self.name)
        self.update_stylesheets()
        self.update_socket_actions()

    # --------------- Overwrites ---------------

    def focusNextPrevChild(self, forward: bool) -> bool:
        input_widget: QtWidgets.QWidget = self.focusWidget()

        # if input_widget == QtWidgets.QApplication.focusWidget():
        #     return False

        socket_idx: int = self.parent_node.input_socket_widgets.index(input_widget.parent())
        next_idx: int = 0
        for idx in range(socket_idx + 1, len(self.parent_node.input_socket_widgets)):
            if self.parent_node.input_socket_widgets[idx].input_widget.focusPolicy() == QtCore.Qt.StrongFocus:
                next_idx: int = idx
                break

        self.parent_node.input_socket_widgets[next_idx].setFocus(QtCore.Qt.TabFocusReason)
        return True

    # --------------- Serialization ---------------

    def __getstate__(self) -> dict:
        data_dict: dict = {
            "Class": self.__class__.__name__,
            "Properties": self._prop_model.__getstate__(),
            "Is Input": self._is_input,
            "Link": self._link
        }
        return data_dict

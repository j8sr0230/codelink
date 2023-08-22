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
from typing import TYPE_CHECKING, Any, Optional, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from utils import flatten, simplify, graft, graft_topology, unwrap, wrap
from property_model import PropertyModel
from pin_item import PinItem

if TYPE_CHECKING:
    from node_item import NodeItem


class SocketWidget(QtWidgets.QWidget):
    def __init__(self, undo_stack: QtWidgets.QUndoStack, name: str = "A", content_value: Any = "<No Input>",
                 is_flatten: bool = False, is_simplify: bool = False, is_graft: bool = False,
                 is_graft_topo: bool = False, is_unwrap: bool = False, is_wrap: bool = False, is_input: bool = True,
                 parent_node: Optional[NodeItem] = None, parent_widget: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent_widget)

        # Persistent data model
        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "Name": name,
                        "Value": content_value,
                        "Flatten": is_flatten,
                        "Simplify": is_simplify,
                        "Graft": is_graft,
                        "Graft Topo": is_graft_topo,
                        "Unwrap": is_unwrap,
                        "Wrap": is_wrap
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

        # UI
        # Layout
        self._content_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self._content_layout.setMargin(0)
        self._content_layout.setSpacing(0)
        self.setFixedHeight(24)
        self.setLayout(self._content_layout)

        # Label
        self._label_widget: QtWidgets.QLabel = QtWidgets.QLabel(self._prop_model.properties["Name"], self)
        self._label_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self._content_layout.addWidget(self._label_widget)

        # Input widget placeholder
        self._input_widget: QtWidgets.QLabel = QtWidgets.QLabel("", self)
        self._input_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self._content_layout.addWidget(self._input_widget)
        self._input_widget.hide()

        self.update_stylesheets()

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

        self._graft_topo_action: QtWidgets.QAction = QtWidgets.QAction("Graft Topo", self)
        self._graft_topo_action.setCheckable(True)
        self._graft_topo_action.setChecked(False)
        cast(QtCore.SignalInstance, self._graft_topo_action.triggered).connect(self.on_socket_action)

        self._unwrap_action: QtWidgets.QAction = QtWidgets.QAction("Unwrap", self)
        self._unwrap_action.setCheckable(True)
        self._unwrap_action.setChecked(False)
        cast(QtCore.SignalInstance, self._unwrap_action.triggered).connect(self.on_socket_action)

        self._wrap_action: QtWidgets.QAction = QtWidgets.QAction("Wrap", self)
        self._wrap_action.setCheckable(True)
        self._wrap_action.setChecked(False)
        cast(QtCore.SignalInstance, self._wrap_action.triggered).connect(self.on_socket_action)

        # Listeners
        cast(QtCore.SignalInstance, self._prop_model.dataChanged).connect(lambda: self.update_all())

    @property
    def prop_model(self) -> QtCore.QAbstractTableModel:
        return self._prop_model

    @property
    def link(self) -> tuple[str, int]:
        return self._link

    @link.setter
    def link(self, value: tuple[str, int]) -> None:
        self._link: tuple[str, int] = value

    @property
    def is_input(self) -> bool:
        return self._is_input

    @is_input.setter
    def is_input(self, value: bool):
        self._is_input: bool = value

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
        return [self._flatten_action, self._simplify_action, self._graft_action, self._graft_topo_action,
                self._unwrap_action,  self._wrap_action]

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

    def perform_socket_operation(self, input_data: list) -> list:
        if self.socket_options_state()[0]:  # Flatten
            input_data: list = list(flatten(input_data))
        if self.socket_options_state()[1]:  # Simplify
            input_data: list = list(simplify(input_data))
        if self.socket_options_state()[2]:  # Graft
            input_data: list = list(graft(input_data))
        if self.socket_options_state()[3]:  # Graft Topo
            input_data: list = list(graft_topology(input_data))
        if self.socket_options_state()[4]:  # Unwrap
            input_data: list = list(unwrap(input_data))
        if self.socket_options_state()[5]:  # Wrap
            input_data: list = list(wrap(input_data))
        return input_data

    # --------------- Callbacks ---------------

    def on_socket_action(self) -> None:
        sender: QtWidgets.QAction = self.sender()
        row: int = list(self._prop_model.properties.keys()).index(sender.text())
        self._prop_model.setData(
            self._prop_model.index(row, 1, QtCore.QModelIndex()), sender.isChecked(), 2
        )

    def update_pin_position(self) -> None:
        if not self._parent_node.is_collapsed:
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
        self._graft_topo_action.setChecked(bool(self._prop_model.properties["Graft Topo"]))
        self._unwrap_action.setChecked(bool(self._prop_model.properties["Unwrap"]))
        self._wrap_action.setChecked(bool(self._prop_model.properties["Wrap"]))

    def update_all(self):
        self._label_widget.setText(self._prop_model.properties["Name"])
        self.update_pin_position()
        self.update_stylesheets()
        self.update_socket_actions()
        self.parent_node.update_details(self._parent_node.zoom_level)

    # --------------- Overwrites ---------------

    def focusNextPrevChild(self, forward: bool) -> bool:
        input_widget: QtWidgets.QWidget = self.focusWidget()

        if input_widget == QtWidgets.QApplication.focusWidget():
            return False

        socket_idx: int = self.parent_node.input_socket_widgets.index(input_widget.parent())
        next_idx: int = 0
        for idx in range(socket_idx + 1, len(self.parent_node.input_socket_widgets)):
            if self.parent_node.input_socket_widgets[idx].input_widget.focusPolicy() == QtCore.Qt.StrongFocus:
                next_idx: int = idx
                break

        self.parent_node.input_socket_widgets[next_idx].input_widget.setFocus(QtCore.Qt.TabFocusReason)
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

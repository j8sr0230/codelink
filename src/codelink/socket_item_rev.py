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

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from utils import flatten, simplify, graft, graft_topology, unwrap, wrap
from property_model import PropertyModel

if TYPE_CHECKING:
    from node_item_rev import NodeItemRev
    from edge_item import EdgeItem


class SocketItemRev(QtWidgets.QGraphicsItem):
    def __init__(self, undo_stack: QtWidgets.QUndoStack, name: str = "A", value: Union[bool, float, str] = 0.,
                 link: tuple[str, int] = ("", -1), is_flatten: bool = False, is_simplify: bool = False,
                 is_graft: bool = False, is_graft_topo: bool = False, is_unwrap: bool = False,
                 is_wrap: bool = False, input_widget: Optional[QtWidgets.QWidget] = None,
                 parent_node: Optional[NodeItemRev] = None) -> None:
        super().__init__(parent_node)

        # Persistent data model
        self._prop_model: PropertyModel = PropertyModel(
            properties={
                "Name": name,
                "Value": value,
                "Link": link,
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

        # Non persistent data model
        self._pin_type: type = float
        self._edges: list[EdgeItem] = []

        # Geometry
        self._size: int = 10

        # Assets
        self._color: QtGui.QColor = QtGui.QColor("red")
        self._border_pen: QtGui.QPen = QtGui.QPen(QtGui.QColor("black"))
        self._background_brush: QtGui.QBrush = QtGui.QBrush(self._color)

        # UI
        # Container and layout
        self._content: QtWidgets.QWidget = QtWidgets.QWidget()
        self._content.setFixedHeight(24)
        self._content_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self._content_layout.setMargin(0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)

        # Label
        self._label_widget: QtWidgets.QLabel = QtWidgets.QLabel(self._prop_model.properties["Name"], self)
        self._label_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self._content_layout.addWidget(self._label_widget)

        # Input widget
        self._input_widget: Optional[QtWidgets.QWidget] = input_widget
        if input_widget is not None:
            self._input_widget.setMinimumWidth(5)
            self._input_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self._input_widget.set_input_data(self._prop_model.properties["Value"])
            self._input_widget.setFocusPolicy(QtCore.Qt.StrongFocus)
            self._content_layout.addWidget(self._input_widget)
            self._content.setFocusProxy(self._input_widget)

        # Socket option actions
        self._flatten_action: QtWidgets.QAction = QtWidgets.QAction("Flatten", self)
        self._flatten_action.setCheckable(True)
        self._flatten_action.setChecked(self._prop_model.properties["Flatten"])
        self._flatten_action.triggered.connect(self.on_socket_action)

        self._simplify_action: QtWidgets.QAction = QtWidgets.QAction("Simplify", self)
        self._simplify_action.setCheckable(True)
        self._simplify_action.setChecked(self._prop_model.properties["Simplify"])
        self._simplify_action.triggered.connect(self.on_socket_action)

        self._graft_action: QtWidgets.QAction = QtWidgets.QAction("Graft", self)
        self._graft_action.setCheckable(True)
        self._graft_action.setChecked(self._prop_model.properties["Graft"])
        self._graft_action.triggered.connect(self.on_socket_action)

        self._graft_topo_action: QtWidgets.QAction = QtWidgets.QAction("Graft Topo", self)
        self._graft_topo_action.setCheckable(True)
        self._graft_topo_action.setChecked(self._prop_model.properties["Graft Topo"])
        self._graft_topo_action.triggered.connect(self.on_socket_action)

        self._unwrap_action: QtWidgets.QAction = QtWidgets.QAction("Unwrap", self)
        self._unwrap_action.setCheckable(True)
        self._unwrap_action.setChecked(self._prop_model.properties["Unwrap"])
        self._unwrap_action.triggered.connect(self.on_socket_action)

        self._wrap_action: QtWidgets.QAction = QtWidgets.QAction("Wrap", self)
        self._wrap_action.setCheckable(True)
        self._wrap_action.setChecked(self._prop_model.properties["Wrap"])
        self._wrap_action.triggered.connect(self.on_socket_action)

        # Widget setup
        self.setAcceptHoverEvents(True)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

        # Listeners
        self._prop_model.dataChanged.connect(lambda: self.update_all())
        if self._input_widget is not None:
            self._input_widget.editingFinished.connect(self.on_editing_finished)

    @property
    def prop_model(self) -> QtCore.QAbstractTableModel:
        return self._prop_model

    @property
    def name(self) -> str:
        return self._prop_model.properties["Name"]

    @property
    def value(self) -> Union[bool, float, str]:
        return self._prop_model.properties["Value"]

    @property
    def link(self) -> tuple[str, int]:
        return self._prop_model.properties["Link"]

    @property
    def pin_type(self) -> type:
        return self._pin_type

    @property
    def edges(self) -> list[EdgeItem]:
        return self._edges

    @property
    def color(self) -> QtGui.QColor:
        return self._color

    @property
    def content(self) -> QtWidgets.QWidget:
        return self._content

    @property
    def uuid(self) -> tuple[str, int]:
        if self.parentItem() is not None and isinstance(self.parentItem(), NodeItemRev):
            parent_node: NodeItemRev = cast(self.parentItem(), NodeItemRev)
            return parent_node.uuid, parent_node.socket_widgets.index(self)
        else:
            return "", -1

    # --------------- Edge editing ---------------

    def add_edge(self, edge: EdgeItem) -> None:
        if edge not in self._edges:
            self._edges.append(edge)

    def remove_edge(self, edge: EdgeItem) -> None:
        if edge in self._edges:
            self._edges.remove(edge)

    def has_edges(self) -> bool:
        return len(self._edges) > 0

    # --------------- Socket data ---------------

    def input_data(self) -> list:
        result: list = []
        if self.has_edges():
            for edge in self.edges:
                pre_node: NodeItemRev = edge.start_pin.parent_node
                if len(pre_node.sub_scene.nodes) > 0:
                    result.append(pre_node.linked_lowest_socket(edge.start_pin.socket_widget).pin)
                else:
                    result.append(edge.start_pin)
        else:
            linked_highest: SocketItemRev = self.parent_node.linked_highest_socket(self)
            if linked_highest != self:
                result.extend(linked_highest.input_data())

        if len(result) == 0:
            if self._input_widget is not None:
                result.append(self._input_widget.input_data())
            else:
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

    # --------------- Events ---------------

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverEnterEvent(event)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverLeaveEvent(event)
        QtWidgets.QApplication.restoreOverrideCursor()

    # --------------- Slots and callbacks ---------------

    def on_editing_finished(self) -> None:
        value: Union[bool, float, str] = self._input_widget.input_data()
        self._prop_model.setData(self._prop_model.index(2, 1, QtCore.QModelIndex()), value, 2)
        self.clearFocus()

    def on_socket_action(self) -> None:
        sender: QtWidgets.QAction = self.sender()
        row: int = list(self._prop_model.properties.keys()).index(sender.text())
        self._prop_model.setData(self._prop_model.index(row, 1, QtCore.QModelIndex()), sender.isChecked(), 2)

    def update_stylesheet(self) -> None:
        if self.has_edges() or self.link != ("", -1):
            self._label_widget.setStyleSheet("background-color: transparent")
            self._input_widget.hide()
            self._input_widget.setFocusPolicy(QtCore.Qt.NoFocus)
        else:
            self._label_widget.setStyleSheet("background-color: #545454")
            self._input_widget.show()
            self._input_widget.setFocusPolicy(QtCore.Qt.StrongFocus)

    def update_socket_actions(self) -> None:
        self._flatten_action.setChecked(self._prop_model.properties["Flatten"])
        self._simplify_action.setChecked(self._prop_model.properties["Simplify"])
        self._graft_action.setChecked(self._prop_model.properties["Graft"])
        self._graft_topo_action.setChecked(self._prop_model.properties["Graft Topo"])
        self._unwrap_action.setChecked(self._prop_model.properties["Unwrap"])
        self._wrap_action.setChecked(self._prop_model.properties["Wrap"])

    def update_all(self):
        self.update_stylesheet()
        self._label_widget.setText(self._prop_model.properties["Name"])
        self.update_socket_actions()

    # --------------- Shape and painting ---------------

    def center(self) -> QtCore.QPointF:
        return QtCore.QPointF(self.x() + self._size / 2, self.y() + self._size / 2)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(-self._size, -self._size, 3 * self._size, 3 * self._size)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(self._border_pen)
        painter.setBrush(self._background_brush)

        painter.drawRect(0, 0, self._size, self._size)

    # --------------- Serialization ---------------

    def __getstate__(self) -> dict:
        state: dict = {
            "Class": self.__class__.__name__,
            "Properties": self._prop_model.__getstate__()
        }
        return state

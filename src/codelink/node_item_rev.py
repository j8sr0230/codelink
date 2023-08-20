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
import sys
import importlib
import warnings

import awkward as ak

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from app_style import NODE_STYLE
from utils import crop_text, unwrap
from property_model import PropertyModel
from frame_item import FrameItem
from sockets import *

if TYPE_CHECKING:
    from socket_item_rev import SocketItemRev


class NodeItemRev(QtWidgets.QGraphicsItem):
    REG_NAME: str = "Node Item"

    def __init__(self, undo_stack: QtWidgets.QUndoStack, uuid: str = QtCore.QUuid.createUuid().toString(),
                 x: float = 0., y: float = 0., width: float = 160,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        # Persistent data model
        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "UUID": uuid,
                        "Name": "Node Item",
                        "Color": "#1D1D1D",
                        "Collapsed": False,
                        "X": x,
                        "Y": y,
                        "Width": width
                        },
            header_left="Node Property",
            header_right="Value",
            undo_stack=undo_stack
        )

        # Non persistent data model
        self._undo_stack: QtWidgets.QUndoStack = undo_stack

        self._inputs: list[SocketItemRev] = []
        self._outputs: list[SocketItemRev] = []
        self._evals: list[object] = [self.eval_socket_0]

        self._parent_frame: Optional[FrameItem] = None
        dag_scene_cls: type = getattr(importlib.import_module("dag_scene"), "DAGScene")  # Hack: Prevents cyclic import
        self._sub_scene: dag_scene_cls = dag_scene_cls(self._undo_stack)
        self._sub_scene.background_color = QtGui.QColor("#383838")
        self._sub_scene.parent_node = self

        self._mode: str = ""
        self._lm_pressed: bool = False
        self._moved: bool = False
        self._resized: bool = False
        self._last_position: QtCore.QPointF = QtCore.QPointF(x, y)
        self._last_width: int = 0
        self._zoom_level: Optional[int] = None
        self._is_dirty: bool = False

        # Node geometry
        self._title_left_padding: int = 20
        self._min_width: int = 80
        self._height: int = 0
        self._header_height: int = 25
        self._min_height: int = self._header_height
        self._content_padding: int = 8
        self._content_y: int = self._header_height + self._content_padding

        # Assets
        self._node_background_color: QtGui.QColor = QtGui.QColor("#303030")
        self._default_border_color: QtGui.QColor = QtGui.QColor("black")
        self._dirty_border_color: QtGui.QColor = QtGui.QColor("red")
        self._selected_border_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._font_color: QtGui.QColor = QtGui.QColor("#E5E5E5")

        self._default_border_pen: QtGui.QPen = QtGui.QPen(self._default_border_color)
        self._dirty_pen: QtGui.QPen = QtGui.QPen(self._dirty_border_color)
        self._selected_border_pen: QtGui.QPen = QtGui.QPen(self._selected_border_color)
        self._selected_border_pen.setWidthF(1.5)

        self._header_font: QtGui.QFont = QtGui.QFont()

        self._collapse_img_down: QtGui.QImage = QtGui.QImage("icon:images_dark-light/down_arrow_light.svg")
        self._collapse_pixmap_down: QtGui.QPixmap = QtGui.QPixmap(self._collapse_img_down)
        self._collapse_img_up: QtGui.QImage = QtGui.QImage("icon:images_dark-light/up_arrow_light.svg")
        self._collapse_pixmap_up: QtGui.QPixmap = QtGui.QPixmap(self._collapse_img_up)

        # UI
        # Collapse button
        self._collapse_btn: QtWidgets.QGraphicsPixmapItem = QtWidgets.QGraphicsPixmapItem()
        self._collapse_btn.setParentItem(self)
        self._collapse_btn.setPixmap(self._collapse_pixmap_down)
        btn_x = ((self._title_left_padding + self._collapse_btn.boundingRect().width() / 2) -
                 self._collapse_btn.boundingRect().width()) / 2
        self._collapse_btn.setPos(btn_x, (self._header_height - self._collapse_btn.boundingRect().height()) / 2)

        # Node name
        self._name_item = QtWidgets.QGraphicsTextItem(self)
        self._name_item.setDefaultTextColor(self._font_color)
        self._name_item.setFont(self._header_font)
        self._name_item.setPlainText(
            crop_text(self._prop_model.properties["Name"],
                      self._prop_model.properties["Width"] - self._title_left_padding - self._content_padding,
                      self._header_font)
        )
        self._name_item.setPos(self._title_left_padding,
                               (self._header_height - self._name_item.boundingRect().height()) / 2
                               )

        # Node content container
        self._content_widget: QtWidgets.QWidget = QtWidgets.QWidget()
        self._content_widget.setStyleSheet(NODE_STYLE)
        self._content_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        self._content_layout.setMargin(0)
        self._content_layout.setSpacing(5)
        self._content_widget.setLayout(self._content_layout)

        # Hack for setting node_item font to qss font defined in app_style.py -> NODE_STYLE -> QWidget
        self._content_widget.style().unpolish(self._content_widget)  # Unload qss
        self._content_widget.style().polish(self._content_widget)  # Reload qss
        self._content_widget.update()
        self._header_font: QtGui.QFont = self._content_widget.font()
        self._name_item.setFont(self._header_font)
        self._name_item.setPos(self._title_left_padding,
                               (self._header_height - self._name_item.boundingRect().height()) / 2
                               )

        self._content_proxy: QtWidgets.QGraphicsProxyWidget = QtWidgets.QGraphicsProxyWidget(self)
        self._content_proxy.setWidget(self._content_widget)

        self.update_all()

        # Widget setup
        self.setPos(QtCore.QPointF(x, y))
        self.setZValue(2)
        self.setAcceptHoverEvents(True)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

        # Listeners
        cast(QtCore.SignalInstance, self._prop_model.dataChanged).connect(lambda: self.update_all())

    @property
    def prop_model(self) -> PropertyModel:
        return self._prop_model

    @property
    def uuid(self) -> str:
        return self._prop_model.properties["UUID"]

    @property
    def name(self) -> str:
        return self._prop_model.properties["Name"]

    @property
    def collapsed(self) -> str:
        return self._prop_model.properties["Collapsed"]

    @property
    def inputs(self) -> list[SocketItemRev]:
        return self._inputs

    @property
    def outputs(self) -> list[SocketItemRev]:
        return self._outputs

    @property
    def evals(self) -> list[object]:
        return self._evals

    @property
    def parent_frame(self) -> FrameItem:
        return self._parent_frame

    @parent_frame.setter
    def parent_frame(self, value: FrameItem) -> None:
        self._parent_frame: FrameItem = value

    @property
    def sub_scene(self) -> Any:
        return self._sub_scene

    @sub_scene.setter
    def sub_scene(self, value: Any) -> None:
        self._sub_scene: Any = value

    @property
    def header_height(self) -> int:
        return self._header_height

    @property
    def content_y(self) -> float:
        return self._content_y

    @property
    def content_widget(self) -> QtWidgets.QWidget:
        return self._content_widget

    @property
    def content_layout(self) -> QtWidgets.QLayout:
        return self._content_layout

    @property
    def moved(self) -> bool:
        return self._moved

    @moved.setter
    def moved(self, value: bool) -> None:
        self._moved: bool = value

    @property
    def last_position(self) -> QtCore.QPointF:
        return self._last_position

    @last_position.setter
    def last_position(self, value: QtCore.QPointF) -> None:
        self._last_position: QtCore.QPointF = value

    @property
    def last_width(self) -> int:
        return self._last_width

    @property
    def zoom_level(self) -> int:
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, value: int) -> None:
        self._zoom_level: int = value

    # --------------- Socket widget editing ---------------

    def append_socket(self, socket: SocketItemRev, is_input: bool = False) -> None:
        socket.setParentItem(self)
        layout_offset: int = len(
            [child for child in self._content_widget.children() if not isinstance(child, SocketItemRev)]
        ) - 1

        self._content_widget.hide()
        if is_input:
            self._inputs.append(socket)
            self._content_layout.insertWidget(len(self._inputs) + layout_offset, socket)
        else:
            self._outputs.append(socket)
            self._content_layout.insertWidget(len(self._inputs) + len(self._outputs) + layout_offset, socket)

        self._content_widget.show()
        self.update_all()

    def remove_socket(self, remove_idx: int = 0, is_input: bool = False) -> None:
        self._content_widget.hide()

        if is_input:
            if 0 <= remove_idx < len(self._inputs):
                socket: SocketItemRev = self._inputs[remove_idx]
                socket_content: QtWidgets.QWidget = socket.content
                socket_content.setParent(None)
                self._content_layout.removeWidget(socket_content)
                self.scene().removeItem(socket)
                self._inputs.remove(socket)

        if not is_input:
            if 0 <= remove_idx < len(self._outputs):
                socket: SocketItemRev = self._outputs[remove_idx]
                socket_content: QtWidgets.QWidget = socket.content
                socket_content.setParent(None)
                self._content_layout.removeWidget(socket_content)
                self.scene().removeItem(socket)
                self._inputs.remove(socket)

            self._content_widget.show()
            self.update_all()

    def clear_sockets(self):
        while len(self._inputs) > 0:
            self.remove_socket(0, is_input=True)
        while len(self._outputs) > 0:
            self.remove_socket(0, is_input=False)

    def remove_from_frame(self):
        if self.parent_frame is not None:
            self.parent_frame.framed_nodes.remove(self)
            self.parent_frame.update()
            self._parent_frame: Optional[FrameItem] = None

    def on_remove(self):
        pass

    # --------------- DAG analytics ---------------

    def has_in_edges(self) -> bool:
        for socket in self._inputs:
            if socket.has_edges():
                return True
        return False

    def has_out_edges(self) -> bool:
        for socket in self._outputs:
            if socket.has_edges():
                return True
        return False

    def linked_lowest_socket(self, socket: SocketItemRev) -> Optional[SocketItemRev]:
        if len(self._sub_scene.nodes) > 0:
            linked_node: NodeItemRev = self.sub_scene.dag_item(socket.link[0])
            linked_socket: SocketItemRev = linked_node._inputs[socket.link[1]]
            return linked_node.linked_lowest_socket(linked_socket)
        else:
            return socket

    def linked_highest_socket(self, socket: SocketItemRev) -> Optional[SocketItemRev]:
        if self.scene().parent_node is not None and socket.link[0] == self.scene().parent_node.uuid:
            linked_node: NodeItemRev = self.scene().parent_node
            linked_socket: SocketItemRev = linked_node._outputs[socket.link[1]]
            return self.scene().parent_node.linked_highest_socket(linked_socket)
        else:
            return socket

    def predecessors(self) -> list[NodeItemRev]:
        result: list[NodeItemRev] = []
        if not self.has_sub_scene():
            for socket in self._inputs:
                if socket.has_edges():
                    for edge in socket.edges:
                        pre_node: NodeItemRev = edge.start_pin.parent_node
                        if pre_node.has_sub_scene():
                            linked_lowest: SocketItemRev = pre_node.linked_lowest_socket(edge.start_pin)
                            result.append(linked_lowest.parentItem())
                        else:
                            result.append(edge.start_pin.parentItem())

                else:
                    linked_highest: SocketItemRev = self.linked_highest_socket(socket)
                    if linked_highest != socket:
                        for edge in linked_highest.edges:
                            start_socket: SocketItemRev = edge.start_pin
                            linked_lowest: SocketItemRev = start_socket.partenItem().linked_lowest_socket(start_socket)
                            result.append(linked_lowest.parentItem())
        else:
            for socket in self._outputs:
                result.append(self.linked_lowest_socket(socket.parentItem()))

        return result

    def has_sub_scene(self) -> bool:
        return len(self._sub_scene.nodes) > 0

    def is_grp_interface(self) -> bool:
        has_links: bool = any([True for socket in self._inputs + self._outputs if socket.link != ("", -1)])
        if not self.has_sub_scene() and has_links:
            return True
        return False

    # --------------- Node eval methods ---------------

    def input_data(self, input_index: int, args) -> list:
        socket_data: list = []
        if 0 <= input_index < len(self._inputs):
            if type(unwrap(args[input_index])) == list:
                socket_data: list = list(unwrap(args[input_index]))
            else:
                socket_data: list = args[input_index]

            socket_data: list = self._inputs[input_index].perform_socket_operation(socket_data)
        return socket_data

    def output_data(self, output_index: int, args) -> list:
        socket_data: list = self._outputs[output_index].perform_socket_operation(args)
        return socket_data

    def eval_socket_0(self, *args) -> list:
        result: list = [0]
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    a: list = self.input_data(0, args)
                    b: list = self.input_data(1, args)
                    result: ak.Array = ak.Array(a) + ak.Array(b)
                    self._is_dirty: bool = False
                    result: list = result.to_list()

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

    def eval_socket_1(self, *args) -> list:
        result: list = [0]
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    a: list = self.input_data(0, args)
                    b: list = self.input_data(1, args)
                    result: ak.Array = ak.Array(a) - ak.Array(b)
                    self._is_dirty: bool = False
                    result: list = result.to_list()

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

    # --------------- Overwrites ---------------

    def scene(self) -> Any:
        return super().scene()

    def itemChange(self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            if not self._moved and self._lm_pressed:
                self._last_position: QtCore.QPointF = value
                self._moved: bool = True

            new_pos: QtCore.QPointF = value

            # snapping_step: int = 10
            x_snap = new_pos.x()  # // snapping_step * snapping_step
            y_snap = new_pos.y()  # // snapping_step * snapping_step

            x_mode_row: int = list(self._prop_model.properties.keys()).index("X")
            y_mode_row: int = list(self._prop_model.properties.keys()).index("Y")

            self._prop_model.setData(self._prop_model.index(x_mode_row, 1, QtCore.QModelIndex()), int(x_snap), 2)
            self._prop_model.setData(self._prop_model.index(y_mode_row, 1, QtCore.QModelIndex()), int(y_snap), 2)

            return QtCore.QPointF(x_snap, y_snap)
        else:
            return super().itemChange(change, value)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)

        self.setZValue(3)

        if event.button() == QtCore.Qt.LeftButton:
            self._lm_pressed: bool = True

            if self.boundingRect().width() - 5 < event.pos().x() < self.boundingRect().width():
                self._mode: str = "RESIZE"
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeHorCursor)

            collapse_btn_left: float = 0
            collapse_btn_right: float = self._title_left_padding
            collapse_btn_top: float = 0
            collapse_btn_bottom: float = self._header_height

            if collapse_btn_left <= event.pos().x() <= collapse_btn_right:
                if collapse_btn_top <= event.pos().y() <= collapse_btn_bottom:
                    collapse_row: int = list(self._prop_model.properties.keys()).index("Collapse State")
                    self._prop_model.setData(
                        self._prop_model.index(collapse_row, 1, QtCore.QModelIndex()), not self.is_collapsed, 2
                    )

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self._mode == "RESIZE":
            if not self._resized and self._lm_pressed:
                self._last_width: int = self.prop_model.properties["Width"]
                self._resized: bool = True

            old_x_left: float = self.boundingRect().x()
            old_y_top: float = self.boundingRect().y()

            old_top_left_local: QtCore.QPointF = QtCore.QPointF(old_x_left, old_y_top)
            old_top_left_global: QtCore.QPointF = self.mapToScene(old_top_left_local)

            current_x: int = self.mapToScene(event.pos()).x()
            new_width: float = current_x - old_top_left_global.x()

            width_row: int = list(self._prop_model.properties.keys()).index("Width")
            self._prop_model.setData(self._prop_model.index(width_row, 1, QtCore.QModelIndex()), new_width, 2)

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        self.setZValue(2)

        intersection_items: list = self.scene().collidingItems(self)
        for item in intersection_items:
            if type(item) == self.__class__:
                item.stackBefore(self)

        self._mode = ""
        self._lm_pressed: bool = False
        QtWidgets.QApplication.restoreOverrideCursor()

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverEnterEvent(event)
        # print("Node UUID:", self._uuid)

    def hoverMoveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverMoveEvent(event)

        if self.boundingRect().width() - 5 < event.pos().x() < self.boundingRect().width():
            if QtWidgets.QApplication.overrideCursor() != QtCore.Qt.SizeHorCursor:
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeHorCursor)
        else:
            QtWidgets.QApplication.restoreOverrideCursor()

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverLeaveEvent(event)
        QtWidgets.QApplication.restoreOverrideCursor()

    # --------------- Callbacks ---------------

    def update_name(self, value: str) -> None:
        self._name_item.setPlainText(
            crop_text(value,
                      self._prop_model.properties["Width"] - self._title_left_padding - self._content_padding,
                      self._header_font)
        )

    def update_width(self, new_width: int = 160) -> None:
        if new_width < self._min_width:
            new_width: float = self._min_width

        self._prop_model.properties["Width"] = new_width
        content_rect: QtCore.QRectF = QtCore.QRectF(
            self._content_padding,
            self._header_height + self._content_padding,
            self._prop_model.properties["Width"] - 2 * self._content_padding,
            self._content_widget.height()
        )
        self._content_proxy.setGeometry(content_rect)
        self.update_name(self._prop_model.properties["Name"])
        self.update_pin_positions()

    def update_height(self):
        # Reset content proxy
        content_proxy_height: int = 0
        self._content_proxy.hide()
        self._collapse_btn.setPixmap(self._collapse_pixmap_up)

        # Calculate and set new fixed content widget height
        if not self.is_collapsed:
            for widget in self._content_widget.children():
                if hasattr(widget, "height"):
                    content_proxy_height += widget.height()
            content_proxy_height += (self._content_layout.count() - 1) * self._content_layout.spacing()
            self._content_proxy.show()
            self._collapse_btn.setPixmap(self._collapse_pixmap_down)

        content_rect: QtCore.QRectF = QtCore.QRectF(
            self._content_padding,
            self._header_height + self._content_padding,
            self._prop_model.properties["Width"] - 2 * self._content_padding,
            content_proxy_height
        )

        # Update node height, content proxy height and pin positions
        self._content_proxy.setGeometry(content_rect)
        self._height = self._header_height + 2 * self._content_padding + content_proxy_height
        self.update_pin_positions()

    def update_pin_positions(self) -> None:
        for widget in self._socket_widgets:
            widget.update_pin_position()

    def update_details(self, zoom_level: int) -> None:
        self._zoom_level = zoom_level

        if self._zoom_level < 8:
            # self.setEnabled(False)
            self.content_widget.hide()
            for socket_widget in self._socket_widgets:
                socket_widget.pin.hide()
        else:
            # self.setEnabled(True)
            if not self.is_collapsed:
                self.content_widget.show()
                for socket_widget in self._socket_widgets:
                    socket_widget.pin.show()

    def update_all(self):
        self.update_name(self._prop_model.properties["Name"])
        self.update_width(self._prop_model.properties["Width"])
        self.update_height()
        if self._zoom_level is not None:
            self.update_details(self._zoom_level)

        # Hack to prevent callback loop while changing the node position
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setPos(QtCore.QPointF(self._prop_model.properties["X"], self._prop_model.properties["Y"]))
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

    # --------------- Shape and painting ---------------

    def center(self) -> QtCore.QPointF:
        return QtCore.QPointF(self.x() + self.boundingRect().width() / 2, self.y() + self.boundingRect().height() / 2)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._prop_model.properties["Width"], self._height)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._node_background_color)
        # painter.drawRoundedRect(self.boundingRect(), self._corner_radius, self._corner_radius)
        painter.drawRect(self.boundingRect())

        rect: QtCore.QRectF = QtCore.QRectF(0, 0, self._prop_model.properties["Width"], self._header_height)
        painter.setBrush(QtGui.QColor(self._prop_model.properties["Color"]))
        # painter.drawRoundedRect(rect, self._corner_radius, self._corner_radius)
        painter.drawRect(rect)

        painter.setBrush(QtCore.Qt.NoBrush)
        if self.isSelected():
            painter.setPen(self._selected_border_pen)
        elif self._is_dirty:
            painter.setPen(self._dirty_border_color)
        else:
            painter.setPen(self._default_border_pen)
        # painter.drawRoundedRect(self.boundingRect(), self._corner_radius, self._corner_radius)
        painter.drawRect(self.boundingRect())

    # --------------- Serialization ---------------

    def __getstate__(self) -> dict:
        data_dict: dict = {
            "Class": self.__class__.__name__,
            "UUID": self._uuid,
            "Properties": self.prop_model.__getstate__()  # ,
        }

        sockets_list: list[dict] = []
        for idx, socket_widget in enumerate(self._socket_widgets):
            sockets_list.append(socket_widget.__getstate__())
        data_dict["Sockets"] = sockets_list

        data_dict["Subgraph"] = self.sub_scene.serialize()

        return data_dict

    def __setstate__(self, state: dict):
        self._uuid = state["UUID"]
        self.prop_model.__setstate__(state["Properties"])

        # Add socket widgets from state
        self.clear_socket_widgets()
        for i in range(len(state["Sockets"])):
            socket_widget_dict: dict = state["Sockets"][i]
            socket_widget_cls: type = getattr(sys.modules[__name__], socket_widget_dict["Class"])
            new_socket_widget: socket_widget_cls = socket_widget_cls(
                undo_stack=self._undo_stack,
                label=socket_widget_dict["Properties"]["Name"],
                is_input=socket_widget_dict["Properties"]["Is Input"],
                data=socket_widget_dict["Properties"]["Data"],
                parent_node=self
            )
            new_socket_widget.prop_model.properties["Flatten"] = socket_widget_dict["Properties"]["Flatten"]
            new_socket_widget.prop_model.properties["Simplify"] = socket_widget_dict["Properties"]["Simplify"]
            new_socket_widget.prop_model.properties["Graft"] = socket_widget_dict["Properties"]["Graft"]
            new_socket_widget.prop_model.properties["Graft Topo"] = socket_widget_dict["Properties"]["Graft Topo"]
            new_socket_widget.prop_model.properties["Unwrap"] = socket_widget_dict["Properties"]["Unwrap"]
            new_socket_widget.prop_model.properties["Wrap"] = socket_widget_dict["Properties"]["Wrap"]
            new_socket_widget.link = tuple(socket_widget_dict["Link"])
            self.insert_socket_widget(new_socket_widget, i)

            new_socket_widget.update_all()

        # Reset sub graph data
        self.sub_scene.deserialize(state["Subgraph"])

        if self.has_sub_scene():
            # If custom node with sub scene
            for sub_node in self.sub_scene.nodes:
                sub_node.scene().parent_node = self

        self.update()

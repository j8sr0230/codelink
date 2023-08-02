from __future__ import annotations
from typing import Optional, Union, cast
import sys
import importlib

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from app_style import NODE_STYLE
from utils import crop_text
from property_model import PropertyModel
from frame_item import FrameItem
from sockets import *
from socket_widget import SocketWidget
from pin_item import PinItem
from edge_item import EdgeItem


class NodeItem(QtWidgets.QGraphicsItem):
    REG_NAME: str = "Node Item"

    def __init__(self, undo_stack: QtWidgets.QUndoStack, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        # Persistent data model
        self._uuid: str = QtCore.QUuid.createUuid().toString()
        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "Name": "Node Item",
                        "Color": "#1D1D1D",
                        "Collapse State": False,
                        "X": 100,
                        "Y": 100,
                        "Width": 160
                        },
            header_left="Base Prop",
            header_right="Value"
        )

        # Non persistent data model
        self._undo_stack: QtWidgets.QUndoStack = undo_stack

        self._parent_frame: Optional[FrameItem] = None
        dag_scene_cls: type = getattr(importlib.import_module("dag_scene"), "DAGScene")  # Hack: Prevents cyclic import
        self._sub_scene: dag_scene_cls = dag_scene_cls(self._undo_stack)
        self._sub_scene.background_color = QtGui.QColor("#383838")

        self._socket_widgets: list[SocketWidget] = []
        self._evals: list[object] = [self.eval_socket_1, self.eval_socket_2]

        self._mode: str = ""
        self._lm_pressed: bool = False
        self._moved: bool = False
        self._resized: bool = False
        self._last_position: QtCore.QPointF = QtCore.QPointF()
        self._last_width: int = 0
        self._zoom_level: Optional[int] = None

        # Node geometry
        self._title_left_padding: int = 20
        self._min_width: int = 80
        self._height: int = 0
        self._header_height: int = 25
        self._min_height: int = self._header_height
        self._content_padding: int = 8
        self._content_y: int = self._header_height + self._content_padding
        # self._corner_radius: int = 0

        # Assets
        self._node_background_color: QtGui.QColor = QtGui.QColor("#303030")
        self._default_border_color: QtGui.QColor = QtGui.QColor("black")
        self._selected_border_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._font_color: QtGui.QColor = QtGui.QColor("#E5E5E5")

        self._default_border_pen: QtGui.QPen = QtGui.QPen(self._default_border_color)
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
        self.setZValue(2)
        self.setAcceptHoverEvents(True)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

        # Listeners
        cast(QtCore.SignalInstance, self._prop_model.dataChanged).connect(lambda: self.update_all())

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str) -> None:
        self._uuid: str = value

    @property
    def prop_model(self) -> PropertyModel:
        return self._prop_model

    @property
    def is_collapsed(self) -> str:
        return self._prop_model.properties["Collapse State"]

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
    def content_widget(self) -> QtWidgets.QWidget:
        return self._content_widget

    @property
    def content_layout(self) -> QtWidgets.QLayout:
        return self._content_layout

    @property
    def socket_widgets(self) -> list[SocketWidget]:
        return self._socket_widgets

    @socket_widgets.setter
    def socket_widgets(self, value: list[SocketWidget]) -> None:
        self._socket_widgets: list[SocketWidget] = value

    @property
    def input_socket_widgets(self) -> list[SocketWidget]:
        return [
            socket_widget for socket_widget in self._socket_widgets if socket_widget.is_input
        ]

    @property
    def output_socket_widgets(self) -> list[SocketWidget]:
        return [
            socket_widget for socket_widget in self._socket_widgets if not socket_widget.is_input
        ]

    @property
    def evals(self) -> list[object]:
        return self._evals

    @evals.setter
    def evals(self, value: list[object]) -> None:
        self._evals: list[object] = value

    @property
    def header_height(self) -> int:
        return self._header_height

    @property
    def content_y(self) -> float:
        return self._content_y

    @property
    def center(self) -> QtCore.QPointF:
        return QtCore.QPointF(
            self.x() + self.boundingRect().width() / 2,
            self.y() + self.boundingRect().height() / 2
        )

    @property
    def last_position(self) -> QtCore.QPointF:
        return self._last_position

    @property
    def moved(self) -> bool:
        return self._moved

    @moved.setter
    def moved(self, value: bool) -> None:
        self._moved: bool = value

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

    def add_socket_widget(self, socket_widget: SocketWidget, insert_idx: int = 0) -> None:
        socket_widget.pin.setParentItem(self)

        self._content_widget.hide()
        self._socket_widgets.insert(insert_idx, socket_widget)
        layout_offset: int = len([child for child in self._content_widget.children()
                                  if not isinstance(child, SocketWidget)]) - 1
        self._content_layout.insertWidget(insert_idx + layout_offset, socket_widget)
        self._content_widget.show()
        self.update_all()

    def remove_socket_widget(self, remove_idx: int = 0):
        if 0 <= remove_idx < len(self._socket_widgets):
            self._content_widget.hide()

            remove_widget: SocketWidget = self._socket_widgets[remove_idx]
            remove_edges: list[EdgeItem] = remove_widget.pin.edges

            while len(remove_edges) > 0:
                edge: EdgeItem = remove_edges.pop()
                self.scene().remove_edge(edge)

            self.scene().removeItem(remove_widget.pin)
            self._content_layout.removeWidget(remove_widget)
            # noinspection PyTypeChecker
            remove_widget.setParent(None)
            self._socket_widgets.remove(remove_widget)

            self._content_widget.show()
            self.update_all()

    def clear_socket_widgets(self):
        while len(self.socket_widgets) > 0:
            self.remove_socket_widget(0)

    def sort_socket_widgets(self) -> None:
        # Sorts widgets in layout
        for socket_widget in self._socket_widgets:
            if not socket_widget.is_input:
                self._content_widget.hide()
                self._content_layout.removeWidget(socket_widget)
                self._content_layout.insertWidget(self._content_layout.count(), socket_widget)
                self._content_widget.show()
                self.update_all()

        # Sorts socket widget list
        self._socket_widgets = [
            child for child in self._content_widget.children() if type(child) == SocketWidget and child.is_input
        ] + [
            child for child in self._content_widget.children() if type(child) == SocketWidget and not child.is_input
        ]

        # Sort socket widget links
        for idx, sorted_socket in enumerate(self._socket_widgets):
            linked_node: NodeItem = self._sub_scene.dag_item(sorted_socket.link[0])
            linked_socket: SocketWidget = linked_node.socket_widgets[sorted_socket.link[1]]
            linked_socket.link = (self.uuid, idx)

    def remove_from_frame(self):
        if self.parent_frame is not None:
            self.parent_frame.framed_nodes.remove(self)
            self.parent_frame.update()
            if len(self.parent_frame.framed_nodes) == 0:
                self.scene().remove_frame(self.parent_frame)
            self._parent_frame: Optional[FrameItem] = None

    # --------------- DAG analytics ---------------

    def has_in_edges(self) -> bool:
        for socket_widget in self.input_socket_widgets:
            if socket_widget.pin.has_edges():
                return True
        return False

    def has_out_edges(self) -> bool:
        for socket_widget in self.output_socket_widgets:
            if socket_widget.pin.has_edges():
                return True
        return False

    def predecessors(self) -> list[NodeItem]:
        result: list[NodeItem] = []
        for socket_widget in self.input_socket_widgets:
            if len(socket_widget.pin.edges) > 0:
                for edge in socket_widget.pin.edges:
                    pre_node: NodeItem = edge.start_pin.parent_node
                    if len(pre_node.sub_scene.nodes) > 0:
                        linked_lowest: SocketWidget = pre_node.linked_lowest_socket(edge.start_pin.socket_widget)
                        result.append(linked_lowest.parent_node)
                    else:
                        result.append(edge.start_pin.parent_node)

            else:
                linked_highest: SocketWidget = self.linked_highest_socket(socket_widget)
                if linked_highest != socket_widget:
                    for edge in linked_highest.pin.edges:
                        start_socket: SocketWidget = edge.start_pin.socket_widget
                        linked_lowest: SocketWidget = start_socket.parent_node.linked_lowest_socket(start_socket)
                        result.append(linked_lowest.parent_node)

        return result

    def successors(self) -> list[NodeItem]:
        result: list[NodeItem] = []
        for socket_widget in self._socket_widgets:
            if not socket_widget.is_input:
                for edge in socket_widget.pin.edges:
                    result.append(edge.end_pin.parent_node)
        return result

    def has_sub_scene(self) -> bool:
        return len(self._sub_scene.nodes) > 0

    def linked_lowest_socket(self, socket: SocketWidget) -> Optional[SocketWidget]:
        if len(self._sub_scene.nodes) > 0:
            linked_node: NodeItem = self.sub_scene.dag_item(socket.link[0])
            linked_socket: SocketWidget = linked_node.socket_widgets[socket.link[1]]
            return linked_node.linked_lowest_socket(linked_socket)
        else:
            return socket

    def linked_highest_socket(self, socket: SocketWidget) -> Optional[SocketWidget]:
        if self.scene().parent_node is not None and socket.link[0] == self.scene().parent_node.uuid:
            linked_node: NodeItem = self.scene().parent_node
            linked_socket: SocketWidget = linked_node.socket_widgets[socket.link[1]]
            return self.scene().parent_node.linked_highest_socket(linked_socket)
        else:
            return socket

    # --------------- Node eval methods ---------------

    @staticmethod
    def eval_socket_1(*args) -> Union[PinItem, int]:
        if len(args) > 1:
            return args[0] + args[1]
        else:
            return 0

    @staticmethod
    def eval_socket_2(*args) -> Union[PinItem, int]:
        if len(args) > 1:
            return args[0] - args[1]
        else:
            return 0

    # --------------- Overwrites ---------------

    def scene(self) -> Any:
        return super().scene()

    def itemChange(self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            if not self._moved and self._lm_pressed:
                self._last_position: QtCore.QPointF = value
                self._moved: bool = True

            new_pos: QtCore.QPointF = value

            snapping_step: int = 10
            x_snap = new_pos.x() // snapping_step * snapping_step
            y_snap = new_pos.y() // snapping_step * snapping_step

            x_mode_row: int = list(self._prop_model.properties.keys()).index("X")
            y_mode_row: int = list(self._prop_model.properties.keys()).index("Y")

            self._prop_model.setData(
                self._prop_model.index(x_mode_row, 1, QtCore.QModelIndex()), int(x_snap), 2  # QtCore.Qt.EditRole
            )
            self._prop_model.setData(
                self._prop_model.index(y_mode_row, 1, QtCore.QModelIndex()), int(y_snap), 2  # QtCore.Qt.EditRole
            )

            return QtCore.QPointF(x_snap, y_snap)

        elif change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemVisibleChange:
            self.update_details(self.scene().zoom_level)
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
                    # Hack to prevent cyclic imports
                    tgl_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "ToggleNodeCollapseCommand")
                    self._undo_stack.push(tgl_cmd_cls(self.scene(), self))

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

            self._prop_model.setData(
                self._prop_model.index(width_row, 1, QtCore.QModelIndex()), new_width, 2  # QtCore.Qt.EditRole
            )
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        # Hack to prevent cyclic imports
        resize_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "ResizeNodeCommand")
        if self._resized:
            self._undo_stack.push(resize_cmd_cls(self.scene(), self))

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
        print("Node UUID:", self._uuid)

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
                label=socket_widget_dict["Properties"]["Name"],
                is_input=socket_widget_dict["Properties"]["Is Input"],
                data=socket_widget_dict["Properties"]["Data"],
                parent_node=self
            )
            new_socket_widget.link = socket_widget_dict["Link"]
            self.add_socket_widget(new_socket_widget, i)

        # Reset sub graph data
        self.sub_scene.deserialize(state["Subgraph"])

        if self.has_sub_scene():
            # If custom node with sub scene
            for sub_node in self.sub_scene.nodes:
                sub_node.scene().parent_node = self

        self.update()

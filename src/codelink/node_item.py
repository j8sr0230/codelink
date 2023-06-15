from typing import Optional, Union, Any
import importlib

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from app_style import NODE_STYLE
from property_model import PropertyModel
from socket_widget import SocketWidget
from pin_item import PinItem
from edge_item import EdgeItem
from frame_item import FrameItem
from utils import crop_text


class NodeItem(QtWidgets.QGraphicsItem):
    def __init__(self, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._prop_model: PropertyModel = PropertyModel(
            properties={"Class": self.__class__.__name__,
                        "Name": "Scalar Math",
                        "Color": "#1D1D1D",
                        "Collapse State": False,
                        "X": 100,
                        "Y": 100,
                        "Width": 160
                        },
            header_left="Base Prop",
            header_right="Value"
        )

        self._mode: str = ""
        self._evals: list[object] = [self.eval_socket_1, self.eval_socket_2]
        self._socket_widgets: list[QtWidgets.QWidget] = []

        self._parent_frame: Optional[FrameItem] = None
        SubScene = getattr(importlib.import_module("editor_scene"), "EditorScene")  # Hack to prevent cyclic import
        self._sub_scene: SubScene = SubScene()
        self._pin_map: dict = {}

        # Node geometry
        self._title_left_padding: int = 20
        self._min_width: int = 80
        self._height: int = 0
        self._header_height: int = 25
        self._min_height: int = self._header_height
        self._content_padding: int = 8
        self._content_y: int = self._header_height + self._content_padding
        self._corner_radius: int = 5

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

        self._shadow: QtWidgets.QGraphicsDropShadowEffect = QtWidgets.QGraphicsDropShadowEffect()
        self._shadow.setColor(QtGui.QColor("black"))
        self._shadow.setBlurRadius(20)
        self._shadow.setOffset(1)
        self.setGraphicsEffect(self._shadow)

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

        # Hack for setting node_item ont to qss ont defined in app_style.py -> NODE_STYLE -> QWidget
        self._content_widget.style().unpolish(self._content_widget)  # Unload qss
        self._content_widget.style().polish(self._content_widget)  # Reload qss
        self._content_widget.update()
        self._header_font: QtGui.QFont = self._content_widget.font()
        self._name_item.setFont(self._header_font)
        self._name_item.setPos(self._title_left_padding,
                               (self._header_height - self._name_item.boundingRect().height()) / 2
                               )

        # Option combo box
        self._option_box: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Add", "Sub", "Mul"])
        self._option_box.currentIndexChanged.connect(self.update_socket_widgets)
        item_list_view: QtWidgets.QAbstractItemView = self._option_box.view()
        item_list_view.setSpacing(2)
        self._content_layout.addWidget(self._option_box)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            SocketWidget(label="A", is_input=True, parent_node=self),
            SocketWidget(label="B", is_input=True, parent_node=self),
            SocketWidget(label="Res", is_input=False, parent_node=self)
        ]
        for widget in self._socket_widgets:
            self._content_layout.addWidget(widget)

        self._content_proxy: QtWidgets.QGraphicsProxyWidget = QtWidgets.QGraphicsProxyWidget(self)
        self._content_proxy.setWidget(self._content_widget)

        self.update_all()
        self.setZValue(2)
        self.setAcceptHoverEvents(True)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

        # Listeners
        self._prop_model.dataChanged.connect(lambda: self.update_all())

    @property
    def prop_model(self) -> QtCore.QAbstractTableModel:
        return self._prop_model

    @property
    def evals(self) -> list[object]:
        return self._evals

    @property
    def socket_widgets(self) -> list[SocketWidget]:
        return self._socket_widgets

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
    def parent_frame(self) -> FrameItem:
        return self._parent_frame

    @parent_frame.setter
    def parent_frame(self, value: FrameItem) -> None:
        self._parent_frame: FrameItem = value

    @property
    def sub_scene(self) -> QtWidgets.QGraphicsScene:
        return self._sub_scene

    @property
    def pin_map(self) -> dict:
        return self._pin_map

    @pin_map.setter
    def pin_map(self, value: dict) -> None:
        self._pin_map: dict = value

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
    def is_collapsed(self) -> str:
        return self._prop_model.properties["Collapse State"]

    @property
    def content_widget(self) -> QtWidgets.QWidget:
        return self._content_widget

    def add_socket_widget(self, input_widget: SocketWidget, insert_idx: int = 0):
        input_widget.pin.setParentItem(self)

        self._content_widget.hide()
        self._socket_widgets.insert(insert_idx, input_widget)
        self._content_layout.insertWidget(insert_idx + 1, input_widget)
        self._content_widget.show()
        self._content_widget.update()
        self.update_all()
        self.update()

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
            # remove_widget.deleteLater()
            self._socket_widgets.remove(remove_widget)

            self._content_widget.show()
            self._content_widget.update()
            self.update_all()
            self.update()

    def clear_socket_widgets(self):
        while len(self.socket_widgets) > 0:
            self.remove_socket_widget(0)

    def sort_socket_widgets(self) -> None:
        input_pin_map: dict = {}
        output_pin_map: dict = {}

        # Sorts widgets in layout
        for socket_idx, socket_widget in enumerate(self._socket_widgets):
            if not socket_widget.is_input:
                self._content_layout.removeWidget(socket_widget)
                self._content_layout.insertWidget(self._content_layout.count(), socket_widget)
                output_pin_map[socket_idx] = self._pin_map[str(socket_idx)]
            else:
                input_pin_map[socket_idx] = self._pin_map[str(socket_idx)]

        # Sorts pin map
        sorted_pin_map: dict = {}
        for idx, value in enumerate(list(input_pin_map.values()) + list(output_pin_map.values())):
            sorted_pin_map[str(idx)] = value
        self._pin_map: dict = sorted_pin_map

        # Sorts socket widget list
        self._socket_widgets = [
            child for child in self._content_widget.children() if type(child) == SocketWidget and child.is_input
        ] + [
            child for child in self._content_widget.children() if type(child) == SocketWidget and not child.is_input
        ]

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

    def linked_lowest_socket(self, socket: SocketWidget) -> Optional[SocketWidget]:
        if len(self._sub_scene.nodes) > 0:
            linked_node_idx: int = self._pin_map[str(self._socket_widgets.index(socket))][0]
            linked_socket_idx: int = self._pin_map[str(self._socket_widgets.index(socket))][1]
            linked_socket: SocketWidget = self._sub_scene.nodes[linked_node_idx].socket_widgets[linked_socket_idx]
            return linked_socket.parent_node.linked_lowest_socket(linked_socket)
        else:
            return socket

    def linked_highest_socket(self, socket: SocketWidget) -> Optional[SocketWidget]:
        if self.scene().parent_custom_node:
            pin_map: dict = self.scene().parent_custom_node.pin_map
            linked_node_idx: int = self.scene().nodes.index(self)
            linked_socket_idx: int = self.scene().nodes[linked_node_idx].socket_widgets.index(socket)
            if [linked_node_idx, linked_socket_idx] in list(pin_map.values()):
                linked_socket: SocketWidget = self.scene().parent_custom_node.socket_widgets[
                    list(pin_map.values()).index([linked_node_idx, linked_socket_idx])
                ]
                return self.scene().parent_custom_node.linked_highest_socket(linked_socket)
            else:
                return socket
        else:
            return socket

    def predecessors(self) -> list['NodeItem']:
        result: list['NodeItem'] = []
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
                        result.append(edge.start_pin.parent_node)

        return result

    def successors(self) -> list['NodeItem']:
        result: list['NodeItem'] = []
        for socket_widget in self._socket_widgets:
            if not socket_widget.is_input:
                for edge in socket_widget.pin.edges:
                    result.append(edge.end_pin.parent_node)
        return result

    # noinspection PyUnusedLocal
    @staticmethod
    def eval_socket_1(*args) -> Union[PinItem, int]:
        if len(args) > 1:
            return args[0] + args[1]
        else:
            return 0

    # noinspection PyUnusedLocal
    @staticmethod
    def eval_socket_2(*args) -> Union[PinItem, int]:
        if len(args) > 1:
            return args[0] - args[1]
        else:
            return 0

    def itemChange(self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            new_pos: QtCore.QPointF = value

            snapping_step: int = 10
            x_snap = new_pos.x() // snapping_step * snapping_step
            y_snap = new_pos.y() // snapping_step * snapping_step

            x_mode_row: int = list(self._prop_model.properties.keys()).index("X")
            y_mode_row: int = list(self._prop_model.properties.keys()).index("Y")

            # noinspection PyTypeChecker
            self._prop_model.setData(
                self._prop_model.index(x_mode_row, 1, QtCore.QModelIndex()), int(x_snap), QtCore.Qt.EditRole
            )
            # noinspection PyTypeChecker
            self._prop_model.setData(
                self._prop_model.index(y_mode_row, 1, QtCore.QModelIndex()), int(y_snap), QtCore.Qt.EditRole
            )

            return QtCore.QPointF(x_snap, y_snap)
        else:
            return super().itemChange(change, value)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)

        self.setZValue(3)

        if event.button() == QtCore.Qt.LeftButton:
            if self.boundingRect().width() - 5 < event.pos().x() < self.boundingRect().width():
                self._mode: str = "RESIZE"
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeHorCursor)

            collapse_btn_left: float = 0
            collapse_btn_right: float = self._title_left_padding
            collapse_btn_top: float = 0
            collapse_btn_bottom: float = self._header_height

            if collapse_btn_left <= event.pos().x() <= collapse_btn_right:
                if collapse_btn_top <= event.pos().y() <= collapse_btn_bottom:
                    collapse_state: bool = not self._prop_model.properties["Collapse State"]

                    collapse_mode_row: int = list(self._prop_model.properties.keys()).index("Collapse State")

                    # noinspection PyTypeChecker
                    self._prop_model.setData(
                        self._prop_model.index(collapse_mode_row, 1, QtCore.QModelIndex()),
                        collapse_state, QtCore.Qt.EditRole
                    )

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self._mode == "RESIZE":
            old_x_left: float = self.boundingRect().x()
            old_y_top: float = self.boundingRect().y()

            old_top_left_local: QtCore.QPointF = QtCore.QPointF(old_x_left, old_y_top)
            old_top_left_global: QtCore.QPointF = self.mapToScene(old_top_left_local)

            current_x: int = self.mapToScene(event.pos()).x()
            new_width: float = current_x - old_top_left_global.x()

            width_row: int = list(self._prop_model.properties.keys()).index("Width")

            # noinspection PyTypeChecker
            self._prop_model.setData(
                self._prop_model.index(width_row, 1, QtCore.QModelIndex()), new_width, QtCore.Qt.EditRole
            )
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
        QtWidgets.QApplication.restoreOverrideCursor()

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

    def update_socket_widgets(self):
        option_name: str = self._option_box.currentText()
        input_widget_count: int = len(self.input_socket_widgets)

        if option_name == "Add":
            while input_widget_count < 2:
                new_socket_widget: SocketWidget = SocketWidget(label="N", is_input=True, parent_node=self)
                insert_idx: int = len(self.input_socket_widgets)
                self.add_socket_widget(new_socket_widget, insert_idx)
                input_widget_count += 1

            while input_widget_count > 2:
                remove_idx: int = len(self.input_socket_widgets) - 1
                self.remove_socket_widget(remove_idx)
                input_widget_count -= 1

    def update_all(self):
        self.update_name(self._prop_model.properties["Name"])
        self.update_width(self._prop_model.properties["Width"])
        self.update_height()

        # Hack to prevent callback loop while changing the node position
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setPos(QtCore.QPointF(self._prop_model.properties["X"], self._prop_model.properties["Y"]))
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._prop_model.properties["Width"], self._height)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._node_background_color)
        painter.drawRoundedRect(self.boundingRect(), self._corner_radius, self._corner_radius)

        rect: QtCore.QRectF = QtCore.QRectF(0, 0, self._prop_model.properties["Width"], self._header_height)
        painter.setBrush(QtGui.QColor(self._prop_model.properties["Color"]))
        painter.drawRoundedRect(rect, self._corner_radius, self._corner_radius)

        painter.setBrush(QtCore.Qt.NoBrush)
        if self.isSelected():
            painter.setPen(self._selected_border_pen)
        else:
            painter.setPen(self._default_border_pen)
        painter.drawRoundedRect(self.boundingRect(), self._corner_radius, self._corner_radius)

    def __getstate__(self) -> dict:
        data_dict: dict = {
            "Properties": self.prop_model.__getstate__(),
            "Option_idx": self._option_box.currentIndex()
        }

        sockets_list: list[dict] = []
        for idx, socket_widget in enumerate(self._socket_widgets):
            sockets_list.append(socket_widget.prop_model.__getstate__())

        data_dict["Sockets"] = sockets_list
        data_dict["Subgraph"] = {
            "Nodes": self.sub_scene.serialize_nodes(),
            "Edges": self.sub_scene.serialize_edges(),
            "Pin Map": self._pin_map
        }

        return data_dict

    def __setstate__(self, state: dict):
        self.prop_model.__setstate__(state["Properties"])
        self._option_box.setCurrentIndex(state["Option_idx"])

        # Remove predefined socket widgets
        self.clear_socket_widgets()

        # Add socket widgets from state
        for i in range(len(state["Sockets"])):
            socket_widget_props: dict = state["Sockets"][i]
            SocketWidgetClass = getattr(importlib.import_module("socket_widget"), socket_widget_props["Class"])
            new_socket_widget: SocketWidgetClass = SocketWidgetClass(
                label=socket_widget_props["Name"],
                is_input=socket_widget_props["Is Input"],
                parent_node=self
            )
            new_socket_widget.prop_model.__setstate__(socket_widget_props)
            self.add_socket_widget(new_socket_widget, i)

            new_socket_widget.update_all()
            new_socket_widget.update()

        # Reset sub graph data
        self.sub_scene.deserialize_nodes(state["Subgraph"]["Nodes"])
        self.sub_scene.deserialize_edges(state["Subgraph"]["Edges"])
        self._pin_map: dict = state["Subgraph"]["Pin Map"]

        if len(self.sub_scene.nodes) > 0:
            # If custom node with sub scene
            for sub_node in self.sub_scene.nodes:
                sub_node.scene().parent_custom_node = self

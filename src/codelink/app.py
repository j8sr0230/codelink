import os
import sys
import math
import pickle
from typing import Optional, Any, Union

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from dask.threaded import get


class Socket(QtWidgets.QGraphicsItem):
    def __init__(self, color: QtGui.QColor, socket_widget: Optional['SocketWidget'],
                 parent_node: Optional['Node'] = None) -> None:
        super().__init__(parent_node)

        self._color: QtGui.QColor = QtGui.QColor(color)
        self._socket_widget: Optional['SocketWidget'] = socket_widget

        self._edges: list['Edge'] = []

        self._size: int = 12

        self.setAcceptHoverEvents(True)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

    @property
    def color(self) -> QtGui.QColor:
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        self._color: QtGui.QColor = QtGui.QColor(value)

    @property
    def socket_widget(self) -> Optional['SocketWidget']:
        return self._socket_widget

    @property
    def edges(self) -> list['Edge']:
        return self._edges

    @edges.setter
    def edges(self, value: list['Edge']) -> None:
        self._edges: list[Edge] = value

    @property
    def size(self) -> int:
        return self._size

    def add_edge(self, edge: 'Edge') -> None:
        self._edges.append(edge)

    def remove_edge(self, edge: 'Edge') -> None:
        self._edges.remove(edge)

    def has_edges(self) -> bool:
        if len(self._edges) > 0:
            return True
        else:
            return False

    def center(self) -> QtCore.QPointF:
        return QtCore.QPointF(
            self.x() + self._size / 2,
            self.y() + self._size / 2,
        )

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverEnterEvent(event)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverLeaveEvent(event)
        QtWidgets.QApplication.restoreOverrideCursor()

    def boundingRect(self) -> QtCore.QRectF:
        # return QtCore.QRectF(0, 0, self._size, self._size)
        return QtCore.QRectF(-self._size, -self._size, 3 * self._size, 3 * self._size)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtGui.QPen(QtGui.QColor("black")))
        painter.setBrush(QtGui.QBrush(self._color))
        # painter.drawEllipse(self.boundingRect())  # Visualises snapping area
        painter.drawEllipse(0, 0, self._size, self._size)


class SocketWidget(QtWidgets.QWidget):
    def __init__(self, label: str = "In", socket_type: object = int, is_input: bool = True,
                 parent_node: Optional['Node'] = None,
                 parent_widget: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent_widget)

        self._label: str = label
        self._socket_type: object = socket_type
        self._is_input: bool = is_input
        self._parent_node: Optional['Node'] = parent_node

        self._socket: Socket = Socket(color=QtGui.QColor("#00D6A3"), parent_node=parent_node, socket_widget=self)

        self._layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self._layout.setMargin(0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)

        self._label_widget: QtWidgets.QLabel = QtWidgets.QLabel(self._label, self)
        self._label_widget.setFont(self._parent_node.font)
        self._layout.addWidget(self._label_widget)

        self._input_widget: QtWidgets.QWidget = QtWidgets.QLineEdit(self)
        self._input_widget.setFont(self._parent_node.font)
        self._input_widget.setMinimumWidth(5)
        self._input_widget.setPlaceholderText("Enter value")
        self._layout.addWidget(self._input_widget)

        self.update_stylesheets()

    @property
    def socket_type(self) -> object:
        return self._socket_type

    @property
    def is_input(self) -> bool:
        return self._is_input

    @property
    def socket(self) -> Socket:
        return self._socket

    @property
    def input_widget(self) -> QtWidgets.QWidget:
        return self._input_widget

    def has_edges(self) -> bool:
        return self._socket.has_edges()

    def input_data(self) -> Union['Node', int]:
        if self.has_edges():
            return self._socket.edges[0].start_socket.socket_widget
        else:
            if self._input_widget.text() != "":
                return int(self._input_widget.text())
            else:
                return 0

    def update_stylesheets(self):
        if self._is_input:
            self._label_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

            if self._socket.has_edges():
                self._label_widget.setStyleSheet(
                    "color: #E5E5E5;"
                    "background-color: transparent;"
                    "min-height: 24px;"
                    "margin: 0px;"
                    "padding-left: 10px;"
                    "padding-right: 0px;"
                    "padding-top: 0px;"
                    "padding-bottom: 0px;"
                    "border-radius: 0px;"
                    "border: 0px;"
                )
                self._input_widget.hide()
            else:
                self._label_widget.setStyleSheet(
                    "color: #E5E5E5;"
                    "background-color: #545454;"
                    "min-height: 24px;"
                    "margin-left: 0px;"
                    "margin-right: 1px;"
                    "margin-top: 0px;"
                    "margin-bottom: 0px;"
                    "padding-left: 10px;"
                    "padding-right: 10px;"
                    "padding-top: 0px;"
                    "padding-bottom: 0px;"
                    "border-top-left-radius: 5px;"
                    "border-bottom-left-radius: 5px;"
                    "border-top-right-radius: 0px;"
                    "border-bottom-right-radius: 0px;"
                    "border: 0px;"
                )

                self._input_widget.setStyleSheet(
                    "color: #E5E5E5;"
                    "background-color: #545454;"
                    "min-width: 5px;"
                    "min-height: 24px;"
                    "margin-left: 1px;"
                    "margin-right: 0px;"
                    "margin-top: 0px;"
                    "margin-bottom: 0px;"
                    "padding-left: 10px;"
                    "padding-right: 10px;"
                    "padding-top: 0px;"
                    "padding-bottom: 0px;"
                    "border-top-left-radius: 0px;"
                    "border-bottom-left-radius: 0px;"
                    "border-top-right-radius: 5px;"
                    "border-bottom-right-radius: 5px;"
                    "border: 0px;"
                )
                self._input_widget.show()
        else:
            self._label_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self._label_widget.setStyleSheet(
                "color: #E5E5E5;"
                "background-color: transparent;"
                "min-height: 24px;"
                "margin: 0px;"
                "padding-left: 0px;"
                "padding-right: 10px;"
                "padding-top: 0px;"
                "padding-bottom: 0px;"
                "border-radius: 0px;"
                "border: 0px;"
            )
            self._input_widget.hide()

    def update_socket_positions(self) -> None:
        if not self._parent_node.is_collapsed:
            y_pos: float = (self._parent_node.content_y + self.y() + (self.height() - self._socket.size) / 2)

            if self._is_input:
                self._socket.setPos(-self._socket.size / 2, y_pos)
            else:
                self._socket.setPos(self._parent_node.boundingRect().width() - self._socket.size / 2, y_pos)
            self._socket.show()

        else:
            y_pos: float = (self._parent_node.header_height - self._socket.size) / 2
            if self._is_input:
                self._socket.setPos(-self._socket.size / 2, y_pos)
            else:
                self._socket.setPos(self._parent_node.boundingRect().width() - self._socket.size / 2, y_pos)
            self._socket.hide()


class Edge(QtWidgets.QGraphicsPathItem):
    def __init__(self, color: QtGui.QColor, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._color: QtGui.QColor = color

        self._start_socket: Optional[QtWidgets.QGraphicsItem] = None
        self._end_socket: Optional[QtWidgets.QGraphicsItem] = None

        self.setAcceptHoverEvents(True)
        self.setZValue(-1)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

    @property
    def start_socket(self) -> QtWidgets.QGraphicsItem:
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value: QtWidgets.QGraphicsItem) -> None:
        self._start_socket: QtWidgets.QGraphicsItem = value

    @property
    def end_socket(self) -> QtWidgets.QGraphicsItem:
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value: QtWidgets.QGraphicsItem) -> None:
        self._end_socket: QtWidgets.QGraphicsItem = value

    def sort_sockets(self) -> None:
        old_start_socket: QtWidgets.QGraphicsItem = self._start_socket

        if old_start_socket.socket_widget.is_input:
            self._start_socket: QtWidgets.QGraphicsItem = self._end_socket
            self._end_socket: QtWidgets.QGraphicsItem = old_start_socket

    def path(self) -> QtGui.QPainterPath:
        start_point: QtCore.QPointF = self._start_socket.parentItem().mapToScene(self._start_socket.center())

        if type(self._end_socket) == Socket:
            end_point: QtCore.QPointF = self._end_socket.parentItem().mapToScene(self._end_socket.center())
        else:
            end_point: QtCore.QPointF = self._end_socket.pos()

        ctr_pt_offset: float = abs(end_point.x() - start_point.x()) / 2.5

        if not self._start_socket.socket_widget.is_input:
            ctr_pt_1: QtCore.QPointF = QtCore.QPointF(start_point.x() + ctr_pt_offset, start_point.y())
            ctr_pt_2: QtCore.QPointF = QtCore.QPointF(end_point.x() - ctr_pt_offset, end_point.y())
        else:
            ctr_pt_1: QtCore.QPointF = QtCore.QPointF(start_point.x() - ctr_pt_offset, start_point.y())
            ctr_pt_2: QtCore.QPointF = QtCore.QPointF(end_point.x() + ctr_pt_offset, end_point.y())

        path: QtGui.QPainterPath = QtGui.QPainterPath(start_point)
        path.cubicTo(ctr_pt_1, ctr_pt_2, end_point)

        return path

    def shape(self) -> QtGui.QPainterPath:
        return self.path()

    def boundingRect(self) -> QtCore.QRectF:
        return self.path().boundingRect()

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:
        pen: QtGui.QPen = QtGui.QPen(self._color)
        pen.setWidthF(3.0)

        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawPath(self.path())


class Node(QtWidgets.QGraphicsItem):
    def __init__(self, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._visited_count: int = 0
        self._evals: list[object] = [self.eval_socket_1, self.eval_socket_2]

        self._title: str = "Node Name"
        self._socket_widgets: list[QtWidgets.QWidget] = []

        self._title_x: int = 20
        self._min_width: int = 80
        self._width: int = 160
        self._max_height: int = 80
        self._height: int = self._max_height
        self._header_height: int = 25
        self._min_height: int = self._header_height
        self._content_padding: int = 8
        self._content_y: int = self._header_height + self._content_padding
        self._corner_radius: int = 5

        self._mode: str = ""
        self._is_collapsed: bool = False

        self._node_background_color: QtGui.QColor = QtGui.QColor("#303030")
        self._header_background_color: QtGui.QColor = QtGui.QColor("#1D1D1D")
        self._default_border_color: QtGui.QColor = QtGui.QColor("black")
        self._selected_border_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._font_color: QtGui.QColor = QtGui.QColor("#E5E5E5")

        self._default_border_pen: QtGui.QPen = QtGui.QPen(self._default_border_color)
        self._selected_border_pen: QtGui.QPen = QtGui.QPen(self._selected_border_color)

        self._font: QtGui.QFont = QtGui.QFont("Sans Serif", 10)

        self._shadow: QtWidgets.QGraphicsDropShadowEffect = QtWidgets.QGraphicsDropShadowEffect()
        self._shadow.setColor(QtGui.QColor("black"))
        self._shadow.setBlurRadius(20)
        self._shadow.setOffset(1)
        self.setGraphicsEffect(self._shadow)

        self.setAcceptHoverEvents(True)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

        self._collapse_img_down: QtGui.QImage = QtGui.QImage("icon:images_dark-light/down_arrow_light.svg")
        self._collapse_pixmap_down: QtGui.QPixmap = QtGui.QPixmap(self._collapse_img_down)
        self._collapse_img_up: QtGui.QImage = QtGui.QImage("icon:images_dark-light/up_arrow_light.svg")
        self._collapse_pixmap_up: QtGui.QPixmap = QtGui.QPixmap(self._collapse_img_up)

        self._collapse_btn: QtWidgets.QGraphicsPixmapItem = QtWidgets.QGraphicsPixmapItem()
        self._collapse_btn.setParentItem(self)
        self._collapse_btn.setPixmap(self._collapse_pixmap_down)
        btn_x = ((self._title_x + self._collapse_btn.boundingRect().width() / 2) -
                 self._collapse_btn.boundingRect().width()) / 2
        self._collapse_btn.setPos(btn_x, (self._header_height - self._collapse_btn.boundingRect().height()) / 2)

        self._title_item = QtWidgets.QGraphicsTextItem(self)
        self._title_item.setDefaultTextColor(self._font_color)
        self._title_item.setFont(self._font)
        self._title_item.setPlainText(
            self.crop_text(self._title, self._width - self._title_x - self._content_padding, self._font)
        )
        self._title_item.setPos(self._title_x, (self._header_height - self._title_item.boundingRect().height()) / 2)

        self._content_widget: QtWidgets.QWidget = QtWidgets.QWidget()
        self._content_widget.setStyleSheet("background-color: transparent")
        self._content_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        self._content_layout.setMargin(0)
        self._content_layout.setSpacing(5)
        self._content_widget.setLayout(self._content_layout)

        self._option_box: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self._option_box.setMinimumWidth(5)
        self._option_box.setFont(self._font)
        self._option_box.addItems(["Option 1", "Option 2", "Option 3"])
        self._option_box.setStyleSheet("""
            QComboBox {
                color: #E5E5E5;
                background-color: #282828;
                border-radius: 5px;
                min-width: 5px;
                min-height:  24px;
                padding-left: 10px;
                padding-right: 0px;
                padding-top: 0px;
                padding-bottom: 0px;
                margin: 0px;
                border: 0px;
            }
            QComboBox::drop-down {
                background-color: #545454;
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }
            QComboBox::down-arrow {
                image: url(icon:images_dark-light/down_arrow_light.svg);
                /*image: url(qss:images_dark-light/down_arrow_light.svg);*/
            }
        """)

        item_list_view: QtWidgets.QAbstractItemView = self._option_box.view()
        item_list_view.setSpacing(2)
        item_list_view.setStyleSheet("""
            QAbstractItemView {
                color: #E5E5E5;
                selection-color: #E5E5E5;
                background-color: #282828;
                selection-background-color: #4772B3;
                border-radius: 5px;
                min-width: 20px;
                min-height: 24px;
                padding-left: 5px;
                padding-right: 0px;
                padding-top: 0px;
                padding-bottom: 0px;
                margin: 0px;
                border: 0px;
            }
        """)

        self._content_layout.addWidget(self._option_box)

        self._socket_widgets: list[Optional[SocketWidget]] = [
            SocketWidget(label="A", socket_type=int, is_input=True, parent_node=self),
            SocketWidget(label="B", socket_type=int, is_input=True, parent_node=self),
            SocketWidget(label="Res", socket_type=int, is_input=False, parent_node=self)
        ]
        for widget in self._socket_widgets:
            self._content_layout.addWidget(widget)

        self._content_proxy: QtWidgets.QGraphicsProxyWidget = QtWidgets.QGraphicsProxyWidget(self)
        self._content_proxy.setWidget(self._content_widget)
        self._content_rect: QtCore.QRectF = QtCore.QRectF(self._content_padding,
                                                          self._header_height + self._content_padding,
                                                          self._width - 2 * self._content_padding,
                                                          self._content_widget.height())
        self._content_proxy.setGeometry(self._content_rect)
        self._height = (self._header_height + 2 * self._content_padding + self._content_widget.height())

        self.update_socket_positions()

    @staticmethod
    def crop_text(text: str = "Test", width: float = 30, font: QtGui.QFont = QtGui.QFont()) -> str:
        font_metrics: QtGui.QFontMetrics = QtGui.QFontMetrics(font)

        cropped_text: str = "..."
        string_idx: int = 0
        while all([font_metrics.horizontalAdvance(cropped_text) < width - font_metrics.horizontalAdvance("..."),
                   string_idx < len(text)]):
            cropped_text = cropped_text[:string_idx] + text[string_idx] + cropped_text[string_idx:]
            string_idx += 1

        if string_idx == len(text):
            cropped_text: str = cropped_text[:len(text)]

        return cropped_text

    @property
    def visited_count(self) -> int:
        return self._visited_count

    @visited_count.setter
    def visited_count(self, value: int) -> None:
        self._visited_count: int = value

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
    def is_collapsed(self) -> bool:
        return self._is_collapsed

    @property
    def font(self) -> QtGui.QFont:
        return self._font

    @property
    def socket_widgets(self) -> list[SocketWidget]:
        return self._socket_widgets

    @property
    def input_socket_widgets(self) -> list[SocketWidget]:
        result: list[SocketWidget] = []
        for socket_widget in self._socket_widgets:
            if socket_widget.is_input:
                result.append(socket_widget)

        return result

    @property
    def output_socket_widgets(self) -> list[SocketWidget]:
        result: list[SocketWidget] = []
        for socket_widget in self._socket_widgets:
            if not socket_widget.is_input:
                result.append(socket_widget)

        return result

    def has_in_edges(self) -> bool:
        for socket_widget in self._socket_widgets:
            if socket_widget.is_input and socket_widget.has_edges():
                return True
        return False

    def has_out_edges(self) -> bool:
        for socket_widget in self._socket_widgets:
            if not socket_widget.is_input and socket_widget.has_edges():
                return True
        return False

    def predecessors(self) -> list['Node']:
        result: list['Node'] = []
        for socket_widget in self._socket_widgets:
            if socket_widget.is_input:
                for edge in socket_widget.socket.edges:
                    result.append(edge.start_socket.parentItem())
        return result

    def successors(self) -> list['Node']:
        result: list['Node'] = []
        for socket_widget in self._socket_widgets:
            if not socket_widget.is_input:
                for edge in socket_widget.socket.edges:
                    result.append(edge.end_socket.parentItem())
        return result

    def update_socket_positions(self) -> None:
        for widget in self._socket_widgets:
            widget.update_socket_positions()

    @staticmethod
    def eval_socket_1(a: int, b: int) -> int:
        return a + b

    @staticmethod
    def eval_socket_2(a: int, b: int) -> int:
        return a + b

    def itemChange(self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            new_pos: QtCore.QPointF = value

            snapping_step: int = 10
            x_snap = new_pos.x() // snapping_step * snapping_step
            y_snap = new_pos.y() // snapping_step * snapping_step
            return QtCore.QPointF(x_snap, y_snap)
        else:
            return super().itemChange(change, value)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)

        self.setZValue(1)

        if event.button() == QtCore.Qt.LeftButton:
            if self.boundingRect().width() - 5 < event.pos().x() < self.boundingRect().width():
                self._mode: str = "RESIZE"
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeHorCursor)

            collapse_btn_left: float = 0
            collapse_btn_right: float = self._title_x
            collapse_btn_top: float = 0
            collapse_btn_bottom: float = self._header_height

            if collapse_btn_left <= event.pos().x() <= collapse_btn_right:
                if collapse_btn_top <= event.pos().y() <= collapse_btn_bottom:
                    self._mode: str = "COLLAPSE"
                    if not self._is_collapsed:
                        self._collapse_btn.setPixmap(self._collapse_pixmap_up)
                        self._content_proxy.hide()
                        self._height = self._min_height
                    else:
                        self._collapse_btn.setPixmap(self._collapse_pixmap_down)
                        self._content_proxy.show()
                        self._height = (self._header_height + self._content_padding + self._content_widget.height() +
                                        self._content_padding)

                    self._is_collapsed = not self._is_collapsed
                    self.update_socket_positions()

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self._mode == "RESIZE":
            old_x_left: float = self.boundingRect().x()
            old_y_top: float = self.boundingRect().y()

            old_top_left_local: QtCore.QPointF = QtCore.QPointF(old_x_left, old_y_top)
            old_top_left_global: QtCore.QPointF = self.mapToScene(old_top_left_local)

            current_x: int = self.mapToScene(event.pos()).x()
            new_width: float = current_x - old_top_left_global.x()
            if new_width < self._min_width:
                new_width: float = self._min_width

            self._width = new_width
            self._shadow.updateBoundingRect()
            self._title_item.setPlainText(
                self.crop_text(self._title, self._width - self._title_x - self._content_padding, self._font)
            )
            self._content_rect: QtCore.QRectF = QtCore.QRectF(self._content_padding,
                                                              self._header_height + self._content_padding,
                                                              self._width - 2 * self._content_padding,
                                                              self._content_widget.height())
            self._content_proxy.setGeometry(self._content_rect)

            self.update_socket_positions()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        self.setZValue(0)

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

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._width, self._height)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._node_background_color)
        painter.drawRoundedRect(self.boundingRect(), self._corner_radius, self._corner_radius)

        rect: QtCore.QRectF = QtCore.QRectF(0, 0, self._width, self._header_height)
        painter.setBrush(self._header_background_color)
        painter.drawRoundedRect(rect, self._corner_radius, self._corner_radius)

        painter.setBrush(QtCore.Qt.NoBrush)
        if self.isSelected():
            painter.setPen(self._selected_border_pen)
        else:
            painter.setPen(self._default_border_pen)
        painter.drawRoundedRect(self.boundingRect(), self._corner_radius, self._corner_radius)

    def __getstate__(self) -> dict:
        print("__getstate__")

        state: dict = {
            "x": self.x(),
            "y": self.y(),
            "width": self._width,
            "is_collapsed": self._is_collapsed
        }

        return state

    def __setstate__(self, state: dict):
        print("__setstate__", repr(state))

        self.__init__(parent=None)
        # self.setPos(QtCore.QPointF(state["x"], state["y"]))
        self.setPos(QtCore.QPointF(32500, 31800))
        self._width = state["width"]
        self._is_collapsed = state["is_collapsed"]


class Cutter(QtWidgets.QGraphicsPathItem):
    def __init__(self, start: QtCore.QPointF = QtCore.QPointF(), end: QtCore.QPointF = QtCore.QPointF(),
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._start_point: QtCore.QPointF = start
        self._end_point: QtCore.QPointF = end

    @property
    def start_point(self) -> QtCore.QPointF():
        return self._start_point

    @start_point.setter
    def start_point(self, value: QtCore.QPointF) -> None:
        self._start_point = value

    @property
    def end_point(self) -> QtCore.QPointF():
        return self._end_point

    @end_point.setter
    def end_point(self, value: QtCore.QPointF) -> None:
        self._end_point = value

    def path(self) -> QtGui.QPainterPath:
        path: QtGui.QPainterPath = QtGui.QPainterPath(self._start_point)
        path.lineTo(self._end_point)
        return path

    def shape(self) -> QtGui.QPainterPath:
        return self.path()

    def boundingRect(self) -> QtCore.QRectF:
        return self.path().boundingRect()

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:
        pen: QtGui.QPen = QtGui.QPen(QtGui.QColor("#E5E5E5"))
        pen.setStyle(QtCore.Qt.DashLine)
        pen.setWidthF(1.0)

        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawPath(self.path())


class NodeEditorScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent: Optional[QtCore.QObject] = None):
        super().__init__(QtCore.QRectF(0, 0, 64000, 64000), parent)

        self._nodes: list[Node] = []
        self._edges: list[Edge] = []

        self._grid_spacing: int = 50
        self._background_color: QtGui.QColor = QtGui.QColor("#1D1D1D")
        self._grid_color: QtGui.QColor = QtGui.QColor("#282828")
        self._grid_pen: QtGui.QPen = QtGui.QPen(self._grid_color)
        self._grid_pen.setWidth(5)

        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)

    @property
    def nodes(self) -> list[Node]:
        return self._nodes

    @nodes.setter
    def nodes(self, value: list[Node]) -> None:
        self._nodes: list[Node] = value

    def add_node(self, node: Node) -> None:
        self._nodes.append(node)
        self.addItem(node)

    def remove_node(self, node: Node) -> None:
        self._nodes.remove(node)
        self.removeItem(node)

    def add_edge(self, edge: Edge) -> None:
        self._edges.append(edge)
        self.addItem(edge)

    def remove_edge(self, edge: Edge) -> None:
        self._edges.remove(edge)
        self.removeItem(edge)

    def graph_ends(self) -> list[Node]:
        result: list[Node] = []
        for node in self._nodes:
            if not node.has_out_edges():
                result.append(node)
        return result

    def _is_node_cyclic(self, visited_node: Node) -> bool:
        visited_node.visited_count += 1

        if visited_node.visited_count > len(visited_node.successors()) + 1:
            return True

        temp_res: list[bool] = []
        for node in visited_node.predecessors():
            temp_res.append(self._is_node_cyclic(node))
        return any(temp_res)

    def is_node_cyclic(self, visited_node: Node) -> bool:
        for node in self._nodes:
            node.visited_count = 0
        return self._is_node_cyclic(visited_node)

    def is_graph_cyclic(self) -> bool:
        temp_res: list[bool] = []
        for node in self._nodes:
            temp_res.append(self.is_node_cyclic(node))
        return any(temp_res)

    def graph_to_dict(self, visited_node: Node, graph_dict: dict) -> dict:
        for node in visited_node.predecessors():
            self.graph_to_dict(node, graph_dict)

        task_inputs: list = []
        for socket_widget in visited_node.input_socket_widgets:
            if socket_widget.is_input:
                task_inputs.append(socket_widget.input_data())

        for idx, socket_widget in enumerate(visited_node.output_socket_widgets):
            if not socket_widget.is_input:
                graph_dict[socket_widget] = (visited_node.evals[idx], *task_inputs)

        return graph_dict

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)

        self.setBackgroundBrush(self._background_color)

        bound_box_left: int = int(math.floor(rect.left()))
        bound_box_right: int = int(math.ceil(rect.right()))
        bound_box_top: int = int(math.floor(rect.top()))
        bound_box_bottom: int = int(math.ceil(rect.bottom()))

        first_left: int = bound_box_left - (bound_box_left % self._grid_spacing)
        first_top: int = bound_box_top - (bound_box_top % self._grid_spacing)

        points: list[Optional[QtCore.QPoint]] = []
        for x in range(first_left, bound_box_right, self._grid_spacing):
            for y in range(first_top, bound_box_bottom, self._grid_spacing):
                points.append(QtCore.QPoint(x, y))

        painter.setPen(self._grid_pen)
        painter.drawPoints(points)


class NodeEditorView(QtWidgets.QGraphicsView):
    def __init__(self, scene: QtWidgets.QGraphicsScene = None, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(scene, parent)

        self._lm_pressed: bool = False
        self._mm_pressed: bool = False
        self._rm_pressed: bool = False
        self._mode: str = ""

        self._last_pos: QtCore.QPoint = QtCore.QPoint()
        self._last_socket: Optional[Socket] = None
        self._temp_edge: Optional[Edge] = None
        self._cutter: Optional[Cutter] = None

        self._zoom_level: int = 10
        self._zoom_level_range: list = [5, 10]

        self.setStyleSheet("selection-background-color: black")
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)

        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing |
                            QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:

        self._last_pos: QtCore.QPointF = self.mapToScene(event.pos())

        if event.button() == QtCore.Qt.LeftButton and self._mode == "":
            super().mousePressEvent(event)

            self._lm_pressed: bool = True

            if type(self.itemAt(event.pos())) == Socket:
                self._last_socket: QtWidgets.QGraphicsItem = self.itemAt(event.pos())

                if (not self._last_socket.socket_widget.is_input or
                        (self._last_socket.socket_widget.is_input and not self._last_socket.has_edges())):
                    self._mode: str = "EDGE_ADD"
                    self._temp_edge: Edge = Edge(color=self._last_socket.color)
                    self._temp_edge.start_socket = self._last_socket

                    temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                    temp_target.setPen(QtGui.QPen(QtGui.QColor("black")))
                    temp_target.setBrush(self._last_socket.color)
                    temp_target.setPos(self._last_socket.parentItem().mapToScene(self._last_socket.center()))
                    temp_target.setZValue(-1)

                    self._temp_edge.end_socket = temp_target
                    self.scene().add_edge(self._temp_edge)

                if self._last_socket.socket_widget.is_input and self._last_socket.has_edges():
                    self._mode: str = "EDGE_EDIT"

                    self._temp_edge: Edge = self._last_socket.edges[-1]
                    connected_sockets: list[QtWidgets.QGraphicsItem] = [
                        self._temp_edge.start_socket,
                        self._temp_edge.end_socket
                    ]
                    for socket in connected_sockets:
                        socket.remove_edge(self._temp_edge)

                    temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                    temp_target.setPen(QtGui.QPen(QtGui.QColor("black")))
                    temp_target.setBrush(self._last_socket.color)
                    temp_target.setPos(self._last_socket.parentItem().mapToScene(self._last_socket.center()))
                    temp_target.setZValue(-1)

                    self._temp_edge.end_socket = temp_target
                    self._mode = "EDGE_ADD"

        if event.button() == QtCore.Qt.MiddleButton and self._mode == "":
            super().mousePressEvent(event)

            self._mode: str = "SCENE_DRAG"
            self._mm_pressed: bool = True
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeAllCursor)

        if event.button() == QtCore.Qt.RightButton and self._mode == "":
            # super().mousePressEvent(event)

            self._rm_pressed: bool = True
            if event.modifiers() == QtCore.Qt.ShiftModifier:
                self._mode: str = "EDGE_CUT"
                self._cutter: Cutter = Cutter(start=self._last_pos, end=self._last_pos)
                self.scene().addItem(self._cutter)
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)

        if self._mode == "EDGE_ADD":
            if type(self.itemAt(event.pos())) == Socket:
                snapping_pos: QtCore.QPointF = self.itemAt(event.pos()).parentItem().mapToScene(
                    self.itemAt(event.pos()).pos()
                )
                snap_x: float = snapping_pos.x() + self.itemAt(event.pos()).size / 2
                snap_y: float = snapping_pos.y() + self.itemAt(event.pos()).size / 2
                self._temp_edge.end_socket.setPos(snap_x, snap_y)
            else:
                self._temp_edge.end_socket.setPos(self.mapToScene(event.pos()))

        if self._mode == "SCENE_DRAG":
            current_pos: QtCore.QPoint = self.mapToScene(event.pos())
            pos_delta: QtCore.QPoint = current_pos - self._last_pos
            self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
            self.translate(pos_delta.x(), pos_delta.y())
            self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        if self._mode == "EDGE_CUT":
            current_pos: QtCore.QPoint = self.mapToScene(event.pos())
            self._cutter.end_point = current_pos

            selected_items: list[QtWidgets.QGraphicsItem] = self.scene().collidingItems(self._cutter)

            for item in selected_items:
                if type(item) is Edge:
                    connected_sockets: list[QtWidgets.QGraphicsItem] = [
                        item.start_socket,
                        item.end_socket
                    ]
                    for socket in connected_sockets:
                        socket.remove_edge(item)
                        socket.socket_widget.update_stylesheets()

                    self.scene().remove_edge(item)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        if self._mode == "EDGE_ADD":
            if type(self.itemAt(event.pos())) == Socket:
                self._temp_edge.end_socket = self.itemAt(event.pos())

                # Validate edge here!
                socket_type_start: object = self._temp_edge.start_socket.socket_widget.socket_type
                socket_type_end: object = self._temp_edge.end_socket.socket_widget.socket_type
                if socket_type_start == socket_type_end:
                    if self._temp_edge.start_socket.parentItem() is self._temp_edge.end_socket.parentItem():
                        # Sockets of the same node
                        self.scene().remove_edge(self._temp_edge)

                    elif (self._temp_edge.start_socket.socket_widget.is_input and
                          self._temp_edge.end_socket.socket_widget.is_input):
                        # Input with input socket
                        self.scene().remove_edge(self._temp_edge)

                    elif (not self._temp_edge.start_socket.socket_widget.is_input and
                          not self._temp_edge.end_socket.socket_widget.is_input):
                        # Output with output socket
                        self.scene().remove_edge(self._temp_edge)

                    else:
                        # Maybe valid connection ...
                        self._temp_edge.start_socket.add_edge(self._temp_edge)
                        self._temp_edge.end_socket.add_edge(self._temp_edge)
                        self._temp_edge.sort_sockets()
                        self._temp_edge.end_socket.socket_widget.update_stylesheets()

                        if self.scene().is_graph_cyclic():
                            # ... if not cyclic graph
                            connected_sockets: list[QtWidgets.QGraphicsItem] = [
                                self._temp_edge.start_socket,
                                self._temp_edge.end_socket
                            ]
                            for socket in connected_sockets:
                                socket.remove_edge(self._temp_edge)
                                socket.socket_widget.update_stylesheets()

                            self.scene().remove_edge(self._temp_edge)
                else:
                    # Incompatible socket types
                    self.scene().remove_edge(self._temp_edge)
            else:
                # No target socket
                self.scene().remove_edge(self._temp_edge)

            self._last_socket.socket_widget.update_stylesheets()

            for node in self.scene().graph_ends():
                dsk: dict = self.scene().graph_to_dict(node, {})
                print(get(dsk, node.socket_widgets[-1]))

        if self._mode == "EDGE_CUT":
            self.scene().removeItem(self._cutter)

        self._lm_pressed: bool = False
        self._mm_pressed: bool = False
        self._rm_pressed: bool = False
        self._mode: str = ""
        QtWidgets.QApplication.restoreOverrideCursor()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        event.accept()

        self._last_pos = self.mapToScene(event.pos())

        if event.angleDelta().y() > 0:
            if self._zoom_level < self._zoom_level_range[1]:
                self._zoom_level += 1
                self.scale(1.25, 1.25)
        else:
            if self._zoom_level > self._zoom_level_range[0]:
                self._zoom_level -= 1
                self.scale(1 / 1.25, 1 / 1.25)

        # Hack: Fixes the scene drifting while zooming
        drifted_pos: QtCore.QPoint = self.mapToScene(event.pos())
        pos_delta: QtCore.QPoint = drifted_pos - self._last_pos
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.translate(pos_delta.x(), pos_delta.y())
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # app.setStyle(QtWidgets.QStyleFactory().create("Fusion"))
    QtCore.QDir.addSearchPath('icon', os.path.abspath(os.path.dirname(__file__)))

    node_editor_scene: NodeEditorScene = NodeEditorScene()
    node_editor_view: NodeEditorView = NodeEditorView()

    node_editor_view.setScene(node_editor_scene)
    node_editor_view.resize(1200, 600)
    node_editor_view.show()

    node_1 = Node()
    node_1.setPos(QtCore.QPointF(31600, 31800))
    node_editor_scene.add_node(node_1)

    node_2 = Node()
    node_2.setPos(QtCore.QPointF(32200, 32050))
    node_editor_scene.add_node(node_2)

    node_3 = Node()
    node_3.setPos(QtCore.QPointF(31900, 32100))
    node_editor_scene.add_node(node_3)

    node_1_data: bytes = pickle.dumps(node_1, 2)
    node_1_copy: Node = pickle.loads(node_1_data)
    node_editor_scene.add_node(node_1_copy)

    sys.exit(app.exec_())

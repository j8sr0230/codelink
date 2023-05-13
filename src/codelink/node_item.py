from typing import Optional, Any

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_model import PropertyModel
from socket_widget import SocketWidget


class NodeItem(QtWidgets.QGraphicsItem):
    def __init__(self, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._prop_model: PropertyModel = PropertyModel(
            properties={"Class": self.__class__.__name__,
                        "Title": "Add",
                        "Color": QtGui.QColor("#232323"),
                        "Collapse State": False,
                        "X Pos": 5.1,
                        "Y Pos": 5.1
                        }
        )

        self._visited_count: int = 0
        self._evals: list[object] = [self.eval_socket_1, self.eval_socket_2]

        self._title: str = self._prop_model.properties["Title"]  # "NodeItem Name"
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
        self._is_collapsed: str = self._prop_model.properties["Collapse State"]  # False

        self._node_background_color: QtGui.QColor = QtGui.QColor("#303030")
        self._header_background_color: QtGui.QColor = QtGui.QColor("#1D1D1D")
        self._default_border_color: QtGui.QColor = QtGui.QColor("black")
        self._selected_border_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._font_color: QtGui.QColor = QtGui.QColor("#E5E5E5")

        self._default_border_pen: QtGui.QPen = QtGui.QPen(self._default_border_color)
        self._selected_border_pen: QtGui.QPen = QtGui.QPen(self._selected_border_color)
        self._selected_border_pen.setWidthF(1.5)

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
            QListView{
                border: none;
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
                min-width: 20px;
                min-height: 24px;
                padding-left: 5px;
                padding-right: 0px;
                padding-top: 0px;
                padding-bottom: 0px;
                margin: 0px;
                border: 0px;
                border-radius: 0px;
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

        self._prop_model.dataChanged.connect(lambda: self.update_title(self._prop_model.properties["Title"]))
        self._prop_model.dataChanged.connect(
            lambda: self.update_collapse_state(self._prop_model.properties["Collapse State"])
        )
        # lambda i, j: print(list(self._prop_model.properties.keys())[i.row()], "changed \n",
        #                    self._prop_model.properties)
        # lambda: self._title = self._prop_model.properties["Title"]
        # )

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
    def prop_model(self) -> QtCore.QAbstractTableModel:
        return self._prop_model

    @property
    def visited_count(self) -> int:
        return self._visited_count

    @visited_count.setter
    def visited_count(self, value: int) -> None:
        self._visited_count: int = value

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title: str = value

    def update_title(self, value: str) -> None:
        self._title: str = value
        self._title_item.setPlainText(
            self.crop_text(self._title, self._width - self._title_x - self._content_padding, self._font)
        )

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
    def is_collapsed(self) -> str:
        return self._is_collapsed

    def update_collapse_state(self, collapse_state: bool) -> None:
        if collapse_state:
            self._collapse_btn.setPixmap(self._collapse_pixmap_up)
            self._content_proxy.hide()
            self._height = self._min_height
        else:
            self._collapse_btn.setPixmap(self._collapse_pixmap_down)
            self._content_proxy.show()
            self._height = (self._header_height + self._content_padding + self._content_widget.height() +
                            self._content_padding)

        self._is_collapsed = collapse_state
        self.update_socket_positions()

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

    def predecessors(self) -> list['NodeItem']:
        result: list['NodeItem'] = []
        for socket_widget in self._socket_widgets:
            if socket_widget.is_input:
                for edge in socket_widget.socket.edges:
                    result.append(edge.start_socket.parentItem())
        return result

    def successors(self) -> list['NodeItem']:
        result: list['NodeItem'] = []
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

                    if self._prop_model.properties["Collapse State"]:
                        # noinspection PyTypeChecker
                        self._prop_model.setData(
                            self._prop_model.index(3, 1, QtCore.QModelIndex()), False, QtCore.Qt.EditRole
                        )
                    else:
                        # noinspection PyTypeChecker
                        self._prop_model.setData(
                            self._prop_model.index(3, 1, QtCore.QModelIndex()), True, QtCore.Qt.EditRole
                        )

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

    def contextMenuEvent(self, event: QtWidgets.QGraphicsSceneContextMenuEvent) -> None:
        super().contextMenuEvent(event)

        # self.setSelected(True)
        # self._prop_proxy.setGeometry(QtCore.QRectF(self._width + 10, 0, 200, 200))
        # self._prop_proxy.show()

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

    # def __getstate__(self) -> dict:
    #     print("NodeItem.__getstate__(self)")
    #
    #     state: dict = {
    #         "x": self.x(),
    #         "y": self.y(),
    #         "width": self._width,
    #         "is_collapsed": self._is_collapsed
    #     }
    #
    #     return state
    #
    # def __setstate__(self, state: dict):
    #     print("NodeItem.__setstate__(self, state: dict)", repr(state))
    #
    #     self.__init__(parent=None)
    #     # self.setPos(QtCore.QPointF(state["x"], state["y"]))
    #     self.setPos(QtCore.QPointF(32500, 31800))
    #     self._width = state["width"]
    #     self._is_collapsed = state["is_collapsed"]

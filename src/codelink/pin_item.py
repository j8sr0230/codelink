from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

if TYPE_CHECKING:
    from node_item import NodeItem
    from socket_widget import SocketWidget
    from edge_item import EdgeItem


class PinItem(QtWidgets.QGraphicsItem):
    def __init__(self, pin_type: type, color: QtGui.QColor, socket_widget: Optional[SocketWidget],
                 parent_node: Optional[NodeItem] = None) -> None:
        super().__init__(parent_node)

        # Non persistent data model
        self._pin_type: type = pin_type
        self._color: QtGui.QColor = QtGui.QColor(color)
        self._socket_widget: Optional[SocketWidget] = socket_widget
        self._parent_widget: Optional[NodeItem] = parent_node
        self._edges: list[EdgeItem] = []

        # Pin geometry
        self._size: int = 12

        # Widget setup
        self.setAcceptHoverEvents(True)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

    @property
    def pin_type(self) -> type:
        return self._pin_type

    @pin_type.setter
    def pin_type(self, value: type) -> None:
        self._pin_type: type = value

    @property
    def color(self) -> QtGui.QColor:
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        self._color: QtGui.QColor = QtGui.QColor(value)

    @property
    def socket_widget(self) -> Optional[SocketWidget]:
        return self._socket_widget

    @property
    def parent_node(self) -> Optional[NodeItem]:
        return self.parentItem()

    @property
    def edges(self) -> list[EdgeItem]:
        return self._edges

    @edges.setter
    def edges(self, value: list[EdgeItem]) -> None:
        self._edges: list[EdgeItem] = value

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size: int = value

    def center(self) -> QtCore.QPointF:
        return QtCore.QPointF(
            self.x() + self._size / 2,
            self.y() + self._size / 2,
        )

    def uuid(self) -> tuple[str, int]:
        return self.parent_node.uuid, self.parent_node.socket_widgets.index(self._socket_widget)

    # --------------- Edge editing ---------------

    def add_edge(self, edge: EdgeItem) -> None:
        if edge not in self._edges:
            self._edges.append(edge)

    def remove_edge(self, edge: EdgeItem) -> None:
        if edge in self._edges:
            self._edges.remove(edge)

    def has_edges(self) -> bool:
        return len(self._edges) > 0

    # --------------- Overwrites ---------------

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverEnterEvent(event)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        print(self._edges)
        print(self._socket_widget.link)

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverLeaveEvent(event)
        QtWidgets.QApplication.restoreOverrideCursor()

    # --------------- Shape and painting ---------------

    def boundingRect(self) -> QtCore.QRectF:
        # return QtCore.QRectF(0, 0, self._size, self._size)
        return QtCore.QRectF(-self._size, -self._size, 3 * self._size, 3 * self._size)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtGui.QPen(QtGui.QColor("black")))
        painter.setBrush(QtGui.QBrush(self._color))
        # painter.drawEllipse(self.boundingRect())  # Visualises snapping area
        painter.drawEllipse(0, 0, self._size, self._size)

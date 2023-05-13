from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class SocketItem(QtWidgets.QGraphicsItem):
    def __init__(self, color: QtGui.QColor, socket_widget: Optional['SocketWidget'],
                 parent_node: Optional['NodeItem'] = None) -> None:
        super().__init__(parent_node)

        self._color: QtGui.QColor = QtGui.QColor(color)
        self._socket_widget: Optional['SocketWidget'] = socket_widget

        self._edges: list['EdgeItem'] = []

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
    def edges(self) -> list['EdgeItem']:
        return self._edges

    @edges.setter
    def edges(self, value: list['EdgeItem']) -> None:
        self._edges: list[Edge] = value

    @property
    def size(self) -> int:
        return self._size

    def add_edge(self, edge: 'EdgeItem') -> None:
        self._edges.append(edge)

    def remove_edge(self, edge: 'EdgeItem') -> None:
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
from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from pin_item import PinItem


class EdgeItem(QtWidgets.QGraphicsPathItem):
    def __init__(self, color: QtGui.QColor = QtGui.QColor("#E5E5E5"),
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._color: QtGui.QColor = color

        self._start_pin: Optional[QtWidgets.QGraphicsItem] = None
        self._end_pin: Optional[QtWidgets.QGraphicsItem] = None

        self.setAcceptHoverEvents(True)
        self.setZValue(-1)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

    @property
    def start_pin(self) -> QtWidgets.QGraphicsItem:
        return self._start_pin

    @start_pin.setter
    def start_pin(self, value: QtWidgets.QGraphicsItem) -> None:
        self._start_pin: QtWidgets.QGraphicsItem = value

    @property
    def end_pin(self) -> QtWidgets.QGraphicsItem:
        return self._end_pin

    @end_pin.setter
    def end_pin(self, value: QtWidgets.QGraphicsItem) -> None:
        self._end_pin: QtWidgets.QGraphicsItem = value

    def sort_pins(self) -> None:
        old_start_socket: QtWidgets.QGraphicsItem = self._start_pin

        if old_start_socket.socket_widget.is_input:
            self._start_pin: QtWidgets.QGraphicsItem = self._end_pin
            self._end_pin: QtWidgets.QGraphicsItem = old_start_socket

    def path(self) -> QtGui.QPainterPath:
        start_point: QtCore.QPointF = self._start_pin.parentItem().mapToScene(self._start_pin.center())

        if type(self._end_pin) == PinItem:
            end_point: QtCore.QPointF = self._end_pin.parentItem().mapToScene(self._end_pin.center())
        else:
            end_point: QtCore.QPointF = self._end_pin.pos()

        ctr_pt_offset: float = abs(end_point.x() - start_point.x()) / 2.5

        if not self._start_pin.socket_widget.is_input:
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

    def __getstate__(self) -> dict:
        data_dict: dict = {
            "Start Node Idx": self.scene().nodes.index(self._start_pin.parentItem()),
            "Start Socket Idx": self._start_pin.parentItem().socket_widgets.index(self._start_pin.socket_widget),
            "End Node Idx": self.scene().nodes.index(self._end_pin.parentItem()),
            "End Socket Idx": self._end_pin.parentItem().socket_widgets.index(self._end_pin.socket_widget)
        }
        return data_dict

    def __setstate__(self, state):
        start_node: 'NodeItem' = self.scene().nodes[state["Start Node Idx"]]
        self._start_pin: PinItem = start_node.socket_widgets[state["Start Socket Idx"]].pin

        end_node: 'NodeItem' = self.scene().nodes[state["End Node Idx"]]
        self._end_pin: PinItem = end_node.socket_widgets[state["End Socket Idx"]].pin

        self._start_pin.add_edge(self)
        self._end_pin.add_edge(self)
        self.end_pin.socket_widget.update_stylesheets()
        self._color: QtGui.QColor = self._start_pin.color

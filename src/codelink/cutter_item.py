from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class CutterItem(QtWidgets.QGraphicsPathItem):
    def __init__(self, start: QtCore.QPointF = QtCore.QPointF(), end: QtCore.QPointF = QtCore.QPointF(),
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        # Non persistent data model
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

    # --------------- Shape and painting ---------------

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

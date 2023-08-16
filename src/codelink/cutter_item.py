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

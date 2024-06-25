#!/usr/bin/env python

# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2024 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
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

from codelink.frontend.color_palette import ColorPalette


class EdgeGrItem(QtWidgets.QGraphicsPathItem):
    def __init__(self, start: QtWidgets.QGraphicsItem, end: QtWidgets.QGraphicsItem,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._start: QtWidgets.QGraphicsEllipseItem = start
        self._end: QtWidgets.QGraphicsEllipseItem = end

        self._default_color: QtGui.QColor = QtGui.QColor(ColorPalette.REGULARGRAY)
        self._selected_color: QtGui.QColor = QtGui.QColor(ColorPalette.HIGHLIGHT)
        self._pen: QtGui.QPen = QtGui.QPen(self._default_color)
        self._pen.setWidthF(2.0)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setZValue(1)

    @property
    def start(self) -> QtWidgets.QGraphicsItem:
        return self._start

    @start.setter
    def start(self, value: QtWidgets.QGraphicsItem) -> None:
        self._start: QtWidgets.QGraphicsItem = value

    @property
    def end(self) -> QtWidgets.QGraphicsItem:
        return self._end

    @end.setter
    def end(self, value: QtWidgets.QGraphicsItem) -> None:
        self._end: QtWidgets.QGraphicsItem = value

    def path(self) -> QtGui.QPainterPath:
        start_point: QtCore.QPointF = self.mapToScene(self._start.pos())
        if self._start.parentItem():
            start_point: QtCore.QPointF = self._start.parentItem().mapToScene(self._start.pos())

        end_point: QtCore.QPointF = self.mapToScene(self._end.pos())
        if self._end.parentItem():
            end_point: QtCore.QPointF = self._end.parentItem().mapToScene(self._end.pos())

        path: QtGui.QPainterPath = QtGui.QPainterPath(start_point)
        path.lineTo(end_point)

        return path

    def shape(self) -> QtGui.QPainterPath:
        return self.path()

    def boundingRect(self) -> QtCore.QRectF:
        return self.path().boundingRect()

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        self._pen.setColor(self._default_color)
        if self.isSelected():
            self._pen.setColor(self._selected_color)

        painter.setPen(self._pen)
        painter.drawPath(self.path())

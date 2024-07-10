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
    def __init__(self, source: QtWidgets.QGraphicsItem, destination: QtWidgets.QGraphicsItem,
                 persistent_index: QtCore.QPersistentModelIndex = QtCore.QPersistentModelIndex(),
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._persistent_index: Optional[QtCore.QPersistentModelIndex] = persistent_index
        self._source: QtWidgets.QGraphicsEllipseItem = source
        self._destination: QtWidgets.QGraphicsEllipseItem = destination

        self._is_invalid: bool = False

        self._default_color: QtGui.QColor = QtGui.QColor(ColorPalette.REGULARGRAY)
        self._selected_color: QtGui.QColor = QtGui.QColor(ColorPalette.HIGHLIGHT)
        self._invalid_color: QtGui.QColor = QtGui.QColor("red")
        self._pen: QtGui.QPen = QtGui.QPen(self._default_color)
        self._pen.setWidthF(2.0)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setZValue(1)

    @property
    def persistent_index(self) -> QtCore.QPersistentModelIndex:
        return self._persistent_index

    @property
    def source(self) -> QtWidgets.QGraphicsItem:
        return self._source

    @source.setter
    def source(self, value: QtWidgets.QGraphicsItem) -> None:
        self._source: QtWidgets.QGraphicsItem = value

    @property
    def destination(self) -> QtWidgets.QGraphicsItem:
        return self._destination

    @destination.setter
    def destination(self, value: QtWidgets.QGraphicsItem) -> None:
        self._destination: QtWidgets.QGraphicsItem = value

    @property
    def is_invalid(self) -> bool:
        return self._is_invalid

    @is_invalid.setter
    def is_invalid(self, value: bool) -> None:
        self._is_invalid: bool = value

    def index(self) -> QtCore.QModelIndex:
        if not self._persistent_index.isValid():
            return QtCore.QModelIndex()

        return QtCore.QModelIndex(self._persistent_index)

    def path(self) -> QtGui.QPainterPath:
        start_point: QtCore.QPointF = self.mapToScene(self._source.pos())
        if self._source.parentItem():
            start_point: QtCore.QPointF = self._source.parentItem().mapToScene(self._source.pos())

        end_point: QtCore.QPointF = self.mapToScene(self._destination.pos())
        if self._destination.parentItem():
            end_point: QtCore.QPointF = self._destination.parentItem().mapToScene(self._destination.pos())

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

        elif self._is_invalid:
            self._pen.setColor(self._invalid_color)

        painter.setPen(self._pen)
        painter.drawPath(self.path())

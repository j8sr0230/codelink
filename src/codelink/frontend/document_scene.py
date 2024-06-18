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

import math

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.frontend.color_palette import ColorPalette


class DocumentScene(QtWidgets.QGraphicsScene):
    def __init__(self) -> None:
        super().__init__()

        self._background_color: QtGui.QColor = QtGui.QColor(ColorPalette.PALEGRAY)
        self._background_brush: QtGui.QBrush = QtGui.QBrush(self._background_color)

        self._grid_color: QtGui.QColor = QtGui.QColor(ColorPalette.LIGHTGRAY)
        self._grid_brush: QtGui.QBrush = QtGui.QBrush(self._grid_color)
        self._grid_pen: QtGui.QPen = QtGui.QPen(self._grid_color)
        self._grid_pen.setWidth(0)
        self._grid_spacing: int = 50
        self._grid_radius: int = 2

        self._scene_width: int = 32000
        self.setSceneRect(-self._scene_width // 2, -self._scene_width // 2, self._scene_width, self._scene_width)

        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
        self.setSortCacheEnabled(False)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)
        self.setBackgroundBrush(self._background_brush)

        painter.setBrush(self._grid_brush)
        painter.setPen(self._grid_pen)

        bound_box_left: int = int(math.floor(rect.left()))
        bound_box_right: int = int(math.ceil(rect.right()))
        bound_box_top: int = int(math.floor(rect.top()))
        bound_box_bottom: int = int(math.ceil(rect.bottom()))

        first_left: int = bound_box_left - (bound_box_left % self._grid_spacing)
        first_top: int = bound_box_top - (bound_box_top % self._grid_spacing)

        # points: list[Optional[QtCore.QPoint]] = []
        for x in range(first_left, bound_box_right, self._grid_spacing):
            for y in range(first_top, bound_box_bottom, self._grid_spacing):
                # points.append(QtCore.QPoint(x, y))
                painter.drawEllipse(QtCore.QPoint(x, y), self._grid_radius, self._grid_radius)

        # painter.setPen(self._grid_pen)
        # painter.drawPoints(points)

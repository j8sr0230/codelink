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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from codelink.frontend.color_palette import ColorPalette

if TYPE_CHECKING:
    from codelink.frontend.node_gr_item import NodeGrItem


class PinGrItem(QtWidgets.QGraphicsItem):
    def __init__(self, color: str, parent: Optional[NodeGrItem] = None) -> None:
        super().__init__(parent)

        self._background_color: QtGui.QColor = QtGui.QColor(color)
        self._border_color: QtGui.QColor = QtGui.QColor(ColorPalette.DOUBLEDARKGRAY)
        self._brush: QtGui.QBrush = QtGui.QBrush(QtGui.QColor(self._background_color))
        self._pen: QtGui.QPen = QtGui.QPen(self._border_color)

        self._size: int = 10
        self._snap_factor: int = 5

        self.setZValue(2)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(
            -self._snap_factor * (self._size // 2), -self._size // 2,
            self._snap_factor * self._size, self._size
        )

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawEllipse(-self._size // 2, -self._size // 2, self._size, self._size)
        # painter.drawRect(self.boundingRect())
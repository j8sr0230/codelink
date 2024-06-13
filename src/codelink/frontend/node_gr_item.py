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
from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class NodeGrItem(QtWidgets.QGraphicsItem):
    def __init__(self, index: QtCore.QModelIndex, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._index: QtCore.QModelIndex = index

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, 120, 80)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("red")))
        painter.drawRoundedRect(self.boundingRect(), self._corner_radius, self._corner_radius)

        # rect: QtCore.QRectF = QtCore.QRectF(0, 0, self._prop_model.properties["Width"], self._header_height)
        # painter.setBrush(QtGui.QColor(self._prop_model.properties["Color"]))
        # # painter.drawRoundedRect(rect, self._corner_radius, self._corner_radius)
        # painter.drawRect(rect)
        #
        # painter.setBrush(QtCore.Qt.NoBrush)
        # if self.isSelected():
        #     painter.setPen(self._selected_border_pen)
        # elif self._is_dirty:
        #     painter.setPen(self._dirty_border_color)
        # elif self._is_invalid:
        #     painter.setPen(self._invalid_border_color)
        # else:
        #     painter.setPen(self._default_border_pen)
        # # painter.drawRoundedRect(self.boundingRect(), self._corner_radius, self._corner_radius)
        # painter.drawRect(self.boundingRect())

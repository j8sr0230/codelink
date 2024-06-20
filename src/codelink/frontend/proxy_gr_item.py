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


class ProxyGrItem(QtWidgets.QGraphicsProxyWidget):
    def __init__(self, parent: Optional[QtWidgets.QGraphicsItem] = None,
                 w_flags: Optional[QtCore.Qt.WindowFlags] = None) -> None:
        super().__init__(parent, w_flags)

        self._is_selected: bool = False
        self._cached_pix_map: Optional[QtGui.QPixmap] = None

    @property
    def is_selected(self) -> bool:
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value: bool) -> None:
        if not value:
            self.update_cache()
        self._is_selected: bool = value

    def update_cache(self) -> None:
        self._cached_pix_map: QtGui.QPixmap = QtGui.QPixmap(QtCore.QSize(self.widget().size()))
        self.widget().render(self._cached_pix_map)

    def setWidget(self, widget: QtWidgets.QWidget) -> None:
        super().setWidget(widget)
        self.update_cache()

    def setGeometry(self, rect: QtCore.QRectF) -> None:
        super().setGeometry(rect)
        self.update_cache()

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: QtWidgets.QWidget) -> None:
        if self._is_selected:
            super().paint(painter, option, widget)
        else:
            painter.drawPixmap(QtCore.QPoint(0, 0), self._cached_pix_map)

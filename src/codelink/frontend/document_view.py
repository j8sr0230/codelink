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

from typing import Optional, Any

import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.frontend.graphics_scene import GraphicsScene


class DocumentView(QtWidgets.QWidget):
    def __init__(self, file_name: str = "untitled", parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle(file_name)
        self.setLayout(QtWidgets.QVBoxLayout())

        self._graphics_view: QtWidgets.QGraphicsView = QtWidgets.QGraphicsView()
        self._graphics_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self._graphics_view.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self._graphics_view.setScene(GraphicsScene())

        self.layout().addWidget(self._graphics_view)

    @staticmethod
    def update_view(data: Any) -> None:
        print(f"Data: {data}")

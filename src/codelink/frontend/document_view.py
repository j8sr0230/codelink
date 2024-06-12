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
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.document_model import DocumentModel
from codelink.frontend.document_scene import DocumentScene


class DocumentView(QtWidgets.QWidget):
    def __init__(self, model: DocumentModel, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self._model: DocumentModel = model

        self.setLayout(QtWidgets.QVBoxLayout())
        self._graphics_view: QtWidgets.QGraphicsView = QtWidgets.QGraphicsView()
        self._graphics_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self._graphics_view.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self._graphics_view.setScene(DocumentScene())
        self.layout().addWidget(self._graphics_view)

    @property
    def model(self) -> DocumentModel:
        return self._model

    # noinspection PyUnusedLocal
    def on_model_data_changed(self, top_left: QtCore.QModelIndex, bottom_right: QtCore.QModelIndex,
                              roles: list[int]) -> None:
        print("Changed at:", top_left.row(), top_left.column(), "to:",
              top_left.data(roles[0]) if len(roles) > 0 else None)

        self._model.is_modified = True
        self.update()

    # noinspection PyUnusedLocal
    def on_model_row_changed(self, parent: QtCore.QModelIndex, first_row: QtCore.QModelIndex,
                             last_row: QtCore.QModelIndex) -> None:
        print("Inserted/Removed at:", first_row)
        self._model.is_modified = True
        self.update()

    def update(self) -> None:
        super().update()
        self.setWindowTitle(self._model.get_title())

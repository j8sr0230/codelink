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

from codelink.backend.tree_model import TreeModel
from codelink.frontend.graphics_scene import GraphicsScene


class DocumentView(QtWidgets.QWidget):
    def __init__(self, model: TreeModel, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self._model: TreeModel = model
        self._model.rowsInserted.connect(self.on_model_row_changed)
        self._model.rowsRemoved.connect(self.on_model_row_changed)
        self._model.dataChanged.connect(self.on_model_data_changed)

        self._file_name: Optional[str] = None
        self._is_modified: bool = False

        self.setLayout(QtWidgets.QVBoxLayout())
        self._graphics_view: QtWidgets.QGraphicsView = QtWidgets.QGraphicsView()
        self._graphics_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self._graphics_view.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self._graphics_view.setScene(GraphicsScene())
        self.layout().addWidget(self._graphics_view)

    @property
    def model(self) -> TreeModel:
        return self._model

    @property
    def file_name(self) -> Optional[str]:
        return self._file_name

    @file_name.setter
    def file_name(self, value: Optional[str]) -> None:
        self._file_name: Optional[str] = value

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @is_modified.setter
    def is_modified(self, value: bool) -> None:
        self._is_modified: bool = value

    def get_title(self) -> str:
        title: str = self._file_name if self._file_name else "untitled"
        title: str = title + "*" if self._is_modified else title
        return title

    # noinspection PyUnusedLocal
    def on_model_data_changed(self, top_left: QtCore.QModelIndex, bottom_right: QtCore.QModelIndex,
                              roles: list[int]) -> None:
        print("Changed at:", top_left.row(), top_left.column(), "to:",
              top_left.data(roles[0]) if len(roles) > 0 else None)

        self._is_modified: bool = True
        self.update()

    # noinspection PyUnusedLocal
    def on_model_row_changed(self, parent: QtCore.QModelIndex, first_row: QtCore.QModelIndex,
                             last_row: QtCore.QModelIndex) -> None:
        print("Inserted/Removed at:", first_row)
        self._is_modified: bool = True
        self.update()

    def update(self) -> None:
        super().update()
        self.setWindowTitle(self.get_title())

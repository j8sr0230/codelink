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
from pathlib import Path

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.document_model import DocumentModel
from codelink.frontend.document_gr_view import DocumentGrView
from codelink.frontend.document_scene import DocumentScene


class DocumentView(QtWidgets.QWidget):
    def __init__(self, model: DocumentModel, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self._model: DocumentModel = model

        self.setLayout(QtWidgets.QVBoxLayout())

        self._document_gr_view: DocumentGrView = DocumentGrView(model)
        self._document_gr_view.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self._document_scene: DocumentScene = DocumentScene()
        self._document_gr_view.setScene(self._document_scene)

        self.layout().addWidget(self._document_gr_view)
        self.layout().setMargin(0)
        self.layout().setSpacing(0)

    @property
    def model(self) -> DocumentModel:
        return self._model

    @property
    def document_gr_view(self) -> DocumentGrView:
        return self._document_gr_view

    # noinspection PyUnusedLocal
    def on_model_rows_inserted(self, parent: QtCore.QModelIndex, first_row: int, last_row: int) -> None:
        self._model.modified = True
        self.update()

        self._document_gr_view.on_model_rows_inserted(parent, first_row, last_row)

    # noinspection PyUnusedLocal
    def on_model_begin_remove_rows(self, parent: QtCore.QModelIndex, first_row: int, last_row: int) -> None:
        self._model.modified = True
        self.update()

        self._document_gr_view.on_model_begin_remove_rows(parent, first_row, last_row)

    # noinspection PyUnusedLocal
    def on_model_data_changed(self, top_left: QtCore.QModelIndex, bottom_right: QtCore.QModelIndex,
                              roles: list[int]) -> None:
        self._model.modified = True
        self.update()

        self._document_gr_view.on_model_data_changed(top_left, bottom_right, roles)

    def update(self) -> None:
        super().update()
        file_name: Optional[str] = Path(self._model.get_pretty_file_name()).name
        title: str = file_name + "*" if self._model.modified else file_name
        self.setWindowTitle(title)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self._model.modified:
            reply: QtWidgets.QMessageBox.StandardButton = QtWidgets.QMessageBox.question(
                self, "Message", "Are you sure to quit? Any unsaved changes will be lost.",
                QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,
                QtWidgets.QMessageBox.Cancel
            )

            if reply == QtWidgets.QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()

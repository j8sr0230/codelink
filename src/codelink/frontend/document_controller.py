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

from typing import Any

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from codelink.backend.tree_model import TreeModel
from codelink.frontend.document_view import DocumentView


class DocumentController:
    def __init__(self, model: TreeModel, view: DocumentView) -> None:
        self._doc_model: TreeModel = model
        self._doc_view: DocumentView = view

        self._doc_model.rowsInserted.connect(self.on_model_row_changed)
        self._doc_model.rowsRemoved.connect(self.on_model_row_changed)
        self._doc_model.dataChanged.connect(self.on_model_data_changed)

    @property
    def doc_model(self) -> TreeModel:
        return self._doc_model

    @property
    def doc_view(self) -> DocumentView:
        return self._doc_view

    def handle_input(self, data: Any) -> None:
        self._doc_model.setData(QtCore.QModelIndex(), data)

    # noinspection PyUnusedLocal
    def on_model_data_changed(self, top_left: QtCore.QModelIndex, bottom_right: QtCore.QModelIndex,
                              roles: list[int]) -> None:
        window_title: str = self._doc_view.windowTitle()
        if not window_title.endswith("*"):
            self._doc_view.setWindowTitle(window_title + "*")

        print("Changed at:", top_left.row(), top_left.column(), "to:",
              top_left.data(roles[0]) if len(roles) > 0 else None)

    # noinspection PyUnusedLocal
    def on_model_row_changed(self, parent: QtCore.QModelIndex, first_row: QtCore.QModelIndex,
                             last_row: QtCore.QModelIndex) -> None:
        window_title: str = self._doc_view.windowTitle()
        if not window_title.endswith("*"):
            self._doc_view.setWindowTitle(window_title + "*")

        print("Inserted/Removed at:", first_row)

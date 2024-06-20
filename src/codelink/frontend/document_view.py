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

from typing import TYPE_CHECKING, Optional, cast
from pathlib import Path

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.document_model import DocumentModel
from codelink.backend.node_item import NodeItem
from codelink.frontend.document_gr_view import DocumentGrView
from codelink.frontend.document_scene import DocumentScene
from codelink.frontend.node_gr_item import NodeGrItem

if TYPE_CHECKING:
    from codelink.backend.tree_item import TreeItem


class DocumentView(QtWidgets.QWidget):
    selection_changed: QtCore.Signal = QtCore.Signal(list)

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

        self._document_scene.selectionChanged.connect(self.on_scene_selection_changed)

    @property
    def model(self) -> DocumentModel:
        return self._model

    def graphics_item_from_index(self, index: QtCore.QModelIndex) -> Optional[QtWidgets.QGraphicsItem]:
        graphics_items: list[QtWidgets.QGraphicsItem] = []
        for graphics_item in self._document_gr_view.scene().items():
            if hasattr(graphics_item, "index"):
                if graphics_item.index() == index or self._model.has_parent_recursively(index, graphics_item.index()):
                    graphics_items.append(graphics_item)

        if len(graphics_items) > 0:
            return graphics_items[0]
        else:
            return None

    # noinspection PyUnusedLocal
    def on_model_rows_inserted(self, parent: QtCore.QModelIndex, first_row: int, last_row: int) -> None:
        # print("Inserted at:", first_row)
        self._model.is_modified = True
        self.update()

        index: QtCore.QModelIndex = self._model.index(first_row, 0, parent)
        item: TreeItem = self._model.item_from_index(index)
        if isinstance(item, NodeItem):
            node_gr_item: NodeGrItem = NodeGrItem(QtCore.QPersistentModelIndex(index))
            self._document_gr_view.scene().addItem(node_gr_item)
            node_gr_item.update()

    # noinspection PyUnusedLocal
    def on_model_begin_remove_rows(self, parent: QtCore.QModelIndex, first_row: int, last_row: int) -> None:
        # print("Removed at:", first_row)
        self._model.is_modified = True
        self.update()

        index: QtCore.QModelIndex = self._model.index(first_row, 0, parent)
        gr_item: Optional[QtWidgets.QGraphicsItem] = self.graphics_item_from_index(index)
        if gr_item:
            self._document_gr_view.scene().removeItem(gr_item)

    # noinspection PyUnusedLocal
    def on_model_data_changed(self, top_left: QtCore.QModelIndex, bottom_right: QtCore.QModelIndex,
                              roles: list[int]) -> None:
        # print("Changed at:", top_left.row(), top_left.column(), "to:",
        #       top_left.data(roles[0]) if len(roles) > 0 else None)
        self._model.is_modified = True
        self.update()

        gr_item: Optional[QtWidgets.QGraphicsItem] = self.graphics_item_from_index(top_left)
        if gr_item:
            gr_item.update()

    def on_scene_selection_changed(self):
        selected_indexes: list[QtCore.QModelIndex] = [item.index() for item in self._document_scene.selectedItems()]
        cast(QtCore.SignalInstance, self.selection_changed).emit(selected_indexes)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self._model.is_modified:
            reply: QtWidgets.QMessageBox.StandardButton = QtWidgets.QMessageBox.question(
                self, "Message", "Are you sure to quit? Any unsaved changes will be lost.",
                QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,
                QtWidgets.QMessageBox.Cancel
            )

            if reply == QtWidgets.QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()

    def update(self) -> None:
        super().update()
        file_name: Optional[str] = Path(self._model.get_pretty_file_name()).name
        title: str = file_name + "*" if self._model.is_modified else file_name
        self.setWindowTitle(title)

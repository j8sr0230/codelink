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

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from codelink.backend.user_roles import UserRoles
from codelink.backend.document_model import DocumentModel
from codelink.backend.node_item import NodeItem
from codelink.backend.edge_item import EdgeItem
from codelink.frontend.node_gr_item import NodeGrItem
from codelink.frontend.pin_gr_item import PinGrItem
from codelink.frontend.edge_gr_item import EdgeGrItem

if TYPE_CHECKING:
    from codelink.backend.tree_item import TreeItem


class DocumentGrView(QtWidgets.QGraphicsView):
    selection_changed: QtCore.Signal = QtCore.Signal(QtCore.QItemSelection)

    def __init__(self, model: DocumentModel, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self._model: DocumentModel = model

        self._lm_pressed: bool = False
        self._mm_pressed: bool = False
        self._rm_pressed: bool = False

        self._pressed_pin: Optional[QtWidgets.QGraphicsEllipseItem] = None
        self._temp_edge: Optional[EdgeGrItem] = None

    def graphics_item_from_index(self, index: QtCore.QModelIndex) -> Optional[QtWidgets.QGraphicsItem]:
        graphics_items: list[QtWidgets.QGraphicsItem] = []
        for graphics_item in self.scene().items():
            if hasattr(graphics_item, "index"):
                if graphics_item.index() == index or self._model.has_parent_recursively(index, graphics_item.index()):
                    graphics_items.append(graphics_item)

        if len(graphics_items) > 0:
            return graphics_items[0]
        else:
            return None

    def select(self, item_selection: QtCore.QItemSelection):
        self.scene().clearSelection()
        for index in item_selection.indexes():
            gr_item: QtWidgets.QGraphicsItem = self.graphics_item_from_index(cast(QtCore.QModelIndex, index))
            if gr_item:
                gr_item.setSelected(True)

    # noinspection PyUnusedLocal
    def on_model_rows_inserted(self, parent: QtCore.QModelIndex, first_row: int, last_row: int) -> None:
        index: QtCore.QModelIndex = self._model.index(first_row, 0, parent)
        item: TreeItem = self._model.item_from_index(index)
        if isinstance(item, NodeItem):
            node_gr_item: NodeGrItem = NodeGrItem(QtCore.QPersistentModelIndex(index))
            self.scene().addItem(node_gr_item)
            node_gr_item.update()

        elif type(item) == EdgeItem:
            edge_item: EdgeItem = cast(EdgeItem, item)

            source_index: QtCore.QModelIndex = self._model.index_from_uuid(edge_item.source_uuid)
            source_node_index: QtCore.QModelIndex = source_index.parent().parent()
            source_node_gr_item: NodeGrItem = self.graphics_item_from_index(source_node_index)
            source_pin_row: int = source_index.parent().row() - 1
            source_pin: PinGrItem = source_node_gr_item.pins[1][source_index.row()]

            destination_index: QtCore.QModelIndex = self._model.index_from_uuid(edge_item.destination_uuid)
            destination_node_index: QtCore.QModelIndex = destination_index.parent().parent()
            destination_node_gr_item: NodeGrItem = self.graphics_item_from_index(destination_node_index)
            destination_pin_row: int = destination_index.parent().row() - 1
            destination_pin: PinGrItem = destination_node_gr_item.pins[0][destination_index.row()]

            self.scene().addItem(EdgeGrItem(source_pin, destination_pin, QtCore.QPersistentModelIndex(index)))

    # noinspection PyUnusedLocal
    def on_model_begin_remove_rows(self, parent: QtCore.QModelIndex, first_row: int, last_row: int) -> None:
        index: QtCore.QModelIndex = self._model.index(first_row, 0, parent)
        gr_item: Optional[QtWidgets.QGraphicsItem] = self.graphics_item_from_index(index)
        if gr_item:
            self.scene().removeItem(gr_item)

    # noinspection PyUnusedLocal
    def on_model_data_changed(self, top_left: QtCore.QModelIndex, bottom_right: QtCore.QModelIndex,
                              roles: list[int]) -> None:
        gr_item: Optional[QtWidgets.QGraphicsItem] = self.graphics_item_from_index(top_left)
        if gr_item:
            gr_item.update()

    def on_selection_changed(self):
        selected_indexes: list[QtCore.QModelIndex] = [item.index() for item in self.scene().selectedItems()]

        item_selection: QtCore.QItemSelection = QtCore.QItemSelection()
        for index in selected_indexes:
            item_selection.select(index, index)
        cast(QtCore.SignalInstance, self.selection_changed).emit(item_selection)

    def setScene(self, scene: QtWidgets.QGraphicsScene) -> None:
        super().setScene(scene)
        scene.selectionChanged.connect(self.on_selection_changed)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:

        if event.button() == QtCore.Qt.LeftButton:
            self._lm_pressed: bool = True

            if type(self.itemAt(event.pos())) == PinGrItem:
                self._pressed_pin: PinGrItem = self.itemAt(event.pos())
                self._temp_edge: EdgeGrItem = EdgeGrItem(self._pressed_pin, self._pressed_pin)
                self.scene().addItem(self._temp_edge)

            else:
                super().mousePressEvent(event)

        elif event.button() == QtCore.Qt.MiddleButton:
            super().mousePressEvent(event)
            self._mm_pressed: bool = True

        else:
            super().mousePressEvent(event)
            self._rm_pressed: bool = True

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:

        if self._lm_pressed and self._pressed_pin and self._temp_edge:
            temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(QtCore.QRect(-1, -1, 2, 2))
            self._temp_edge.destination = temp_target
            temp_target.setPos(self.mapToScene(event.pos()))

            if type(self.itemAt(event.pos())) == PinGrItem:
                pin_gr_item: PinGrItem = cast(PinGrItem, self.itemAt(event.pos()))
                # TODO: Add EdgeValidator class on the base of NetworkX
                temp_target.setPos(pin_gr_item.parentItem().mapToScene(pin_gr_item.pos().toPoint()))

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            for item in self.scene().selectedItems():
                if hasattr(item, "moved") and item.moved:
                    item: NodeGrItem = cast(NodeGrItem, item)
                    pos: QtCore.QPoint = item.pos()
                    pos: list[int] = [pos.x(), pos.y()]
                    self._model.setData(item.index(), pos, UserRoles.POS)
                    item.moved = False

            if type(self.itemAt(event.pos())) == PinGrItem:
                pressed_index: QtCore.QModelIndex = QtCore.QModelIndex(self._pressed_pin.data(0))
                pressed_uuid: str = self._model.data(pressed_index, UserRoles.UUID)

                released_pin: PinGrItem = cast(PinGrItem, self.itemAt(event.pos()))
                released_index: QtCore.QModelIndex = QtCore.QModelIndex(released_pin.data(0))
                released_uuid: str = self._model.data(released_index, UserRoles.UUID)

                if self._model.is_input(pressed_index) and self._model.is_output(released_index):
                    temp_uuid: str = released_uuid
                    released_uuid: str = pressed_uuid
                    pressed_uuid: str = temp_uuid

                self._model.append_edge(pressed_uuid, released_uuid)

            self.scene().removeItem(self._temp_edge)
            self._temp_edge: Optional[EdgeGrItem] = None
            self._pressed_pin: Optional[QtWidgets.QGraphicsEllipseItem] = None
            self._lm_pressed: bool = False

        elif event.button() == QtCore.Qt.MiddleButton:
            self._mm_pressed: bool = False

        else:
            self._rm_pressed: bool = False

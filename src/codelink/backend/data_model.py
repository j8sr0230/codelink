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
from typing import cast, Any, Optional, Union

import PySide2.QtCore as QtCore


class DataModel(QtCore.QAbstractItemModel):
    def __init__(self, parent: QtCore.QObject = None):
        super().__init__(parent)

        self._root_item: TreeItem = TreeItem(header)

    @property
    def root_item(self) -> TreeItem:
        return self._root_item

    def index(self, row: int, column: int, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        parent_item: TreeItem = self.get_item(parent)
        child_item: Optional[TreeItem] = parent_item.child(row)
        if child_item is not None:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def get_item(self, index: QtCore.QModelIndex) -> TreeItem:
        if index.isValid():
            item: Optional[TreeItem] = cast(TreeItem, index.internalPointer())
            if item is not None:
                return item

        return self._root_item

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return None

        item: Optional[TreeItem] = self.get_item(index)
        return item.data(index.column())

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.EditRole) -> bool:
        if role != QtCore.Qt.EditRole:
            return False

        item: TreeItem = self.get_item(index)
        result: bool = item.set_data(index.column(), value)

        if result:
            self.dataChanged.emit(index, index)

        return result

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 2

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        parent_item: TreeItem = self.get_item(parent)
        return parent_item.child_count()

    def insertRows(self, position: int, rows: int, parent=QtCore.QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        result: bool = parent_item.insert_children(position, rows)
        self.endInsertRows()
        return result

    def removeRows(self, position: int, rows: int, parent=QtCore.QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        result: bool = parent_item.remove_children(position, rows)
        self.endRemoveRows()
        return result

    def parent(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item: TreeItem = self.get_item(index)
        parent_item: Optional[TreeItem] = child_item.parent

        if parent_item == self._root_item or parent_item is None:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.child_row_number(), 0, parent_item)

    def flags(self, index: QtCore.QModelIndex) -> Union[int, QtCore.Qt.ItemFlags]:
        if not index.isValid():
            return 0

        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role=QtCore.Qt.DisplayRole) -> Any:
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._root_item.data(section)

        return None

    def setHeaderData(self, section: int, orientation: QtCore.Qt.Orientation, value: Any,
                      role: int = QtCore.Qt.EditRole) -> bool:
        if role != QtCore.Qt.EditRole or orientation != QtCore.Qt.Horizontal:
            return False

        result: bool = self.rootItem.set_data(section, value)
        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

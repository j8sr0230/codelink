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
from typing import cast, Any, Union, Optional
import sys

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from data_item import DataItem
from data_root import DataRoot
from data_property import DataProperty


class DataModel(QtCore.QAbstractItemModel):
    def __init__(self, parent: QtCore.QObject = None):
        super().__init__(parent)

        self._root_item: DataRoot = DataRoot()

    @property
    def root_item(self) -> DataRoot:
        return self._root_item

    @root_item.setter
    def root_item(self, value: DataRoot) -> None:
        self._root_item: DataRoot = value

    def append_property(self, data_property: DataProperty) -> QtCore.QModelIndex:
        row: int = self.rowCount(QtCore.QModelIndex())

        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self._root_item.append_child(data_property)
        self.endInsertRows()

        return self.index(row, 0, QtCore.QModelIndex())

    def insertRows(self, position: int, rows: int, parent=QtCore.QModelIndex()) -> bool:
        return False

    def removeRows(self, position: int, rows: int, parent=QtCore.QModelIndex()) -> bool:
        if not parent.isValid():
            parent_item: DataItem = self._root_item
        else:
            parent_item: DataItem = cast(DataItem, parent.internalPointer())

        for i in range(rows):
            child_item: Optional[DataItem] = parent_item.child(position)
            if child_item is not None:
                self.beginRemoveRows(parent, position, position)
                parent_item.remove_child(position)
                self.endRemoveRows()

        return True

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        if not parent.isValid():
            parent_item: DataItem = self._root_item
        else:
            parent_item: DataItem = cast(DataItem, parent.internalPointer())

        return parent_item.child_count()

    def hasChildren(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        if not parent.isValid():
            parent_item: DataItem = self._root_item
        else:
            parent_item: DataItem = cast(DataItem, parent.internalPointer())

        return parent_item.child_count() > 0

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 2

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        data_item: DataItem = cast(DataItem, index.internalPointer())

        if type(data_item) is DataProperty:
            data_property: DataProperty = cast(DataProperty, data_item)
            if index.column() == 0:
                return data_property.key
            if index.column() == 1:
                return data_property.value

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.EditRole) -> bool:
        if not index.isValid():
            return False

        data_item: DataItem = cast(DataItem, index.internalPointer())

        if type(data_item) is DataProperty and index.column() == 1 and role == QtCore.Qt.EditRole:
            data_property: DataProperty = cast(DataProperty, data_item)
            data_property.value = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex) -> QtCore.QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parent_item: DataItem = self._root_item
        else:
            parent_item: DataItem = cast(DataItem, parent.internalPointer())

        child_item: Optional[DataItem] = parent_item.child(row)
        if child_item is not None:
            return self.createIndex(row, column, child_item)

        return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item: Optional[DataItem] = cast(DataItem, index.internalPointer())
        parent_item: Optional[DataItem] = child_item.parent

        if parent_item is None or parent_item == self._root_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def flags(self, index: QtCore.QModelIndex) -> Union[int, QtCore.Qt.ItemFlags]:
        if not index.isValid():
            return 0

        data_item: Optional[DataItem] = cast(DataItem, index.internalPointer())
        if type(data_item) is DataProperty:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEnabled

        return 0

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role=QtCore.Qt.DisplayRole) -> Any:
        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                if role == QtCore.Qt.DisplayRole:
                    return "Key"
                if role == QtCore.Qt.ToolTipRole:
                    return "The name of the property"
            if section == 1:
                if role == QtCore.Qt.DisplayRole:
                    return "Value"
                if role == QtCore.Qt.ToolTipRole:
                    return "The value of the property"


if __name__ == "__main__":
    model: DataModel = DataModel()
    model.dataChanged.connect(
        lambda top_left_idx, bottom_right_idx, roles: print(model.data(top_left_idx))
    )

    model.append_property(DataProperty(key="Color", value="red"))

    print(model.root_item.child(0).parent)
    # model.data(model.createIndex(0, 0, model.root_item.child(0)))

    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    main_window: QtWidgets.QMainWindow = QtWidgets.QMainWindow()

    tree_view: QtWidgets.QTreeView = QtWidgets.QTreeView()
    tree_view.setModel(model)
    main_window.setCentralWidget(tree_view)
    main_window.show()

    sys.exit(app.exec_())
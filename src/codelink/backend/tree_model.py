#!/usr/bin/env python

############################################################################
#
# Copyright (C) 2005-2005 Trolltech AS. All rights reserved.
# Modified 2024 by Ronny Scharf-W. (ronny.scharf08@gmail.com).
#
# This file is part of the example classes of the Qt Toolkit.
#
# This file may be used under the terms of the GNU General Public
# License version 2.0 as published by the Free Software Foundation
# and appearing in the file LICENSE.GPL included in the packaging of
# this file.  Please review the following information to ensure GNU
# General Public Licensing requirements will be met:
# http://www.trolltech.com/products/qt/opensource.html
#
# If you are unsure which license is appropriate for your use, please
# review the following information:
# http://www.trolltech.com/products/qt/licensing.html or contact the
# sales department at sales@trolltech.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
############################################################################

from __future__ import annotations
from typing import cast, Any, Optional, Union

import PySide2.QtCore as QtCore

from tree_item import TreeItem


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, header: list[str], parent: QtCore.QObject = None):
        super().__init__(parent)

        self.rootItem: TreeItem = TreeItem(header)

    def get_item(self, index: QtCore.QModelIndex) -> TreeItem:
        if index.isValid():
            item: Optional[TreeItem] = cast(TreeItem, index.internalPointer())
            if item is not None:
                return item

        return self.rootItem

    def index(self, row: int, column: int, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        parent_item: TreeItem = self.get_item(parent)
        child_item: Optional[TreeItem] = parent_item.child(row)
        if child_item is not None:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

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
        return self.rootItem.data_column_count()

    def insertColumns(self, position: int, columns: int, parent=QtCore.QModelIndex()) -> bool:
        self.beginInsertColumns(parent, position, position + columns - 1)
        result: bool = self.rootItem.insert_data_columns(position, columns)
        self.endInsertColumns()
        return result

    def removeColumns(self, position: int, columns: int, parent=QtCore.QModelIndex()) -> bool:
        self.beginRemoveColumns(parent, position, position + columns - 1)
        result: bool = self.rootItem.remove_data_columns(position, columns)
        self.endRemoveColumns()

        if self.rootItem.data_column_count() == 0:
            self.removeRows(0, self.rowCount())

        return result

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        parent_item: TreeItem = self.get_item(parent)
        return parent_item.child_row_count()

    def insertRows(self, position: int, rows: int, parent=QtCore.QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        result: bool = parent_item.insert_child_rows(position, rows, self.rootItem.data_column_count())
        self.endInsertRows()
        return result

    def removeRows(self, position: int, rows: int, parent=QtCore.QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        result: bool = parent_item.remove_child_rows(position, rows)
        self.endRemoveRows()
        return result

    def parent(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item: TreeItem = self.get_item(index)
        parent_item: Optional[TreeItem] = child_item.parent

        if parent_item == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.child_row_number(), 0, parent_item)

    def flags(self, index: QtCore.QModelIndex) -> Union[int, QtCore.Qt.ItemFlags]:
        if not index.isValid():
            return 0

        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role=QtCore.Qt.DisplayRole) -> Any:
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def setHeaderData(self, section: int, orientation: QtCore.Qt.Orientation, value: Any,
                      role: int = QtCore.Qt.EditRole) -> bool:
        if role != QtCore.Qt.EditRole or orientation != QtCore.Qt.Horizontal:
            return False

        result: bool = self.rootItem.set_data(section, value)
        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result


if __name__ == "__main__":
    import PySide2.QtGui as QtGui

    root_item: TreeItem = TreeItem(data=["Key", "Value"], parent=None)
    root_item.insert_child_rows(position=0, count=1, columns=2)

    data_item: TreeItem = root_item.child(0)
    data_item.set_data(column=0, value="Color")
    data_item.set_data(column=1, value=QtGui.QColor("#1D1D1D"))

    print(root_item.data(0), root_item.data(1))
    print(data_item.child_row_number(), data_item.data(0), data_item.data(1))

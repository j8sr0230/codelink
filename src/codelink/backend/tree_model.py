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
from typing import cast, Any, Optional
import sys

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from tree_item import TreeItem
from root_item import RootItem
from container_item import ContainerItem
from property_item import PropertyItem


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent: QtCore.QObject = None):
        super().__init__(parent)

        self._root_item: RootItem = RootItem()

    @property
    def root_item(self) -> RootItem:
        return self._root_item

    @root_item.setter
    def root_item(self, value: RootItem) -> None:
        self._root_item: RootItem = value

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return QtCore.QModelIndex()

        child_item: Optional[TreeItem] = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)

        return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item: TreeItem = self.get_item(index)
        if child_item:
            parent_item: Optional[TreeItem] = child_item.parent
        else:
            parent_item: Optional[TreeItem] = None

        if parent_item == self.root_item or not parent_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return 0

        return len(parent_item.children)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 2

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        tree_item: TreeItem = self.get_item(index)

        if role == QtCore.Qt.DisplayRole:
            if type(tree_item) is ContainerItem:
                container_item: ContainerItem = cast(ContainerItem, tree_item)
                if index.column() == 0:
                    return container_item.name

            if type(tree_item) is PropertyItem:
                property_item: PropertyItem = cast(PropertyItem, tree_item)
                if index.column() == 0:
                    return property_item.key
                if index.column() == 1:
                    return property_item.value

        if role == QtCore.Qt.BackgroundColorRole:
            if type(tree_item) is ContainerItem:
                return QtGui.QColor("#ccc")

    def hasChildren(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        if parent_item:
            return len(parent_item.children) > 0
        else:
            return False

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.EditRole) -> bool:
        if role != QtCore.Qt.EditRole:
            return False

        tree_item: TreeItem = self.get_item(index)

        if type(tree_item) is PropertyItem and index.column() == 1:
            property_item: PropertyItem = cast(PropertyItem, tree_item)
            property_item.value = value
            self.dataChanged.emit(index, index, [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole])
            return True

        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtCore.Qt.NoItemFlags | QtCore.Qt.NoItemFlags

        tree_item: Optional[TreeItem] = cast(TreeItem, index.internalPointer())
        if type(tree_item) is PropertyItem:
            if index.column() == 0:
                return QtCore.Qt.NoItemFlags | QtCore.Qt.NoItemFlags
            if index.column() == 1:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        return QtCore.Qt.ItemIsEnabled | QtCore.QAbstractItemModel.flags(self, index)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role=QtCore.Qt.DisplayRole) -> Any:
        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                if role == QtCore.Qt.DisplayRole:
                    return "Property"
                if role == QtCore.Qt.ToolTipRole:
                    return "The name of the property"
            if section == 1:
                if role == QtCore.Qt.DisplayRole:
                    return "Value"
                if role == QtCore.Qt.ToolTipRole:
                    return "The value of the property"

    def removeRow(self, row: int, parent=QtCore.QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False

        child_item: Optional[TreeItem] = parent_item.child(row)
        if child_item:
            self.beginRemoveRows(parent, row, row)
            parent_item.remove_child(row)
            self.endRemoveRows()
            return True

        return False

    def get_item(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> TreeItem:
        if index.isValid():
            item: TreeItem = cast(TreeItem, index.internalPointer())
            if item:
                return item

        return self.root_item

    def append_item(self, tree_item: TreeItem, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        parent_item: TreeItem = self.get_item(parent)
        row: int = len(parent_item.children)

        if parent_item == self.root_item or not parent_item:
            parent_index: QtCore.QModelIndex = QtCore.QModelIndex()
        else:
            parent_index: QtCore.QModelIndex = parent

        self.beginInsertRows(parent_index, row, row)
        parent_item.append_child(tree_item)
        self.endInsertRows()
        return self.index(row, 0, parent_index)

    def traverse(self, depth: int = 0, parent_index: QtCore.QModelIndex = QtCore.QModelIndex()) -> None:
        row_count: int = self.rowCount(parent_index)
        for row in range(row_count):
            index: QtCore.QModelIndex = self.index(row, 0, parent_index)
            tree_item: TreeItem = self.get_item(index)
            print(4 * " " * depth, type(tree_item), tree_item.__getstate__())

            if self.hasChildren(index):
                self.traverse(depth+1, index)


if __name__ == "__main__":
    model: TreeModel = TreeModel()
    model.rowsInserted.connect(
        lambda parent_idx, first_row_idx, last_row_idx: print("Inserted at:", first_row_idx)
    )
    model.rowsRemoved.connect(
        lambda parent_idx, first_row_idx, last_row_idx: print("Removed at:", first_row_idx)
    )
    model.dataChanged.connect(
        lambda top_left_idx, bottom_right_idx, roles: print(
            "Changed at:", top_left_idx.row(), top_left_idx.column(), "to:", model.data(top_left_idx)
        )
    )

    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    main_window: QtWidgets.QMainWindow = QtWidgets.QMainWindow()
    tree_view: QtWidgets.QTreeView = QtWidgets.QTreeView()
    tree_view.setModel(model)
    tree_view.setAlternatingRowColors(True)
    main_window.setCentralWidget(tree_view)
    main_window.show()

    model.rowsInserted.connect(
        lambda: tree_view.expandRecursively(QtCore.QModelIndex())
    )

    node_container: ContainerItem = ContainerItem(name="Nodes")
    nodes_idx: QtCore.QModelIndex = model.append_item(node_container, QtCore.QModelIndex())

    vector_item: PropertyItem = PropertyItem(key="Vector", value="")
    x_component: PropertyItem = PropertyItem(key="X", value=1)
    y_component: PropertyItem = PropertyItem(key="Y", value=0)
    z_component: PropertyItem = PropertyItem(key="Z", value=0)

    vect_idx: QtCore.QModelIndex = model.append_item(vector_item, nodes_idx)
    model.append_item(x_component, vect_idx)
    model.append_item(y_component, vect_idx)
    model.append_item(z_component, vect_idx)

    edge_container: ContainerItem = ContainerItem(name="Edges")
    edges_idx: QtCore.QModelIndex = model.append_item(edge_container, QtCore.QModelIndex())

    model.traverse()

    sys.exit(app.exec_())

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
import json

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from tree_item import TreeItem
from root_item import RootItem
from seperator_item import SeperatorItem
from property_item import PropertyItem
from integer_property_item import IntegerPropertyItem

from undo_cmds import PropertyEditCommand
from delegates import TreeViewDelegate


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, data: Optional[dict[str, Any]] = None, parent: QtCore.QObject = None):
        super().__init__(parent)

        if data:
            self._root_item: RootItem = cast(RootItem, self.from_dict(data))
        else:
            self._root_item: RootItem = RootItem()

        self._undo_stack: QtWidgets.QUndoStack = QtWidgets.QUndoStack()

    @property
    def root_item(self) -> RootItem:
        return self._root_item

    @root_item.setter
    def root_item(self, value: RootItem) -> None:
        self._root_item: RootItem = value

    @property
    def undo_stack(self) -> QtWidgets.QUndoStack:
        return self._undo_stack

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

        if role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole and role != QtCore.Qt.BackgroundColorRole:
            return None

        tree_item: TreeItem = self.get_item(index)

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if type(tree_item) is SeperatorItem:
                container_item: SeperatorItem = cast(SeperatorItem, tree_item)
                if index.column() == 0:
                    return container_item.name

            if isinstance(tree_item, PropertyItem):
                property_item: PropertyItem = cast(PropertyItem, tree_item)
                if index.column() == 0:
                    return property_item.key
                if index.column() == 1:
                    return property_item.value

        if role == QtCore.Qt.BackgroundColorRole:
            if type(tree_item) is SeperatorItem:
                return QtGui.QColor("#ccc")

    def hasChildren(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        return self.rowCount(parent) > 0

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.EditRole) -> bool:
        if role != QtCore.Qt.EditRole:
            return False

        tree_item: TreeItem = self.get_item(index)

        if isinstance(tree_item, PropertyItem) and index.column() == 1:
            self._undo_stack.push(PropertyEditCommand(index, value, self))
            return True

        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtCore.Qt.NoItemFlags | QtCore.Qt.NoItemFlags

        tree_item: Optional[TreeItem] = self.get_item(index)
        if isinstance(tree_item, PropertyItem):
            if index.column() == 0:
                return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
            if index.column() == 1:
                return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

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

    def insert_item(self, row: int, tree_item: TreeItem, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        parent_item: TreeItem = self.get_item(parent)

        if parent_item == self.root_item or not parent_item:
            parent_index: QtCore.QModelIndex = QtCore.QModelIndex()
        else:
            parent_index: QtCore.QModelIndex = parent

        self.beginInsertRows(parent, row, row)
        parent_item.insert_child(row, tree_item)
        self.endInsertRows()
        return self.index(row, 0, parent_index)

    def append_item(self, tree_item: TreeItem, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        return self.insert_item(self.rowCount(parent), tree_item, parent)

    def get_item(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> TreeItem:
        if index.isValid():
            item: TreeItem = cast(TreeItem, index.internalPointer())
            if item:
                return item

        return self.root_item

    def remove_item(self, row: int, parent=QtCore.QModelIndex()) -> bool:
        return self.removeRow(row, parent)

    def to_dict(self, parent_index: QtCore.QModelIndex = QtCore.QModelIndex()) -> dict[str, Any]:
        parent_item: TreeItem = self.get_item(parent_index)
        state: dict[str, Any] = parent_item.__getstate__()

        if self.hasChildren(parent_index):
            child_states: list[dict[str, Any]] = []
            row_count: int = self.rowCount(parent_index)

            for row in range(row_count):
                child_index: QtCore.QModelIndex = self.index(row, 0, parent_index)
                child_states.append(self.to_dict(child_index))

            state["children"] = child_states

        return state

    def from_dict(self, state: dict[str, Any]) -> TreeItem:
        values: list[Any] = list(state.values())
        cls_name: str = values.pop(0)
        tree_item: TreeItem = eval(cls_name)(*values)

        if "children" in state.keys():
            for child_data in state["children"]:
                tree_item.append_child(self.from_dict(child_data))

        return tree_item

    def _repr_recursion(self, tree_item: TreeItem, indent: int = 0) -> str:
        result: str = " " * indent + repr(tree_item) + "\n"
        for child in tree_item.children:
            result += self._repr_recursion(child, indent + 4)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self.root_item)


if __name__ == "__main__":
    # Setup tree model
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

    # Setup ui
    # Main window
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    main_window: QtWidgets.QMainWindow = QtWidgets.QMainWindow()
    main_window.setWindowTitle("Main Window")
    main_undo_action: QtWidgets.QAction = model.undo_stack.createUndoAction(main_window, "Undo")
    main_undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
    main_window.addAction(main_undo_action)
    main_redo_action: QtWidgets.QAction = model.undo_stack.createRedoAction(main_window, "Redo")
    main_redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
    main_window.addAction(main_redo_action)

    main_tree_view: QtWidgets.QTreeView = QtWidgets.QTreeView()
    main_tree_view.setModel(model)
    main_tree_view.setAlternatingRowColors(True)
    main_tree_view.setItemDelegate(TreeViewDelegate())

    model.rowsInserted.connect(
        lambda: main_tree_view.expandRecursively(QtCore.QModelIndex())
    )

    main_window.setCentralWidget(main_tree_view)
    main_window.show()

    # Inspection window
    inspection_window: QtWidgets.QMainWindow = QtWidgets.QMainWindow()
    inspection_window.setWindowTitle("Inspection Window")
    inspection_undo_action: QtWidgets.QAction = model.undo_stack.createUndoAction(inspection_window, "Undo")
    inspection_undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
    inspection_window.addAction(main_undo_action)
    inspection_redo_action: QtWidgets.QAction = model.undo_stack.createRedoAction(inspection_window, "Redo")
    inspection_redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
    inspection_window.addAction(main_redo_action)

    second_tree_view: QtWidgets.QTreeView = QtWidgets.QTreeView()
    second_tree_view.setModel(model)
    second_tree_view.setAlternatingRowColors(True)
    second_tree_view.setItemDelegate(TreeViewDelegate())

    main_tree_view.selectionModel().selectionChanged.connect(
        lambda current, previous: second_tree_view.setRootIndex(cast(QtCore.QItemSelection, current).indexes()[0])
    )

    model.rowsInserted.connect(
        lambda: second_tree_view.expandRecursively(QtCore.QModelIndex())
    )

    inspection_window.setCentralWidget(second_tree_view)
    inspection_window.show()

    # Populate tree model with tree items
    node_sep: SeperatorItem = SeperatorItem(name="Nodes")
    nodes_idx: QtCore.QModelIndex = model.append_item(node_sep, QtCore.QModelIndex())

    vector_item: PropertyItem = PropertyItem(key="Vector", value="")
    vect_idx: QtCore.QModelIndex = model.append_item(vector_item, nodes_idx)

    x_component: IntegerPropertyItem = IntegerPropertyItem(key="X", value=1)
    model.append_item(x_component, vect_idx)

    z_component: IntegerPropertyItem = IntegerPropertyItem(key="Z", value=0)
    model.append_item(z_component, vect_idx)

    y_component: IntegerPropertyItem = IntegerPropertyItem(key="Y", value=0)
    model.insert_item(1, y_component, vect_idx)

    edge_sep: SeperatorItem = SeperatorItem(name="Edges")
    edges_idx: QtCore.QModelIndex = model.append_item(edge_sep, QtCore.QModelIndex())

    frame_sep: SeperatorItem = SeperatorItem(name="Frames")
    frame_idx: QtCore.QModelIndex = model.append_item(frame_sep, QtCore.QModelIndex())

    # Set focus of inspection window
    # second_tree_view.setRootIndex(nodes_idx)

    # Serialize tree mode
    serialized: dict[str, Any] = model.to_dict()
    restored_model: TreeModel = TreeModel(serialized)
    json_str: str = json.dumps(restored_model.to_dict(), indent=4)

    with open("./data.json", "w", encoding="utf-8") as f:
        json.dump(restored_model.to_dict(), f, ensure_ascii=False, indent=4)

    print(restored_model)

    sys.exit(app.exec_())

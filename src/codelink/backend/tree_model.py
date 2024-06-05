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
import importlib

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.user_roles import UserRoles
from codelink.backend.undo_cmds import BaseItemEditCommand, TreeItemInsertCommand, TreeItemRemoveCommand
from codelink.backend.tree_item import TreeItem
from codelink.backend.root_item import RootItem
from codelink.backend.base_item import BaseItem
from codelink.backend.node_item import NodeItem
from codelink.backend.tree_seperator_item import SeperatorItem, TreeSeperatorItem
from codelink.backend.edge_item import EdgeItem


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, data: Optional[dict[str, Any]] = None, undo_stack: Optional[QtWidgets.QUndoStack] = None,
                 parent: QtCore.QObject = None) -> None:
        super().__init__(parent)

        if data:
            self._root_item: RootItem = cast(RootItem, self.from_dict(data))
            self._nodes_index: QtCore.QModelIndex = self.index_from_key("Nodes")
            self._edges_index: QtCore.QModelIndex = self.index_from_key("Edges")
            self._frames_index: QtCore.QModelIndex = self.index_from_key("Frames")
        else:
            self._root_item: RootItem = RootItem()
            self._nodes_index: QtCore.QModelIndex = self.append_item(TreeSeperatorItem("Nodes"), QtCore.QModelIndex())
            self._edges_index: QtCore.QModelIndex = self.append_item(TreeSeperatorItem("Edges"), QtCore.QModelIndex())
            self._frames_index: QtCore.QModelIndex = self.append_item(TreeSeperatorItem("Frames"), QtCore.QModelIndex())

        self._undo_stack: QtWidgets.QUndoStack = undo_stack if undo_stack else QtWidgets.QUndoStack()

    @property
    def root_item(self) -> RootItem:
        return self._root_item

    @root_item.setter
    def root_item(self, value: RootItem) -> None:
        self._root_item: RootItem = value

    @property
    def nodes_index(self) -> QtCore.QModelIndex:
        return self._nodes_index

    @property
    def edges_index(self) -> QtCore.QModelIndex:
        return self._edges_index

    @property
    def frames_index(self) -> QtCore.QModelIndex:
        return self._frames_index

    @property
    def undo_stack(self) -> QtWidgets.QUndoStack:
        return self._undo_stack

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        parent_item: TreeItem = self.item_from_index(parent)
        if not parent_item:
            return QtCore.QModelIndex()

        child_item: Optional[TreeItem] = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)

        return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item: TreeItem = self.item_from_index(index)
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

        parent_item: TreeItem = self.item_from_index(parent)
        if not parent_item:
            return 0

        return len(parent_item.children)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 2

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if (role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole and role != QtCore.Qt.BackgroundColorRole
                and role not in [role for role in UserRoles]):
            return None

        tree_item: TreeItem = self.item_from_index(index)

        if isinstance(tree_item, BaseItem):
            base_item: BaseItem = cast(BaseItem, tree_item)
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
                if index.column() == 0:
                    return base_item.key

                if index.column() == 1:
                    return base_item.value

            if role == UserRoles.KEY:
                return base_item.key

            if role == UserRoles.VALUE:
                return base_item.value

            if isinstance(tree_item, NodeItem):
                node_item: NodeItem = cast(NodeItem, tree_item)
                if role == UserRoles.POS:
                    return node_item.pos

        if type(tree_item) is EdgeItem:
            edge_item: EdgeItem = cast(EdgeItem, tree_item)
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
                if index.column() == 0:
                    return "Edge"

                if index.column() == 1:
                    source: TreeItem = self.item_from_uuid(edge_item.source_uuid)
                    destination: TreeItem = self.item_from_uuid(edge_item.destination_uuid)
                    if hasattr(source, "key") and hasattr(destination, "key"):
                        return source.key + "->" + destination.key

            if role == UserRoles.SRC:
                return self.item_from_uuid(edge_item.source_uuid)

            if role == UserRoles.DEST:
                return self.item_from_uuid(edge_item.destination_uuid)

        if type(tree_item) is TreeSeperatorItem:
            if role == QtCore.Qt.BackgroundColorRole:
                return QtGui.QColor("#ccc")

        if role == UserRoles.TYPE:
            return type(tree_item)

        if role == UserRoles.UUID:
            return tree_item.uuid

    def hasChildren(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        return self.rowCount(parent) > 0

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.EditRole) -> bool:
        if role != QtCore.Qt.EditRole and role != UserRoles.POS and role not in [role for role in UserRoles]:
            return False

        tree_item: TreeItem = self.item_from_index(index)

        if isinstance(tree_item, BaseItem):
            self._undo_stack.push(BaseItemEditCommand(index, value, role))
            return True

        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtCore.Qt.NoItemFlags | QtCore.Qt.NoItemFlags

        tree_item: Optional[TreeItem] = self.item_from_index(index)
        if isinstance(tree_item, BaseItem):
            if index.column() in (0, 1):
                return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

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

    def removeRow(self, row: int, parent=QtCore.QModelIndex()) -> bool:
        parent_item: TreeItem = self.item_from_index(parent)
        if not parent_item:
            return False

        child_item: Optional[TreeItem] = parent_item.child(row)
        if child_item:
            self._undo_stack.push(TreeItemRemoveCommand(self, parent, child_item, row))
            return True

        return False

    def insert_item(self, row: int, tree_item: TreeItem, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        parent_item: TreeItem = self.item_from_index(parent)

        if parent_item == self.root_item or not parent_item:
            parent_index: QtCore.QModelIndex = QtCore.QModelIndex()
        else:
            parent_index: QtCore.QModelIndex = parent

        if isinstance(tree_item, SeperatorItem):
            self.beginInsertRows(parent_index, row, row)
            parent_item.insert_child(row, tree_item)
            self.endInsertRows()
        else:
            self._undo_stack.push(TreeItemInsertCommand(self, parent_index, tree_item, row))

        return self.index(row, 0, parent_index)

    def append_item(self, tree_item: TreeItem, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        return self.insert_item(self.rowCount(parent), tree_item, parent)

    def append_node(self, node_item: NodeItem) -> QtCore.QModelIndex:
        node_item.setup_children()
        return self.append_item(node_item, self._nodes_index)

    def index_from_uuid(self, uuid: str, column: int = 1) -> Optional[QtCore.QModelIndex]:
        index_list: list[int] = self.match(
            self.index(0, column, QtCore.QModelIndex()), UserRoles.UUID, uuid, 1,
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive | QtCore.Qt.MatchWrap
        )
        if len(index_list) > 0:
            return cast(QtCore.QModelIndex, index_list[0])

        return None

    def index_from_key(
            self, key: str, parent: QtCore.QModelIndex = QtCore.QModelIndex()
    ) -> Optional[QtCore.QModelIndex]:
        index_list: list[int] = self.match(
            self.index(0, 0, parent), UserRoles.KEY, key, 1,
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive | QtCore.Qt.MatchWrap
        )
        if len(index_list) > 0:
            return cast(QtCore.QModelIndex, index_list[0])

        return None

    def item_from_index(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> TreeItem:
        if index.isValid():
            item: TreeItem = cast(TreeItem, index.internalPointer())
            if item:
                return item

        return self._root_item

    def item_from_uuid(self, uuid: str) -> Optional[TreeItem]:
        index: Optional[QtCore.QModelIndex] = self.index_from_uuid(uuid)
        if index:
            return self.item_from_index(index)

        return None

    def remove_item(self, row: int, parent=QtCore.QModelIndex()) -> bool:
        return self.removeRow(row, parent)

    def to_dict(self, parent_index: QtCore.QModelIndex = QtCore.QModelIndex()) -> dict[str, Any]:
        parent_item: TreeItem = self.item_from_index(parent_index)
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
        type_name: str = values.pop(0)

        if "children" in state.keys():
            values.pop()
        values.append(values.pop(0))

        class_name: str = type_name.split(".")[-1]
        module_name: str = type_name[:-len(class_name) - 1]
        tree_item: TreeItem = getattr(importlib.import_module(module_name), class_name)(*values)

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

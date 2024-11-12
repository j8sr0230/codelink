#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ************************************************************************
# * Copyright (c) 2024 Ronny Scharf-W. <ronny.scharf08@gmail.com>        *
# *                                                                      *
# * This program is free software; you can redistribute it and/or modify *
# * it under the terms of the GNU Lesser General Public License (LGPL)   *
# * as published by the Free Software Foundation; either version 2 of    *
# * the License, or (at your option) any later version.                  *
# * for detail see the LICENSE text file.                                *
# *                                                                      *
# * This program is distributed in the hope that it will be useful,      *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of       *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the         *
# * GNU Library General Public License for more details.                 *
# *                                                                      *
# * You should have received a copy of the GNU Library General Public    *
# * License along with this program; if not, write to the Free Software  *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  *
# * USA                                                                  *
# *                                                                      *
# ************************************************************************

from __future__ import annotations
from typing import cast, Any, Optional
import importlib

import PySide2.QtCore as QtCore

from codelink.backend.item import Item


class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent: QtCore.QObject = None) -> None:
        super().__init__(parent)

        self._root_item: Item = Item()

    @property
    def root_item(self) -> Item:
        return self._root_item

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        parent_item: Item = self.item_from_index(parent)
        if not parent_item:
            return QtCore.QModelIndex()

        child_item: Item | None = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)

        return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item: Item = self.item_from_index(index)
        if child_item:
            parent_item: Item | None = child_item.parent
        else:
            parent_item: Item | None = None

        if parent_item == self._root_item or not parent_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.item_row(), 0, parent_item)

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if parent.isValid() and parent.column() != 0:
            return 0

        parent_item: Item | None = self.item_from_index(parent)
        if not parent_item:
            return 0

        return len(parent_item.children)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 2

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        return 0

    def hasChildren(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        return self.rowCount(parent) > 0

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.EditRole) -> bool:
        if role != QtCore.Qt.EditRole:
            return False
        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtCore.Qt.NoItemFlags | QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.QAbstractItemModel.flags(self, index)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole) -> Any:
        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                if role == QtCore.Qt.DisplayRole:
                    return "Key"

            if section == 1:
                if role == QtCore.Qt.DisplayRole:
                    return "Value"


    def removeRow(self, row: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        parent_item: Item = self.item_from_index(parent)
        if not parent_item:
            return False

        child_item: Item | None = parent_item.child(row)
        if child_item:
            self.beginRemoveRows(parent, row, row)
            parent_item.remove_child(row)
            self.endRemoveRow()
            return True

        return False

    def insert_item(self, row: int, tree_item: Item, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        parent_item: Item = self.item_from_index(parent)

        if parent_item == self.root_item or not parent_item:
            parent_index: QtCore.QModelIndex = QtCore.QModelIndex()
        else:
            parent_index: QtCore.QModelIndex = parent

        self.beginInsertRows(parent_index, row, row)
        parent_item.insert_child(row, tree_item)
        self.endInsertRows()


        return self.index(row, 0, parent_index)

    def append_item(self, tree_item: Item, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        return self.insert_item(self.rowCount(parent), tree_item, parent)







    def item_from_index(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> Item:
        if index.isValid():
            item: Item = cast(Item, index.internalPointer())
            if item:
                return item

        return self._root_item




    def remove_index(self, index=QtCore.QModelIndex()) -> bool:
        return self.removeRow(index.row(), index.parent())

    def to_dict(self, parent_index: QtCore.QModelIndex = QtCore.QModelIndex()) -> dict[str, Any]:
        parent_item: Item = self.item_from_index(parent_index)
        state: dict[str, Any] = parent_item.__getstate__()

        if self.hasChildren(parent_index):
            child_states: list[dict[str, Any]] = []
            row_count: int = self.rowCount(parent_index)

            for row in range(row_count):
                child_index: QtCore.QModelIndex = self.index(row, 0, parent_index)
                child_states.append(self.to_dict(child_index))

            state["children"] = child_states

        return state

    def from_dict(self, state: dict[str, Any]) -> Item:
        try:
            values: list[Any] = list(state.values())
            type_name: str = values.pop(0)

            if "children" in state.keys():
                values.pop()
            values.append(values.pop(0))

            class_name: str = type_name.split(".")[-1]
            module_name: str = type_name[:-len(class_name) - 1]
            tree_item: Item = getattr(importlib.import_module(module_name), class_name)(*values)

            if "children" in state.keys():
                for child_data in state["children"]:
                    tree_item.append_child(self.from_dict(child_data))

            return tree_item

        except (IndexError, ValueError, AttributeError, Exception):
            pass

    def _repr_recursion(self, tree_item: Item, indent: int = 0) -> str:
        result: str = " " * indent + repr(tree_item) + "\n"
        for child in tree_item.children:
            result += self._repr_recursion(child, indent + 4)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self.root_item)

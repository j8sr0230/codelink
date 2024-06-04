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

from typing import Any, Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from codelink.backend.user_roles import UserRoles


class BaseItemEditCommand(QtWidgets.QUndoCommand):
    def __init__(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.EditRole,
                 parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
        super().__init__(parent)

        self._index: QtCore.QModelIndex = index
        self._value: Any = value
        self._role: int = role
        self._model: QtCore.QAbstractItemModel = index.model()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                self._prev_value: Any = self._model.item_from_index(index).key

            if index.column() == 1:
                self._prev_value: Any = self._model.item_from_index(index).value

        if role == UserRoles.POS and hasattr(self._model.item_from_index(index), "pos"):
            self._prev_value: Any = self._model.item_from_index(index).pos

    @property
    def index(self) -> QtCore.QModelIndex:
        return self._index

    @property
    def model(self) -> QtCore.QAbstractItemModel:
        return self._model

    def id(self) -> int:
        return 10

    def undo(self) -> None:
        if self._role == QtCore.Qt.DisplayRole or self._role == QtCore.Qt.EditRole:
            if self._index.column() == 0:
                self._model.item_from_index(self._index).key: Any = self._prev_value

            if self._index.column() == 1:
                self._model.item_from_index(self._index).value: Any = self._prev_value

            self._model.dataChanged.emit(self._index, self._index, [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole])

        if self._role == UserRoles.POS and hasattr(self._model.item_from_index(self._index), "pos"):
            self._model.item_from_index(self._index).pos = self._prev_value
            self._model.dataChanged.emit(self._index, self._index, [UserRoles.POS])

    def redo(self) -> None:
        if self._role == QtCore.Qt.DisplayRole or self._role == QtCore.Qt.EditRole:
            if self._index.column() == 0:
                self._model.item_from_index(self._index).key: Any = self._value

            if self._index.column() == 1:
                self._model.item_from_index(self._index).value: Any = self._value

            self._model.dataChanged.emit(self._index, self._index, [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole])

        if self._role == UserRoles.POS and hasattr(self._model.item_from_index(self._index), "pos"):
            self._model.item_from_index(self._index).pos = self._value
            self._model.dataChanged.emit(self._index, self._index, [UserRoles.POS])

    def mergeWith(self, other: QtWidgets.QUndoCommand) -> bool:
        other_model: QtCore.QAbstractItemModel = other.model
        other_index: QtCore.QModelIndex = other.index

        if other_model != self._model:
            return False

        if other_index != self._index:
            return False

        if self._role == QtCore.Qt.DisplayRole or self._role == QtCore.Qt.EditRole:
            if self._index.column() == 0:
                self._value: Any = other_model.item_from_index(other.index).key

            if self._index.column() == 1:
                self._value: Any = other_model.item_from_index(other.index).value

        if self._role == UserRoles.POS and hasattr(self._model.item_from_index(self._index), "pos"):
            self._value: Any = other_model.item_from_index(other.index).pos

        return True


class TreeItemInsertCommand(QtWidgets.QUndoCommand):
    def __init__(self, model: QtCore.QAbstractItemModel, parent_index: QtCore.QModelIndex, item: Any, row: int,
                 parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
        super().__init__(parent)

        self._model: QtCore.QAbstractItemModel = model
        self._parent_index: QtCore.QModelIndex = parent_index
        self._item: Any = item
        self._row: int = row

        self._parent: Any = self._model.item_from_index(self._parent_index)

    def undo(self) -> None:
        self._model.beginRemoveRows(self._parent_index, self._row, self._row)
        self._parent.remove_child(self._row)
        self._model.endRemoveRows()

    def redo(self) -> None:
        self._model.beginInsertRows(self._parent_index, self._row, self._row)
        self._parent.insert_child(self._row, self._item)
        self._model.endInsertRows()


class TreeItemRemoveCommand(QtWidgets.QUndoCommand):
    def __init__(self, model: QtCore.QAbstractItemModel, parent_index: QtCore.QModelIndex, item: Any, row: int,
                 parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
        super().__init__(parent)

        self._model: QtCore.QAbstractItemModel = model
        self._parent_index: QtCore.QModelIndex = parent_index
        self._item: Any = item
        self._row: int = row

        self._parent: Any = self._model.item_from_index(self._parent_index)

    def undo(self) -> None:
        self._model.beginInsertRows(self._parent_index, self._row, self._row)
        self._parent.insert_child(self._row, self._item)
        self._model.endInsertRows()

    def redo(self) -> None:
        self._model.beginRemoveRows(self._parent_index, self._row, self._row)
        self._parent.remove_child(self._row)
        self._model.endRemoveRows()


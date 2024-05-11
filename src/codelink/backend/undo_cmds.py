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


class BaseItemEditCommand(QtWidgets.QUndoCommand):
    def __init__(self, index: QtCore.QModelIndex, value: Any, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
        super().__init__(parent)

        self._index: QtCore.QModelIndex = index
        self._value: Any = value
        self._model: QtCore.QAbstractItemModel = index.model()
        # noinspection PyUnresolvedReferences

        if index.column() == 0:
            self._prev_value: Any = self._model.item_from_index(index).key

        if index.column() == 1:
            self._prev_value: Any = self._model.item_from_index(index).value

    @property
    def index(self) -> QtCore.QModelIndex:
        return self._index

    @property
    def model(self) -> QtCore.QAbstractItemModel:
        return self._model

    def id(self) -> int:
        return 10

    def undo(self) -> None:
        if self._index.column() == 0:
            self._model.item_from_index(self._index).key: Any = self._prev_value

        if self._index.column() == 1:
            self._model.item_from_index(self._index).value: Any = self._prev_value

        self._model.dataChanged.emit(self._index, self._index, [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole])

    def redo(self) -> None:
        if self._index.column() == 0:
            self._model.item_from_index(self._index).key: Any = self._value

        if self._index.column() == 1:
            self._model.item_from_index(self._index).value: Any = self._value

        self._model.dataChanged.emit(self._index, self._index, [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole])

    def mergeWith(self, other: QtWidgets.QUndoCommand) -> bool:
        other_model: QtCore.QAbstractItemModel = other.model
        other_index: QtCore.QModelIndex = other.index

        if other_model != self._model:
            return False

        if other_index != self._index:
            return False

        # noinspection PyUnresolvedReferences
        self._value: Any = other_model.item_from_index(other.index).value
        return True

# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2023 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
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

from typing import Any, Optional, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from undo_commands import EditModelDataCommand


class PropertyModel(QtCore.QAbstractTableModel):
    def __init__(self, properties: Optional[dict] = None, header_left: str = "Property", header_right: str = "Value",
                 undo_stack: Optional[QtWidgets.QUndoStack] = None, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)

        if properties is None:
            properties: dict = {}

        self._properties = properties
        self._header_left: str = header_left
        self._header_right: str = header_right
        self._undo_stack: QtWidgets.QUndoStack = undo_stack

    @property
    def properties(self) -> dict:
        return self._properties

    @properties.setter
    def properties(self, value: dict) -> None:
        self._properties: dict = value

    @property
    def header_left(self) -> str:
        return self._header_left

    @header_left.setter
    def header_left(self, value: str) -> None:
        self._header_left: str = value
        cast(QtCore.SignalInstance, self.headerDataChanged).emit(QtCore.Qt.Orientation, 0, 0)

    @property
    def header_right(self) -> str:
        return self._header_right

    @header_right.setter
    def header_right(self, value: str) -> None:
        self._header_right: str = value
        cast(QtCore.SignalInstance, self.headerDataChanged).emit(QtCore.Qt.Orientation, 1, 1)

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self._properties.keys())

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 2

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self._properties.keys()):
            return None

        if role == QtCore.Qt.DisplayRole:
            key: str = list(self._properties.keys())[index.row()]

            if index.column() == 0:
                return key
            else:
                return self._properties[key]

        return None

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole) -> Any:
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return self._header_left
            elif section == 1:
                return self._header_right

        return None

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.DisplayRole) -> bool:
        if role == QtCore.Qt.EditRole:
            key: str = list(self._properties.keys())[index.row()]
            data_type = type(self._properties[key])
            old_value: object = self._properties[key]

            if value != old_value:
                if key not in ("X", "Y"):
                    self._undo_stack.push(EditModelDataCommand(self, index, old_value, data_type(value)))
                else:
                    self._properties[key] = data_type(value)
                    cast(QtCore.SignalInstance, self.dataChanged).emit(index, index)
                return True

        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEnabled

        if index.row() < 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        if index.row() >= 0:
            if index.column() == 0:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

            if index.column() == 1:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def __getstate__(self) -> dict:
        return self._properties

    def __setstate__(self, state: dict):
        self._properties: dict = state

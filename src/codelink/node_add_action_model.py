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

from typing import Any, Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets


class NodeActionModel(QtCore.QAbstractListModel):

    def __init__(self, node_actions: Optional[dict] = None, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)

        if node_actions is None:
            node_actions: dict = {}

        self._node_actions = node_actions

    @property
    def node_actions(self) -> dict:
        return self._node_actions

    @node_actions.setter
    def node_actions(self, value: dict) -> None:
        self._node_actions: dict = value

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self._node_actions.keys())

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self._node_actions.keys()):
            return None

        if role == QtCore.Qt.DisplayRole:
            key: str = list(self._node_actions.keys())[index.row()]
            return key

    def add_action(self, row: int) -> QtWidgets.QAction:
        key: str = list(self._node_actions.keys())[row]
        return self._node_actions[key]

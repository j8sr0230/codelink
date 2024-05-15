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
import PySide2.QtGui as QtGui

from codelink.backend.tree_item import TreeItem


class BaseItem(TreeItem):
    def __init__(self, key: str, value: Any, uuid: Optional[str] = None,
                 parent: Optional[TreeItem] = None) -> None:
        super().__init__(uuid, parent)

        self._key: str = key
        self._value: Any = value

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, value: str) -> None:
        self._key: str = value

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value: Any = value

    @staticmethod
    def create_editor(parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                      index: QtCore.QModelIndex()) -> Optional[QtWidgets.QWidget]:
        return None

    @staticmethod
    def set_editor_data(editor: QtWidgets.QWidget, index: QtCore.QModelIndex()) -> None:
        pass

    @staticmethod
    def set_model_data(editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                       index: QtCore.QModelIndex()) -> bool:
        return False

    @staticmethod
    def update_editor_geometry(editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                               index: QtCore.QModelIndex()) -> None:
        pass

    @staticmethod
    def paint(painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        pass

    def __getstate__(self) -> dict[str, Any]:
        state: dict[str, Any] = super().__getstate__()
        state["key"] = self._key
        state["value"] = self._value
        return state

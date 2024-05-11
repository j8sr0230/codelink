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

from tree_item import TreeItem
from property_item import PropertyItem


class IntegerPropertyItem(PropertyItem):
    def __init__(self, key: str, value: int, uuid: Optional[str] = None,
                 parent: Optional[TreeItem] = None) -> None:
        super().__init__(key, value, uuid, parent)

    @staticmethod
    def create_editor(parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                      index: QtCore.QModelIndex()) -> Optional[QtWidgets.QWidget]:
        editor: QtWidgets.QSpinBox = QtWidgets.QSpinBox(parent)
        editor.setFrame(False)
        return editor

    @staticmethod
    def set_editor_data(editor: QtWidgets.QWidget, index: QtCore.QModelIndex()) -> None:
        value: Any = index.model().data(index, QtCore.Qt.EditRole)
        editor.setValue(value)

    @staticmethod
    def set_model_data(editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                       index: QtCore.QModelIndex()) -> bool:
        editor.interpretText()
        value: int = editor.value()
        return model.setData(index, value, int(QtCore.Qt.EditRole))

    @staticmethod
    def update_editor_geometry(editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                               index: QtCore.QModelIndex()) -> None:
        editor.setGeometry(option.rect)

    def __repr__(self) -> str:
        result: str = f"<integer_property_item.IntegerPropertyItem {self._uuid} at 0x{id(self):x}"
        result += f", {len(self._children)} children>"
        return result

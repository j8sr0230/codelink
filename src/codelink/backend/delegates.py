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

from typing import Optional, Any

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from tree_item import TreeItem
from base_item import BaseItem
from seperator_item import SeperatorItem


class TreeViewDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex()) -> Optional[QtWidgets.QWidget]:
        tree_item: TreeItem = index.model().item_from_index(index)

        if isinstance(tree_item, BaseItem) and not isinstance(tree_item, SeperatorItem):
            if index.column() == 0:
                editor: QtWidgets.QLineEdit = QtWidgets.QLineEdit(parent)
                return editor

            if index.column() == 1:
                return tree_item.create_editor(parent, option, index)

        return None

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex()) -> None:
        tree_item: TreeItem = index.model().item_from_index(index)

        if isinstance(tree_item, BaseItem) and not type(tree_item) is SeperatorItem:
            if index.column() == 0:
                value: Any = index.model().data(index, QtCore.Qt.EditRole)
                editor.setText(value)

            if index.column() == 1:
                tree_item.set_editor_data(editor, index)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex()) -> bool:
        tree_item: TreeItem = index.model().item_from_index(index)

        if isinstance(tree_item, BaseItem) and not isinstance(tree_item, SeperatorItem):
            if index.column() == 0:
                value: str = editor.text()
                return model.setData(index, value, int(QtCore.Qt.EditRole))

            if index.column() == 1:
                return tree_item.set_model_data(editor, model, index)

        return False

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex()) -> None:
        editor.setGeometry(option.rect)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        tree_item: TreeItem = index.model().item_from_index(index)

        if isinstance(tree_item, BaseItem) and not isinstance(tree_item, SeperatorItem):
            tree_item.paint(painter, option, index)

        super().paint(painter, option, index)

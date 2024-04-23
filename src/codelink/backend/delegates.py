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


class TreeViewDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex()) -> QtWidgets.QSpinBox:
        editor: Optional[QtWidgets.QWidget] = None
        data_type: type = type(index.model().data(index, QtCore.Qt.EditRole))

        if data_type is str:
            editor: QtWidgets.QSpinBox = QtWidgets.QLineEdit(parent)

        if data_type is int:
            editor: QtWidgets.QSpinBox = QtWidgets.QSpinBox(parent)
            editor.setFrame(False)
            # editor.setMinimum(0)
            # editor.setMaximum(100)

        return editor

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex()) -> None:
        value: Any = index.model().data(index, QtCore.Qt.EditRole)

        if type(editor) is QtWidgets.QSpinBox:
            editor.setValue(value)

        if type(editor) is QtWidgets.QLineEdit:
            editor.setText(value)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex()) -> bool:
        if type(editor) is QtWidgets.QSpinBox:
            editor.interpretText()
            value: int = editor.value()
            return model.setData(index, value, int(QtCore.Qt.EditRole))

        if type(editor) is QtWidgets.QLineEdit:
            value: str = editor.text()
            return model.setData(index, value, int(QtCore.Qt.EditRole))

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex()) -> None:
        editor.setGeometry(option.rect)

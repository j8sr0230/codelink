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

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class IntegerDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:

        editor: QtWidgets.QSpinBox = QtWidgets.QSpinBox(parent)
        editor.setFrame(True)
        editor.setRange(-64000, 64000)
        editor.setSingleStep(10)
        # editor.valueChanged.connect(self.commit_editor)
        editor.editingFinished.connect(self.commit_editor)

        if index.isValid():
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()  # Gets sender, in this case QSpinBox
        self.commitData.emit(editor)  # Emit signal of delegate

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        # noinspection PyTypeChecker
        value: int = int(index.data(QtCore.Qt.DisplayRole))
        editor.setValue(value)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        editor.interpretText()
        value = int(editor.value())
        model.setData(index, value, QtCore.Qt.EditRole | QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def eventFilter(self, editor: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Tab:
                self.commitData.emit(editor)
                self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.NoHint)
                return True

            if event.key() == QtCore.Qt.Key_Return:
                self.commitData.emit(editor)
                self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.NoHint)
                return True
            elif event.matches(QtGui.QKeySequence.Undo) or event.matches(QtGui.QKeySequence.Redo):
                event.ignore()
                return True
            else:
                return False
        else:
            return False


class BooleanDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

        self._items: list[str] = ["false", "true"]

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:

        editor: QtWidgets.QComboBox = QtWidgets.QComboBox(parent)
        editor.addItems(self._items)
        editor.currentIndexChanged.connect(self.commit_editor)
        # editor.currentTextChanged.connect(self.commit_editor)

        item_list_view: QtWidgets.QAbstractItemView = editor.view()
        item_list_view.setSpacing(2)

        if index.isValid():
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()
        self.commitData.emit(editor)

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        # noinspection PyTypeChecker
        value: str = str(index.data(QtCore.Qt.DisplayRole)).lower()
        num: int = self._items.index(value)
        editor.blockSignals(True)
        editor.setCurrentIndex(num)
        editor.blockSignals(False)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        value: bool = eval(editor.currentText().capitalize())
        # noinspection PyTypeChecker
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def eventFilter(self, editor: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Tab:
                self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.NoHint)
                return True
            elif event.matches(QtGui.QKeySequence.Undo) or event.matches(QtGui.QKeySequence.Redo):
                event.ignore()
                return True
            else:
                return False
        else:
            return False


class StringDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:

        editor: QtWidgets.QLineEdit = QtWidgets.QLineEdit(parent)
        editor.setFocusPolicy(QtCore.Qt.StrongFocus)
        # editor.textChanged.connect(self.commit_editor)
        editor.editingFinished.connect(self.commit_editor)

        if index.isValid():
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()
        self.commitData.emit(editor)

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        # noinspection PyTypeChecker
        value: str = index.data(QtCore.Qt.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:

        value: str = editor.text()
        model.setData(index, value, QtCore.Qt.EditRole | QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def eventFilter(self, editor: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Tab:
                self.commitData.emit(editor)
                self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.NoHint)
                return True

            if event.key() == QtCore.Qt.Key_Return:
                self.commitData.emit(editor)
                self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.NoHint)
                return True
            elif event.matches(QtGui.QKeySequence.Undo) or event.matches(QtGui.QKeySequence.Redo):
                event.ignore()
                return True
            else:
                return False
        else:
            return False

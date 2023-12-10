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

from typing import Optional, Union, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class NumberInputWidget(QtWidgets.QLineEdit):
    def __init__(self, undo_stack: QtWidgets.QUndoStack, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self._undo_stack: QtWidgets.QUndoStack = undo_stack
        self._last_valid_value: float = 0

    def input_data(self):
        try:
            self._last_valid_value: float = float(self.text())
        except ValueError:
            self.setText(str(self._last_valid_value))
            print("Wrong input format")

        return self._last_valid_value

    def set_input_data(self, value: Union[bool, float, str]) -> None:
        self.setText(str(value))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.matches(QtGui.QKeySequence.Undo):
            self._undo_stack.undo()
        elif event.matches(QtGui.QKeySequence.Redo):
            self._undo_stack.redo()
        elif event.key() == QtCore.Qt.Key_Return:
            self.parentWidget().clearFocus()
        else:
            super().keyPressEvent(event)

    # def focusInEvent(self, e: QtGui.QFocusEvent) -> None:
    #     super().focusInEvent(e)
    #     print("focus in")
    #
    # def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:
    #     super().focusOutEvent(e)
    #     print("focus Out")

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        # if self.hasFocus():
        self.parentWidget().setFocus()

        if event.modifiers() == QtCore.Qt.ShiftModifier:
            if event.angleDelta().y() > 0:
                self.setText(str(round(float(self.text()) + 10, 2)))
            else:
                self.setText(str(round(float(self.text()) - 10, 2)))

        elif event.modifiers() == QtCore.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.setText(str(round(float(self.text()) + .1, 2)))
            else:
                self.setText(str(round(float(self.text()) - .1, 2)))

        else:
            if event.angleDelta().y() > 0:
                self.setText(str(round(float(self.text()) + 1, 2)))
            else:
                self.setText(str(round(float(self.text()) - 1, 2)))

        cast(QtCore.SignalInstance, self.editingFinished).emit()
        self.selectAll()


class BoolInputWidget(QtWidgets.QCheckBox):
    def __init__(self, undo_stack: QtWidgets.QUndoStack, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self._undo_stack: QtWidgets.QUndoStack = undo_stack

    def input_data(self):
        return self.checkStateSet()

    def set_input_data(self, value: Union[bool, float, str]) -> None:
        self.setChecked(True) if value is True else self.setChecked(False)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.matches(QtGui.QKeySequence.Undo):
            self._undo_stack.undo()
        elif event.matches(QtGui.QKeySequence.Redo):
            self._undo_stack.redo()
        else:
            super().keyPressEvent(event)


class OptionBoxWidget(QtWidgets.QComboBox):
    def __init__(self, undo_stack: QtWidgets.QUndoStack, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self._undo_stack: QtWidgets.QUndoStack = undo_stack
        self._last_index: int = 0

    @property
    def last_index(self) -> int:
        return self._last_index

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self._last_index: int = self.currentIndex()
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.matches(QtGui.QKeySequence.Undo):
            self._undo_stack.undo()
        elif event.matches(QtGui.QKeySequence.Redo):
            self._undo_stack.redo()
        else:
            super().keyPressEvent(event)

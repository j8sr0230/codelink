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

from typing import Optional, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class PropertyTable(QtWidgets.QTableView):
    table_top_reached: QtCore.Signal = QtCore.Signal(QtWidgets.QTableView)
    table_bottom_reached: QtCore.Signal = QtCore.Signal(QtWidgets.QTableView)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # Widget setup
        self.setWordWrap(False)
        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setEditTriggers(QtWidgets.QTableView.AnyKeyPressed | QtWidgets.QTableView.DoubleClicked)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().hide()

    # --------------- Overwrites ---------------

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Tab or event.key() == QtCore.Qt.Key_Down:
            new_row = self.currentIndex().row() + 1

            if new_row == self.model().rowCount():
                cast(QtCore.SignalInstance, self.table_bottom_reached).emit(self)
            else:
                new_index = self.model().index(new_row, 1)
                self.setCurrentIndex(new_index)

        elif event.key() == QtCore.Qt.Key_Up:
            new_row = self.currentIndex().row() - 1

            if new_row == -1:
                cast(QtCore.SignalInstance, self.table_top_reached).emit(self)
            else:
                new_index = self.model().index(new_row, 1)
                self.setCurrentIndex(new_index)

        elif event.matches(QtGui.QKeySequence.Undo) or event.matches(QtGui.QKeySequence.Redo):
            event.ignore()

        else:
            super().keyPressEvent(event)

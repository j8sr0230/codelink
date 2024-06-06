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

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from codelink.frontend.delegates import TreeViewDelegate


class TreeView(QtWidgets.QTreeView):
    def __init__(self) -> None:
        super().__init__()

        self.setAlternatingRowColors(True)
        self.setItemDelegate(TreeViewDelegate())
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def focusNextPrevChild(self, forward: bool) -> bool:
        selection_model: QtCore.QItemSelectionModel = self.selectionModel()
        current_index: QtCore.QModelIndex = selection_model.currentIndex()

        if forward:
            next_index: QtCore.QModelIndex = self.indexBelow(current_index)
        else:
            next_index: QtCore.QModelIndex = self.indexAbove(current_index)

        if not next_index.isValid():
            next_index: QtCore.QModelIndex = self.model().index(0, current_index.column(), self.rootIndex())

        selection_model.select(next_index, QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Rows)
        self.setCurrentIndex(next_index)
        self.edit(self.currentIndex())
        return True

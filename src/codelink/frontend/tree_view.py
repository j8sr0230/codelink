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
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.frontend.delegates import TreeViewDelegate


class TreeView(QtWidgets.QTreeView):
    def __init__(self) -> None:
        super().__init__()

        self.setAlternatingRowColors(True)
        self.setItemDelegate(TreeViewDelegate())
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def visible_row_height(self) -> int:
        height: int = 0

        index: QtCore.QModelIndex = self.rootIndex()
        while index.isValid():
            if self.isIndexHidden(index):
                continue

            print(self.rowHeight(index), self.frameWidth())
            height += self.rowHeight(index) + 1 * self.frameWidth()
            index: QtCore.QModelIndex = self.indexBelow(index)

        return height

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super().keyPressEvent(event)

    def focusNextPrevChild(self, forward: bool) -> bool:
        if forward:
            next_index: QtCore.QModelIndex = self.indexBelow(self.currentIndex())
        else:
            next_index: QtCore.QModelIndex = self.indexAbove(self.currentIndex())

        if not next_index.isValid():
            next_index: QtCore.QModelIndex = self.model().index(0, self.currentIndex().column(), self.rootIndex())

        self.setCurrentIndex(next_index)
        self.edit(next_index)
        return True

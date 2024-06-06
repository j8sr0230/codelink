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

from typing import  cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from codelink.backend.tree_model import TreeModel

from codelink.frontend.delegates import TreeViewDelegate


class TreeView(QtWidgets.QTreeView):
    def __init__(self) -> None:
        super().__init__()

        self.setAlternatingRowColors(True)
        self.setItemDelegate(TreeViewDelegate())
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def focusNextPrevChild(self, forward: bool) -> bool:
        index: QtCore.QModelIndex = self.selectionModel().currentIndex()
        if isinstance(index.model(), QtCore.QSortFilterProxyModel):
            source_index: QtCore.QModelIndex = index.model().mapToSource(index)
            source_model: TreeModel =  cast(TreeModel, self.model().sourceModel())
        else:
            source_index: QtCore.QModelIndex = index
            source_model: TreeModel = cast(TreeModel, self.model())

        parent_index: QtCore.QModelIndex = source_index.parent()
        if source_model.hasChildren(source_index):
            print("Step down")
        elif source_model.index(source_index.row() + 1, 0, parent_index).isValid():
            print("Increment")
        else:
            print("Step up")

        # if input_widget == QtWidgets.QApplication.focusWidget():
        #     return False

        # socket_idx: int = self.parent_node.input_socket_widgets.index(input_widget.parent())
        # next_idx: int = 0
        # for idx in range(socket_idx + 1, len(self.parent_node.input_socket_widgets)):
        #     if self.parent_node.input_socket_widgets[idx].input_widget.focusPolicy() == QtCore.Qt.StrongFocus:
        #         next_idx: int = idx
        #         break
        #
        # self.parent_node.input_socket_widgets[next_idx].setFocus(QtCore.Qt.TabFocusReason)
        return True

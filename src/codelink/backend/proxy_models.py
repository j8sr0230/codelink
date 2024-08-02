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

from typing import Any

import PySide2.QtCore as QtCore

from codelink.backend.user_roles import UserRoles
from codelink.backend.seperator_item import SeperatorItem
from codelink.backend.outputs_seperator_item import OutputsSeperatorItem


class ItemViewProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()

    def mapFromSource(self, source_index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        return super().mapFromSource(source_index)

    def mapToSource(self, proxy_index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        return super().mapToSource(proxy_index)

    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:
        return not source_parent.parent().isValid()


class DetailViewProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()

    def mapFromSource(self, source_index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        return super().mapFromSource(source_index)

    def mapToSource(self, proxy_index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        return super().mapToSource(proxy_index)

    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:
        accepts: bool = True

        if source_parent.isValid():
            index: QtCore.QModelIndex = self.sourceModel().index(source_row, 0, source_parent)

            if index.data() in ["Nodes", "Edges", "Frames"]:
                accepts: bool = False

        return accepts


class NodeViewProxyModel(DetailViewProxyModel):
    def __init__(self) -> None:
        super().__init__()

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if isinstance(index.data(UserRoles.TYPE), SeperatorItem) and role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(5, 5)
        else:
            return super().data(index, role)

    def mapFromSource(self, source_index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        if source_index.parent().isValid():
            if source_index.parent().data(role=UserRoles.TYPE) == OutputsSeperatorItem:
                return super().mapFromSource(source_index).siblingAtColumn(abs(source_index.column() - 1))
            else:
                return super().mapFromSource(source_index)

        else:
            return super().mapFromSource(source_index)

    def mapToSource(self, proxy_index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        if proxy_index.parent().isValid():
            if super().mapToSource(proxy_index).parent().data(role=UserRoles.TYPE) == OutputsSeperatorItem:
                return super().mapToSource(proxy_index).siblingAtColumn(abs(proxy_index.column() - 1))
            else:
                return super().mapToSource(proxy_index)
        else:
            return super().mapToSource(proxy_index)

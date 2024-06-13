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

from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from codelink.frontend.tree_view import TreeView


class NodeGrItem(QtWidgets.QGraphicsItem):
    def __init__(self, index: QtCore.QModelIndex, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._index: QtCore.QModelIndex = index

        self._width: int = 100
        self._height: int = 100

        name_item = QtWidgets.QGraphicsTextItem(self)
        name_item.setDefaultTextColor(QtGui.QColor("#E5E5E5"))
        name_item.setPlainText(self._index.data(int(QtCore.Qt.DisplayRole)))

        item_view: TreeView = TreeView()
        item_view.setIndentation(0)
        item_view.setHeaderHidden(True)
        # item_view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        # item_view.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        # item_view.header().resizeSection(0, self._width // 2 - item_view.frameWidth())
        # item_view.header().resizeSection(1, self._width // 2 - item_view.frameWidth())

        item_view.setModel(index.model())
        item_view.setRootIndex(index)
        item_view.expandAll()

        proxy_w: QtWidgets.QGraphicsProxyWidget = QtWidgets.QGraphicsProxyWidget(self, QtCore.Qt.Widget)
        proxy_w.setWidget(item_view)
        proxy_w.setGeometry(self.boundingRect())

        # item_view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        # item_view.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        item_view.header().resizeSection(0, self._width // 2 - item_view.frameWidth())
        item_view.header().resizeSection(1, self._width // 2 - item_view.frameWidth())

        proxy_w.setPos(0, 20)

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._width, self._height)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("303030")))
        painter.drawRoundedRect(self.boundingRect(), 5, 5)

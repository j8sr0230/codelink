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

from codelink.frontend.color_palette import ColorPalette
from codelink.frontend.tree_view import TreeView


class NodeGrItem(QtWidgets.QGraphicsItem):
    def __init__(self, index: QtCore.QModelIndex, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._index: QtCore.QModelIndex = index

        self._width: int = 100
        self._title_height: int = 20

        title_text_item = QtWidgets.QGraphicsTextItem(self)
        title_text_item.setDefaultTextColor(QtGui.QColor(ColorPalette.WHITE))
        title_text_item.setPlainText(self._index.data(int(QtCore.Qt.DisplayRole)))

        content_view: TreeView = TreeView()
        content_view.setIndentation(0)
        content_view.setHeaderHidden(True)
        content_view.setModel(index.model())
        content_view.setRootIndex(index)
        content_view.expandAll()
        content_view.header().resizeSection(0, self._width // 2 - content_view.frameWidth())
        content_view.header().resizeSection(1, self._width // 2 - content_view.frameWidth())

        self._content_height: int = content_view.visible_row_height()

        gr_proxy_item: QtWidgets.QGraphicsProxyWidget = QtWidgets.QGraphicsProxyWidget(self, QtCore.Qt.Widget)
        gr_proxy_item.setWidget(content_view)
        gr_proxy_item.setGeometry(QtCore.QRect(0, self._title_height, self._width, self._content_height))

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

    @property
    def index(self) -> QtCore.QModelIndex:
        return self._index

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._width, self._content_height + self._title_height)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(ColorPalette.LIGHTGRAY)))
        painter.drawRect(self.boundingRect())

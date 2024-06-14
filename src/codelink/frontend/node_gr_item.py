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
        self._content_height: int = 0

        self._node_background_color: QtGui.QColor = QtGui.QColor(ColorPalette.REGULARGRAY)
        self._selected_border_color: QtGui.QColor = QtGui.QColor(ColorPalette.HIGHLIGHT)
        self._node_background_brush: QtGui.QBrush = QtGui.QBrush(self._node_background_color)
        self._selected_border_pen: QtGui.QPen = QtGui.QPen(self._selected_border_color)
        self._selected_border_pen.setWidthF(1.5)

        self._title_item: QtWidgets.QGraphicsTextItem = self.create_title()
        self._content_item: QtWidgets.QGraphicsProxyWidget = self.create_content()

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

    @property
    def index(self) -> QtCore.QModelIndex:
        return self._index

    def create_title(self) -> QtWidgets.QGraphicsTextItem:
        text_item = QtWidgets.QGraphicsTextItem(self)
        text_item.setDefaultTextColor(QtGui.QColor(ColorPalette.WHITE))
        text_item.setPlainText(self._index.data(int(QtCore.Qt.DisplayRole)))
        return text_item

    def create_content(self) -> QtWidgets.QGraphicsProxyWidget:
        content_view: TreeView = TreeView()
        content_view.setMinimumHeight(0)
        content_view.setIndentation(0)
        content_view.setHeaderHidden(True)
        content_view.setModel(self._index.model())
        content_view.setRootIndex(self._index)
        content_view.expandAll()
        content_view.header().resizeSection(0, self._width // 2 - content_view.frameWidth())
        content_view.header().resizeSection(1, self._width // 2 - content_view.frameWidth())

        self._content_height: int = content_view.visible_row_height()

        proxy_item: QtWidgets.QGraphicsProxyWidget = QtWidgets.QGraphicsProxyWidget(self, QtCore.Qt.Widget)
        proxy_item.setWidget(content_view)
        proxy_item.setGeometry(QtCore.QRect(0, self._title_height, self._width, self._content_height))

        return proxy_item

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._width, self._content_height + self._title_height)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtCore.Qt.NoPen)
        if self.isSelected():
            painter.setPen(self._selected_border_pen)

        painter.setBrush(self._node_background_brush)
        painter.drawRect(self.boundingRect())

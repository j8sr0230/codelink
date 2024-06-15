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

from typing import Optional, cast

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
        self._title_padding_right: int = 5
        self._content_height: int = 0

        self._node_background_color: QtGui.QColor = QtGui.QColor(ColorPalette.REGULARGRAY)
        self._selected_border_color: QtGui.QColor = QtGui.QColor(ColorPalette.HIGHLIGHT)
        self._node_background_brush: QtGui.QBrush = QtGui.QBrush(self._node_background_color)
        self._selected_border_pen: QtGui.QPen = QtGui.QPen(self._selected_border_color)
        self._selected_border_pen.setWidthF(1.5)

        self._title_item: QtWidgets.QGraphicsTextItem = self.create_title()
        self._content_item: QtWidgets.QGraphicsProxyWidget = self.create_content()
        self._base_pins: list[QtWidgets.QGraphicsEllipseItem] = self.create_pins(
            index.model().index_from_key("Base", index)
        )

        self.setZValue(3)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

    @property
    def index(self) -> QtCore.QModelIndex:
        return self._index

    @staticmethod
    def crop_text(text: str = "Test", width: float = 30, font: QtGui.QFont = QtGui.QFont()) -> str:
        font_metrics: QtGui.QFontMetrics = QtGui.QFontMetrics(font)
        ellipsis_width: int = font_metrics.horizontalAdvance("...")
        cropped_text: str = ""
        total_width: int = 0

        for char in text:
            char_width: int = font_metrics.horizontalAdvance(char)
            if total_width + char_width + ellipsis_width > width:
                cropped_text += "..."
                break
            else:
                cropped_text += char
                total_width += char_width

        return cropped_text

    def create_title(self) -> QtWidgets.QGraphicsTextItem:
        text_item = QtWidgets.QGraphicsTextItem(self)
        text_item.setDefaultTextColor(QtGui.QColor(ColorPalette.WHITE))
        text_item.setZValue(3)
        return text_item

    def create_content(self) -> QtWidgets.QGraphicsProxyWidget:
        content_view: TreeView = TreeView()
        content_view.setUniformRowHeights(True)
        content_view.setIndentation(0)
        content_view.setHeaderHidden(True)
        content_view.setModel(self._index.model())
        content_view.setRootIndex(self._index)
        content_view.expandAll()
        content_view.header().resizeSection(0, self._width // 2 - content_view.frameWidth())
        content_view.header().resizeSection(1, self._width // 2 - content_view.frameWidth())
        content_view.collapsed.connect(self.on_collapsed)
        content_view.expanded.connect(self.on_collapsed)

        self._content_height: int = content_view.visible_row_height()

        proxy_item: QtWidgets.QGraphicsProxyWidget = QtWidgets.QGraphicsProxyWidget(self, QtCore.Qt.Widget)
        proxy_item.setWidget(content_view)
        proxy_item.setMinimumHeight(0)
        proxy_item.setZValue(3)
        return proxy_item

    def create_pins(self, sep_index: QtCore.QModelIndex) -> list[QtWidgets.QGraphicsEllipseItem]:
        pins: list[QtWidgets.QGraphicsEllipseItem] = []

        for i in range(self._index.model().rowCount(sep_index)):
            pin: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(self)
            pin.setBrush(QtGui.QBrush(QtCore.Qt.darkBlue))
            pin.setRect(QtCore.QRect(-5, -5, 10, 10))
            pin.setData(0, self._index.model().index(i, 0, sep_index))
            pin.setZValue(2)
            pins.append(pin)

        return pins

    def update_title(self) -> None:
        self._title_item.setPlainText(
            self.crop_text(
                self._index.data(int(QtCore.Qt.DisplayRole)),
                self._width - self._title_padding_right,
                self.scene().font())
        )

    def update_content_height(self) -> None:
        self._content_height: int = cast(TreeView, self._content_item.widget()).visible_row_height()
        self._content_item.setGeometry(QtCore.QRect(0, self._title_height, self._width, self._content_height))

    def update_pins(self, pins: list[QtWidgets.QGraphicsEllipseItem]):
        content_view: TreeView = self._content_item.widget()

        for pin in pins:
            index: QtCore.QModelIndex = pin.data(0)
            rect: QtCore.QRect = content_view.visualRect(index)
            if rect.isValid():
                pos: QtCore.QPoint = QtCore.QPoint(
                    rect.x(),
                    rect.y() + self._title_height + content_view.rowHeight(index) // 2 + content_view.frameWidth()
                )
            else:
                pos: QtCore.QPoint = QtCore.QPoint(
                    rect.x(),
                    rect.y() + self._title_height + content_view.rowHeight(index.parent()) // 2 + content_view.frameWidth()
                )
            pin.setPos(pos)

    # noinspection PyUnusedLocal
    def on_collapsed(self, index: QtCore.QModelIndex) -> None:
        self.update_content_height()
        self.update_pins(self._base_pins)


    def update(self, rect: Optional[QtCore.QRectF] = None) -> None:
        super().update()

        self.update_title()
        self.update_content_height()
        self.update_pins(self._base_pins)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._width, self._content_height + self._title_height)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtCore.Qt.NoPen)
        if self.isSelected():
            painter.setPen(self._selected_border_pen)

        painter.setBrush(self._node_background_brush)
        painter.drawRect(self.boundingRect())

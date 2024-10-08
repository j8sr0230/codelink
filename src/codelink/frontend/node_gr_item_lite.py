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

from typing import Optional, Any, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from codelink.backend.user_roles import UserRoles
# from codelink.backend.proxy_models import NodeViewProxyModel
from codelink.backend.outputs_seperator_item import OutputsSeperatorItem
from codelink.frontend.color_palette import ColorPalette
from codelink.frontend.pin_gr_item import PinGrItem
from codelink.frontend.tree_view import TreeView


class NodeGrItem(QtWidgets.QGraphicsItem):
    def __init__(self, persistent_index: QtCore.QPersistentModelIndex,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._persistent_index: QtCore.QPersistentModelIndex = persistent_index

        self._width: int = 100
        self._title_height: int = 20
        self._title_padding_right: int = 5
        self._content_height: int = 0
        self._pin_size: int = 10

        self._node_background_color: QtGui.QColor = QtGui.QColor(ColorPalette.REGULARGRAY)
        self._selected_border_color: QtGui.QColor = QtGui.QColor(ColorPalette.HIGHLIGHT)
        self._node_background_brush: QtGui.QBrush = QtGui.QBrush(self._node_background_color)
        self._selected_border_pen: QtGui.QPen = QtGui.QPen(self._selected_border_color)
        self._selected_border_pen.setWidthF(1.5)

        self._title_item: QtWidgets.QGraphicsTextItem = self.create_title()
        # self._content_item: CachableGrProxy = self.create_content()
        self._pins: list[list[QtWidgets.QGraphicsEllipseItem]] = self.create_pins()

        self._lm_pressed: bool = False
        self._mm_pressed: bool = False
        self._rm_pressed: bool = False

        self._moved: bool = False

        self._effect: QtWidgets.QGraphicsDropShadowEffect = QtWidgets.QGraphicsDropShadowEffect()
        self._effect.setOffset(5, 5)
        self._effect.setBlurRadius(25)
        self.setGraphicsEffect(self._effect)

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(3)

    @property
    def persistent_index(self) -> QtCore.QPersistentModelIndex:
        return self._persistent_index

    @property
    def pins(self) -> list[list[QtWidgets.QGraphicsEllipseItem]]:
        return self._pins

    @property
    def moved(self) -> bool:
        return self._moved

    @moved.setter
    def moved(self, value: bool) -> None:
        self._moved: bool = value

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
        # text_item.setTextInteractionFlags(QtCore.Qt.TextEditable)
        # text_item.setTextWidth(self._width)
        text_item.setZValue(3)
        return text_item

    def create_content(self) -> None:
        pass

    def create_pins_group(self, sep_index: QtCore.QModelIndex) -> list[PinGrItem]:
        pins: list[PinGrItem] = []

        for i in range(self._persistent_index.model().rowCount(sep_index)):
            index: QtCore.QModelIndex = self.persistent_index.model().index(i, 0, sep_index)
            pin: PinGrItem = PinGrItem(index.data(UserRoles.COLOR), self)
            pin.setData(0, QtCore.QPersistentModelIndex(index))
            pins.append(pin)

            pin_label: QtWidgets.QGraphicsTextItem = QtWidgets.QGraphicsTextItem(pin)
            pin_label.setDefaultTextColor(QtGui.QColor(ColorPalette.WHITE))
            pin_label.setPlainText(index.data(int(QtCore.Qt.DisplayRole)))
            pin_label.setZValue(3)
            # pin_label.setTextWidth(self._width)
            if sep_index.data(UserRoles.TYPE) == OutputsSeperatorItem:
                text_options: QtGui.QTextOption = pin_label.document().defaultTextOption()
                text_options.setAlignment(QtCore.Qt.AlignRight)
                pin_label.document().setDefaultTextOption(
                    text_options
                )

        return pins

    def create_pins(self) -> list[list[PinGrItem]]:
        pins: list[list[PinGrItem]] = []

        sep_indexes: list[QtCore.QModelIndex] = [
            self._persistent_index.model().index_from_key("Inputs", self._persistent_index),
            self._persistent_index.model().index_from_key("Outputs", self._persistent_index)
        ]

        for sep_index in sep_indexes:
            pins.append(self.create_pins_group(sep_index))

        return pins

    def index(self) -> QtCore.QModelIndex:
        if not self._persistent_index.isValid():
            return QtCore.QModelIndex()

        return QtCore.QModelIndex(self._persistent_index)

    def update_title(self) -> None:
        self._title_item.setPlainText(
            self.crop_text(
                self.persistent_index.data(int(QtCore.Qt.DisplayRole)),
                self._width - self._title_padding_right,
                self.scene().font())
        )

    def update_content_height(self) -> None:
        self._content_height: int = cast(TreeView, self._content_item.widget()).visible_row_height()
        self._content_item.setGeometry(QtCore.QRect(0, self._title_height, self._width, self._content_height))

    def update_pins(self):
        # content_view: TreeView = self._content_item.widget()
        # proxy: NodeViewProxyModel = content_view.model()

        for grp_idx, pin_group in enumerate(self._pins):
            for pin_idx, pin in enumerate(pin_group):
                # index: QtCore.QModelIndex = proxy.mapFromSource(pin.data(0))
                # index: QtCore.QModelIndex = proxy.index(index.row(), 0, index.parent())
                #
                # rect: QtCore.QRect = content_view.visualRect(index)
                # if not rect.isValid():
                #     index: QtCore.QModelIndex = index.parent()
                #     rect: QtCore.QRect = content_view.visualRect(index)
                # pin.snap_height = rect.height()

                # pos: QtCore.QPoint = QtCore.QPoint(
                #     rect.x() + grp_idx * (self._width - content_view.frameWidth()),
                #     rect.y() + self._title_height + content_view.rowHeight(index) // 2 + content_view.frameWidth()
                # )

                pos: QtCore.QPoint = QtCore.QPoint(
                    grp_idx * self._width,
                    self._title_height + (grp_idx + 1) * (pin_idx + 1) * 12
                )

                pin.setPos(pos)

    def update_position(self):
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable)
        pos: list[int] = self.persistent_index.data(UserRoles.POS)
        self.setPos(pos[0], pos[1])
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

    # noinspection PyUnusedLocal
    def on_collapsed(self, index: QtCore.QModelIndex) -> None:
        self.update_content_height()
        self.update_pins()

    def itemChange(self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            self._moved: bool = True
            return value
        else:
            return super().itemChange(change, value)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            self._lm_pressed: bool = True

        elif event.button() == QtCore.Qt.MiddleButton:
            self._mm_pressed: bool = True

        else:
            self._rm_pressed: bool = True

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            self._lm_pressed: bool = False

        elif event.button() == QtCore.Qt.MiddleButton:
            self._mm_pressed: bool = False

        else:
            self._rm_pressed: bool = False

    # def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
    #     super().hoverEnterEvent(event)
    #     self._content_item.selected = True
    #
    # def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
    #     self._content_item.clearFocus()
    #     self._content_item.selected = False
    #     super().hoverLeaveEvent(event)

    def update(self, rect: Optional[QtCore.QRectF] = None) -> None:
        super().update()

        self.update_title()
        # self.update_content_height()
        self.update_pins()
        self.update_position()

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._width, self._content_height + self._title_height + 80)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtCore.Qt.NoPen)
        if self.isSelected():
            painter.setPen(self._selected_border_pen)

        painter.setBrush(self._node_background_brush)
        painter.drawRect(self.boundingRect())

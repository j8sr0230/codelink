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

from codelink.backend.user_roles import UserRoles
from codelink.backend.document_model import DocumentModel
from codelink.frontend.node_gr_item import NodeGrItem


class DocumentGrView(QtWidgets.QGraphicsView):
    def __init__(self, model: DocumentModel, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self._model: DocumentModel = model

        self._lm_pressed: bool = False
        self._mm_pressed: bool = False
        self._rm_pressed: bool = False

        self._pressed_pin: Optional[QtWidgets.QGraphicsEllipseItem] = None

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            self._lm_pressed: bool = True

            if type(self.itemAt(event.pos())) == QtWidgets.QGraphicsEllipseItem:
                self._pressed_pin: QtWidgets.QGraphicsEllipseItem = self.itemAt(event.pos())
                print("Pin ModelIndex:", QtCore.QModelIndex(self._pressed_pin.data(0)))

        elif event.button() == QtCore.Qt.MiddleButton:
            self._mm_pressed: bool = True

        else:
            self._rm_pressed: bool = True

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)

        # if isinstance(self.itemAt(event.pos()), QtWidgets.QGraphicsProxyWidget):
        #     gr_proxy_widget: QtWidgets.QGraphicsProxyWidget = cast(
        #         QtWidgets.QGraphicsProxyWidget, self.itemAt(event.pos())
        #     )
        #     tree_view: QtWidgets.QTreeView = gr_proxy_widget.widget()
        #
        #     pos: QtCore.QPoint = self.mapToScene(event.pos()) - gr_proxy_widget.pos()
        #     print(tree_view.indexAt(QtCore.QPoint(pos.x(), pos.y())))

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            self._lm_pressed: bool = False
            self._pressed_pin: Optional[QtWidgets.QGraphicsEllipseItem] = None

            for item in self.scene().selectedItems():
                if hasattr(item, "moved") and item.moved:
                    item: NodeGrItem = cast(NodeGrItem, item)
                    pos: QtCore.QPoint = item.pos()
                    pos: list[int] = [pos.x(), pos.y()]
                    self._model.setData(item.index(), pos, UserRoles.POS)
                    item.moved = False

        elif event.button() == QtCore.Qt.MiddleButton:
            self._mm_pressed: bool = False

        else:
            self._rm_pressed: bool = False

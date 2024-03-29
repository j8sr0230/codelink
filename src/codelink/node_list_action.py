# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2023 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
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

from typing import Any, Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets


class NodeListModel(QtCore.QAbstractListModel):
    def __init__(self, node_actions: Optional[dict[str, QtWidgets.QAction]] = None,
                 parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)

        if node_actions is None:
            node_actions: dict = {}

        self._node_actions = node_actions

    @property
    def node_actions(self) -> dict:
        return self._node_actions

    @node_actions.setter
    def node_actions(self, value: dict) -> None:
        self._node_actions: dict = value

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self._node_actions.keys())

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self._node_actions.keys()):
            return None

        if role == QtCore.Qt.DisplayRole:
            key: str = list(self._node_actions.keys())[index.row()]
            return key


class NodeListAction(QtWidgets.QWidgetAction):
    def __init__(self, node_actions: dict[str, QtWidgets.QAction], parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        # Non persistent data model
        self._node_list_model: NodeListModel = NodeListModel(node_actions)
        self._filtered_node_list_model: QtCore.QSortFilterProxyModel = QtCore.QSortFilterProxyModel()
        self._filtered_node_list_model.setDynamicSortFilter(True)
        self._filtered_node_list_model.setSourceModel(self._node_list_model)
        self._filtered_node_list_model.sort(0, QtCore.Qt.AscendingOrder)
        self._filtered_node_list_model.setFilterKeyColumn(0)

    # --------------- Overwrites ---------------

    def createWidget(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        # Reset filter
        self._filtered_node_list_model.setFilterRegularExpression(
            QtCore.QRegularExpression(
                "",
                QtCore.QRegularExpression.CaseInsensitiveOption | QtCore.QRegularExpression.CaseInsensitiveOption)
        )

        # Main widget
        node_list_widget: QtWidgets.QWidget = QtWidgets.QWidget(parent)
        layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        node_list_widget.setLayout(layout)
        node_list_widget.setFixedWidth(150)
        node_list_widget.setFixedHeight(201)

        # Pattern input
        filter_pattern_input: QtWidgets.QLineEdit = QtWidgets.QLineEdit(node_list_widget)
        filter_pattern_input.setPlaceholderText("...")
        filter_pattern_input.textChanged.connect(self.node_filter_changed)
        layout.addWidget(filter_pattern_input)
        filter_pattern_input.setFocus()

        # Node list output
        filtered_node_list: QtWidgets.QListView = QtWidgets.QListView(node_list_widget)
        filtered_node_list.setSpacing(2)
        filtered_node_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        filtered_node_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        filtered_node_list.setModel(self._filtered_node_list_model)
        filtered_node_list.clicked.connect(self.on_clicked)
        layout.addWidget(filtered_node_list)

        return node_list_widget

    # --------------- Callbacks ---------------

    def node_filter_changed(self, text: str) -> None:
        self._filtered_node_list_model.setFilterRegularExpression(
            QtCore.QRegularExpression(
                text,
                QtCore.QRegularExpression.CaseInsensitiveOption | QtCore.QRegularExpression.CaseInsensitiveOption)
        )

    def on_clicked(self, model_index: QtCore.QModelIndex) -> None:
        self.associatedWidgets()[-1].parent().close()
        self._node_list_model.node_actions[self._filtered_node_list_model.data(model_index)].trigger()

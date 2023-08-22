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

from typing import Optional, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from item_delegates import BooleanDelegate, IntegerDelegate, StringDelegate
from property_model import PropertyModel
from property_table import PropertyTable
from node_item import NodeItem


class PropertyWidget(QtWidgets.QWidget):
	focus_changed: QtCore.Signal = QtCore.Signal(QtWidgets.QTableView)

	def __init__(self, node_item: Optional[NodeItem] = None, width: int = 250, parent: Optional[QtWidgets.QWidget] = None):
		super().__init__(parent)

		# Non persistent data model
		self._node_item: NodeItem = node_item

		# Widget geometry
		self._height: int = 0
		self._width: int = width

		# UI
		# Node property table
		self._layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()

		self._node_prop_table: PropertyTable = PropertyTable(self)
		self._node_prop_table.setModel(self._node_item.prop_model)

		# cast(QtCore.SignalInstance, self._node_prop_table.table_top_reached).connect(self.focus_up)
		cast(QtCore.SignalInstance, self._node_prop_table.table_bottom_reached).connect(self.focus_down)

		self._node_prop_table.setItemDelegateForRow(0, StringDelegate(self._node_prop_table))
		self._node_prop_table.setItemDelegateForRow(1, StringDelegate(self._node_prop_table))
		self._node_prop_table.setItemDelegateForRow(2, BooleanDelegate(self._node_prop_table))
		self._node_prop_table.setItemDelegateForRow(3, IntegerDelegate(self._node_prop_table))
		self._node_prop_table.setItemDelegateForRow(4, IntegerDelegate(self._node_prop_table))
		self._node_prop_table.setItemDelegateForRow(5, IntegerDelegate(self._node_prop_table))
		self._node_prop_table.setFixedHeight(
			self._node_prop_table.model().rowCount() * self._node_prop_table.rowHeight(0) +
			self._node_prop_table.horizontalHeader().height()
		)
		self._height += self._node_prop_table.height()
		self._layout.addWidget(self._node_prop_table)

		# Socket property tables
		for idx, socket_widget in enumerate(self._node_item.socket_widgets):
			socket_model: PropertyModel = socket_widget.prop_model
			socket_model.header_left = "Socket " + str(idx + 1) + " Prop"
			socket_prop_table: PropertyTable = PropertyTable(self)

			cast(QtCore.SignalInstance, socket_prop_table.table_top_reached).connect(self.focus_up)
			if idx < len(self._node_item.socket_widgets) - 1:
				cast(QtCore.SignalInstance, socket_prop_table.table_bottom_reached).connect(self.focus_down)

			socket_prop_table.setModel(socket_model)
			socket_prop_table.setFixedHeight(
				socket_prop_table.model().rowCount() * socket_prop_table.rowHeight(0) +
				socket_prop_table.horizontalHeader().height()
			)
			socket_prop_table.setItemDelegateForRow(0, StringDelegate(socket_prop_table))
			socket_prop_table.setItemDelegateForRow(1, IntegerDelegate(socket_prop_table))
			socket_prop_table.setItemDelegateForRow(2, BooleanDelegate(socket_prop_table))
			socket_prop_table.setItemDelegateForRow(3, BooleanDelegate(socket_prop_table))
			socket_prop_table.setItemDelegateForRow(4, BooleanDelegate(socket_prop_table))
			socket_prop_table.setItemDelegateForRow(5, BooleanDelegate(socket_prop_table))
			socket_prop_table.setItemDelegateForRow(6, BooleanDelegate(socket_prop_table))
			socket_prop_table.setItemDelegateForRow(7, BooleanDelegate(socket_prop_table))
			self._layout.addWidget(socket_prop_table)

		# Widget setup
		self._layout.setMargin(0)
		self._layout.setSpacing(0)
		self.setLayout(self._layout)
		self.setFixedWidth(self._width)

	def get_next_prop_table(self, current_table: QtWidgets.QTableView) -> QtWidgets.QTableView:
		table_views: list[QtWidgets.QTableView] = []
		for child in self.children():
			if type(child) == PropertyTable:
				table_views.append(child)

		table_index: int = table_views.index(current_table)
		table_index += 1
		if table_index == len(table_views):
			table_index = 0

		return table_views[table_index]

	def get_prev_prop_table(self, current_table: QtWidgets.QTableView) -> QtWidgets.QTableView:
		table_views: list[QtWidgets.QTableView] = []
		for child in self.children():
			if type(child) == PropertyTable:
				table_views.append(child)

		table_index: int = table_views.index(current_table)
		table_index -= 1
		if table_index == -1:
			table_index = len(table_views) - 1

		return table_views[table_index]

	# --------------- Callbacks for PropertyTable.table_top_reached and .table_bottom_reached signals ---------------

	def focus_up(self, current_table: QtWidgets.QTableView):
		current_table.clearFocus()
		current_table.clearSelection()

		next_table_view: QtWidgets.QTableView = self.get_prev_prop_table(current_table)
		next_table_view.setFocus()
		next_table_view.setCurrentIndex(next_table_view.model().index(
			next_table_view.model().rowCount() - 1, 1)
		)
		cast(QtCore.SignalInstance, self.focus_changed).emit(next_table_view)

	def focus_down(self, current_table: QtWidgets.QTableView):
		current_table.clearFocus()
		current_table.clearSelection()

		next_table_view: QtWidgets.QTableView = self.get_next_prop_table(current_table)
		next_table_view.setFocus()
		next_table_view.setCurrentIndex(next_table_view.model().index(0, 1))
		cast(QtCore.SignalInstance, self.focus_changed).emit(next_table_view)

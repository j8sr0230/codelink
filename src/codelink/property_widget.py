from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from item_delegates import BooleanDelegate, IntegerDelegate, StringDelegate
from property_table import PropertyTable
from node_item import NodeItem


class PropertyWidget(QtWidgets.QWidget):
	focus_changed: QtCore.Signal = QtCore.Signal(QtWidgets.QTableView)

	def __init__(self, node_item: Optional[NodeItem] = None, width: int = 250, parent: Optional[QtWidgets.QWidget] = None):
		super().__init__(parent)

		self._node_item: NodeItem = node_item

		self._height: int = 0
		self._width: int = width

		self._layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()

		self._node_prop_table: PropertyTable = PropertyTable(self)
		self._node_prop_table.setModel(self._node_item.prop_model)

		self._node_prop_table.table_top_reached.connect(self.focus_up)
		self._node_prop_table.table_bottom_reached.connect(self.focus_down)

		self._node_prop_table.setItemDelegateForRow(1, StringDelegate(self._node_prop_table))
		self._node_prop_table.setItemDelegateForRow(2, StringDelegate(self._node_prop_table))
		self._node_prop_table.setItemDelegateForRow(3, BooleanDelegate(self._node_prop_table))
		self._node_prop_table.setItemDelegateForRow(4, IntegerDelegate(self._node_prop_table))
		self._node_prop_table.setItemDelegateForRow(5, IntegerDelegate(self._node_prop_table))
		self._node_prop_table.setItemDelegateForRow(6, IntegerDelegate(self._node_prop_table))
		self._node_prop_table.setFixedHeight(
			self._node_prop_table.model().rowCount() * self._node_prop_table.rowHeight(0) +
			self._node_prop_table.horizontalHeader().height()
		)
		self._height += self._node_prop_table.height()
		self._layout.addWidget(self._node_prop_table)

		for idx, socket_widget in enumerate(self._node_item.socket_widgets):
			socket_model: PropertyModel = socket_widget.prop_model
			socket_model.header_left = "Socket " + str(idx + 1) + " Prop"
			socket_prop_table: PropertyTable = PropertyTable(self)

			socket_prop_table.table_top_reached.connect(self.focus_up)
			socket_prop_table.table_bottom_reached.connect(self.focus_down)

			socket_prop_table.setModel(socket_model)
			socket_prop_table.setFixedHeight(
				socket_prop_table.model().rowCount() * socket_prop_table.rowHeight(0) +
				socket_prop_table.horizontalHeader().height()
			)
			socket_prop_table.setItemDelegateForRow(1, StringDelegate(socket_prop_table))
			socket_prop_table.setItemDelegateForRow(2, BooleanDelegate(socket_prop_table))
			socket_prop_table.setItemDelegateForRow(3, IntegerDelegate(socket_prop_table))
			self._layout.addWidget(socket_prop_table)

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

	@QtCore.Slot(QtWidgets.QTableView)
	def focus_up(self, current_table: QtWidgets.QTableView):
		current_table.clearFocus()
		current_table.clearSelection()

		next_table_view: QtWidgets.QTableView = self.get_prev_prop_table(current_table)
		next_table_view.setFocus()
		next_table_view.setCurrentIndex(next_table_view.model().index(
			next_table_view.model().rowCount() - 1, 1)
		)
		self.focus_changed.emit(next_table_view)

	@QtCore.Slot(QtWidgets.QTableView)
	def focus_down(self, current_table: QtWidgets.QTableView):
		current_table.clearFocus()
		current_table.clearSelection()

		next_table_view: QtWidgets.QTableView = self.get_next_prop_table(current_table)
		next_table_view.setFocus()
		next_table_view.setCurrentIndex(next_table_view.model().index(0, 1))
		self.focus_changed.emit(next_table_view)

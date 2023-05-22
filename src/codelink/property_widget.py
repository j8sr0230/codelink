from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from item_delegates import BooleanDelegate, IntegerDelegate, StringDelegate
from property_table import PropertyTable
from node_item import NodeItem


class PropertyWidget(QtWidgets.QWidget):
	def __init__(self, node_item: Optional[NodeItem] = None, width: int = 250, parent: Optional[QtWidgets.QWidget] = None):
		super().__init__(parent)

		self._node_item: NodeItem = node_item

		self._height: int = 0
		self._width: int = width

		self._layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()

		self._node_prop_table: PropertyTable = PropertyTable(self)
		self._node_prop_table.setModel(self._node_item.prop_model)
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

	def get_next_prop_table(self, current_table: PropertyTable) -> PropertyTable:
		table_views: list[PropertyTable] = []
		for child in self.children():
			if type(child) == PropertyTable:
				table_views.append(child)

		table_index: int = table_views.index(current_table)
		table_index += 1
		if table_index == len(table_views):
			table_index = 0

		return table_views[table_index]

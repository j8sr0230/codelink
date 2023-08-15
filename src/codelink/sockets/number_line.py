from __future__ import annotations
from typing import TYPE_CHECKING, Optional, cast

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from socket_widget import SocketWidget
from input_widgets import NumberInputWidget

if TYPE_CHECKING:
	from node_item import NodeItem


class NumberLine(SocketWidget):
	def __init__(
			self, undo_stack: QtWidgets.QUndoStack, label: str = "A", is_input: bool = True, data: float = 0.,
			parent_node: Optional[NodeItem] = None, parent_widget: Optional[QtWidgets.QWidget] = None
	) -> None:
		super().__init__(undo_stack, label, is_input, data, parent_node, parent_widget)

		# Removes input widget placeholder from paren class
		self._layout.removeWidget(self._input_widget)
		self._input_widget.setParent(None)

		# Pin setup
		self._pin_item.color = QtGui.QColor("yellow")
		self._pin_item.pin_type = float

		# Input widget setup
		self._input_widget: NumberInputWidget = NumberInputWidget()
		self._input_widget.setMinimumWidth(5)
		self._input_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self._input_widget.setText(str(self._prop_model.properties["Data"]))
		self._layout.addWidget(self._input_widget)
		self._input_widget.setFocusPolicy(QtCore.Qt.StrongFocus)
		self.setFocusProxy(self._input_widget)

		self.update_stylesheets()

		# Listeners
		# cast(QtCore.SignalInstance, self._prop_model.dataChanged).connect(lambda: self.update_all())
		cast(QtCore.SignalInstance, self._input_widget.editingFinished).connect(self.editing_finished)
		# cast(QtCore.SignalInstance, self._input_widget.returnPressed).connect(self.return_pressed)

	# --------------- Socket data ---------------

	def input_data(self) -> list:
		result: list = []
		if self._pin_item.has_edges():
			for edge in self._pin_item.edges:
				pre_node: NodeItem = edge.start_pin.parent_node
				if len(pre_node.sub_scene.nodes) > 0:
					result.append(pre_node.linked_lowest_socket(edge.start_pin.socket_widget).pin)
				else:
					result.append(edge.start_pin)
		else:
			linked_highest: SocketWidget = self.parent_node.linked_highest_socket(self)
			if linked_highest != self:
				result.extend(linked_highest.input_data())

		if len(result) == 0:
			if self._input_widget.text() != "":
				result.append(float(self._input_widget.text()))
			else:
				result.append(0.)

		return result

	# --------------- Callbacks ---------------

	def update_stylesheets(self) -> None:
		if self._prop_model.properties["Is Input"]:
			self._label_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

			if self._pin_item.has_edges() or self.link != ("", -1):
				self._label_widget.setStyleSheet("background-color: transparent")
				self._input_widget.hide()
				self._input_widget.setFocusPolicy(QtCore.Qt.NoFocus)
			else:
				self._label_widget.setStyleSheet("background-color: #545454")
				self._input_widget.show()
				self._input_widget.setFocusPolicy(QtCore.Qt.StrongFocus)

		else:
			self._label_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
			self._label_widget.setStyleSheet("background-color: transparent")
			self._input_widget.hide()

	def update_all(self):
		super().update_all()
		self._input_widget.setText(str(self._prop_model.properties["Data"]))
		self._input_widget.clearFocus()

	def validate_input(self):
		last_value: float = self.prop_model.properties["Data"]
		input_txt: str = self._input_widget.text()

		try:
			input_number: float = float(input_txt)
			self._prop_model.setData(self._prop_model.index(2, 1, QtCore.QModelIndex()), input_number, 2)
		except ValueError:
			self._input_widget.setText(str(last_value))
			print("Wrong input format")

	def editing_finished(self) -> None:
		self.validate_input()
		self.clearFocus()

	def return_pressed(self) -> None:
		self.return_pressed()

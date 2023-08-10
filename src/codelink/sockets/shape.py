from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import FreeCAD
import Part

import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from socket_widget import SocketWidget

if TYPE_CHECKING:
	from node_item import NodeItem


class Shape(SocketWidget):
	def __init__(
			self, undo_stack: QtWidgets.QUndoStack, label: str = "Shape", is_input: bool = True,
			data: Part.Shape = Part.Shape(), parent_node: Optional[NodeItem] = None,
			parent_widget: Optional[QtWidgets.QWidget] = None
	) -> None:
		super().__init__(undo_stack, label, is_input, data, parent_node, parent_widget)

		# Pin setup
		self._pin_item.color = QtGui.QColor("blue")
		self._pin_item.pin_type = Part.Shape

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
			result.append(Part.Shape())

		return result

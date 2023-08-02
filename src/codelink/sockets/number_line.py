from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from socket_widget import SocketWidget

if TYPE_CHECKING:
	from node_item import NodeItem


class NumberLine(SocketWidget):
	def __init__(
			self, label: str = "A", is_input: bool = True, data: object = 0, parent_node: Optional[NodeItem] = None,
			parent_widget: Optional[QtWidgets.QWidget] = None
	) -> None:
		super().__init__(label, is_input, data, parent_node, parent_widget)

		self._pin_item.color = QtGui.QColor("yellow")

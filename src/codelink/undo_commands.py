from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from editor_scene import EditorScene
from node_item import NodeItem
from edge_item import EdgeItem


class DeleteNodeCommand(QtWidgets.QUndoCommand):

	def __init__(self, scene: QtWidgets.QGraphicsScene, parent: Optional[QtWidgets.QUndoCommand] = None):
		super().__init__(parent)

		self._scene: QtWidgets.QGraphicsScene = scene
		self._selected_nodes: list[NodeItem] = [item for item in scene.selectedItems() if type(item) == NodeItem]

	def undo(self) -> None:
		for node in self._selected_nodes:
			self._scene.nodes.append(node)
			self._scene.addItem(node)

	def redo(self) -> None:
		for node in self._selected_nodes:
			node.remove_from_frame()

			for socket_widget in node.socket_widgets:
				while len(socket_widget.pin.edges) > 0:
					edge: EdgeItem = socket_widget.pin.edges.pop()
					self._scene.remove_edge(edge)

			# noinspection PyTypeChecker
			node.content_widget.setParent(None)
			self._scene.removeItem(node)
			self._scene.nodes.remove(node)

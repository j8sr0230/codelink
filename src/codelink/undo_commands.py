from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from graph_scene import GraphScene
from frame_item import FrameItem
from node_item import NodeItem
from edge_item import EdgeItem


class DeleteSelectedCommand(QtWidgets.QUndoCommand):

	def __init__(self, scene: QtWidgets.QGraphicsScene, parent: Optional[QtWidgets.QUndoCommand] = None):
		super().__init__(parent)

		self._scene: QtWidgets.QGraphicsScene = scene
		self._selected_nodes: list[NodeItem] = [item for item in scene.selectedItems() if type(item) == NodeItem]
		self._connected_edges: list[EdgeItem] = []
		self._frames: list[FrameItem] = []

	def undo(self) -> None:
		for node in self._selected_nodes:
			self._scene.nodes.append(node)
			self._scene.addItem(node)

			if node.parent_frame:
				if node.parent_frame not in self._scene.frames:
					self._scene.add_frame(node.parent_frame)
				node.parent_frame.framed_nodes.append(node)

			for edge in self._connected_edges:
				self._scene.add_edge_from_pins(edge.start_pin, edge.end_pin)

	def redo(self) -> None:
		for node in self._selected_nodes:
			if node.parent_frame:
				self._frames.append(node.parent_frame)
				node.remove_from_frame()

			for socket_widget in node.socket_widgets:
				while len(socket_widget.pin.edges) > 0:
					edge: EdgeItem = socket_widget.pin.edges.pop()
					self._connected_edges.append(edge)
					self._scene.remove_edge(edge)

			# noinspection PyTypeChecker
			node.content_widget.setParent(None)
			self._scene.removeItem(node)
			self._scene.nodes.remove(node)

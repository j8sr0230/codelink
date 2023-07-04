from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import PySide2.QtWidgets as QtWidgets

from frame_item import FrameItem
from node_item import NodeItem
from edge_item import EdgeItem

if TYPE_CHECKING:
	from dag_scene import DAGScene


class DeleteSelectedCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, parent: Optional[QtWidgets.QUndoCommand] = None):
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._selected_nodes: list[NodeItem] = [item for item in scene.selectedItems() if type(item) == NodeItem]
		self._selected_edges: set[EdgeItem] = {item for item in scene.selectedItems() if type(item) == EdgeItem}
		self._selected_frames: set[FrameItem] = {item for item in scene.selectedItems() if type(item) == FrameItem}

	def undo(self) -> None:
		for node in self._selected_nodes:
			self._scene.add_node(node)

			if node.parent_frame:
				if node.parent_frame not in self._scene.frames:
					self._scene.add_frame(node.parent_frame)
				node.parent_frame.framed_nodes.append(node)

			for edge in self._selected_edges:
				self._scene.add_edge_from_pins(edge.start_pin, edge.end_pin)

		for edge in self._selected_edges:
			if edge not in self._scene.edges:
				self._scene.add_edge(edge)

		for frame in self._selected_frames:
			if frame not in self._scene.frames:
				self._scene.add_frame(frame)

	def redo(self) -> None:
		for frame in self._selected_frames:
			self._scene.remove_frame(frame)

		for edge in self._selected_edges:
			self._scene.remove_edge(edge)

		for node in self._selected_nodes:
			if node.parent_frame:
				self._selected_frames.add(node.parent_frame)

			for socket_widget in node.socket_widgets:
				while len(socket_widget.pin.edges) > 0:
					edge: EdgeItem = socket_widget.pin.edges.pop()
					self._selected_edges.add(edge)
					self._scene.remove_edge(edge)

			self._scene.remove_node(node)

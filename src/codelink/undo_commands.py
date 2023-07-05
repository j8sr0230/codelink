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
		self._selected_edges: list[EdgeItem] = [item for item in scene.selectedItems() if type(item) == EdgeItem]
		self._selected_frames: list[FrameItem] = [item for item in scene.selectedItems() if type(item) == FrameItem]

		self._linked_frames: dict[FrameItem, list[NodeItem]] = dict()
		self._linked_edges: set[EdgeItem] = set()

	def undo(self) -> None:
		for node in self._selected_nodes:
			self._scene.add_node(node)

			while len(self._linked_edges) > 0:
				edge: EdgeItem = self._linked_edges.pop()
				self._scene.add_edge(edge)

			for frame, framed_nodes in self._linked_frames.items():
				if frame not in self._scene.frames:
					self._scene.add_frame(frame)

				frame.framed_nodes.extend(framed_nodes)
				while len(framed_nodes) > 0:
					framed_node: NodeItem = framed_nodes.pop()
					framed_node.parent_frame = frame
					frame.update()

		for edge in self._selected_edges:
			if edge not in self._scene.edges:
				self._scene.add_edge(edge)

		for frame in self._selected_frames:
			if frame not in self._scene.frames:
				self._scene.add_frame(frame)
				for node in frame.framed_nodes:
					node.parent_frame = frame

	def redo(self) -> None:
		for frame in self._selected_frames:
			self._scene.remove_frame(frame)

		for edge in self._selected_edges:
			edge.mode = ""
			self._scene.remove_edge(edge)

		for node in self._selected_nodes:
			if node.parent_frame:
				if node.parent_frame not in self._linked_frames.keys():
					self._linked_frames[node.parent_frame] = []

				self._linked_frames[node.parent_frame].append(node)

			for socket_widget in node.socket_widgets:
				for edge in socket_widget.pin.edges:
					self._linked_edges.add(edge)

			self._scene.remove_node(node)

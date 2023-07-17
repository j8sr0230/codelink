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
		self._selected_node_states: list[dict] = []
		self._selected_edge_states: list[dict] = []
		self._selected_frame_states: list[dict] = []
		self._linked_frame_states: list[dict] = []

		# Copy states of selected and linked items
		selected_nodes: list[NodeItem] = [item for item in scene.selectedItems() if type(item) == NodeItem]

		selected_edges: set[EdgeItem] = {item for item in scene.selectedItems() if type(item) == EdgeItem}
		for node in selected_nodes:
			for socket_widget in node.socket_widgets:
				for edge in socket_widget.pin.edges:
					selected_edges.add(edge)

		selected_frames: set[FrameItem] = {item for item in scene.selectedItems() if type(item) == FrameItem}

		linked_frames: set[FrameItem] = {
			item.parent_frame for item in scene.selectedItems() if (
					type(item) == NodeItem and
					item.parent_frame is not None and
					item not in selected_frames
			)
		}

		self._selected_node_states: list[dict] = [node.__getstate__() for node in selected_nodes]
		self._selected_edge_states: list[dict] = [edge.__getstate__() for edge in selected_edges]
		self._selected_frame_states: list[dict] = [frame.__getstate__() for frame in selected_frames]
		self._linked_frame_states: list[dict] = [frame.__getstate__() for frame in linked_frames]

	def undo(self) -> None:
		self._scene.deserialize_nodes(self._selected_node_states)
		self._scene.deserialize_edges(self._selected_edge_states)
		self._scene.deserialize_frames(self._selected_frame_states)

		for state in self._linked_frame_states:
			self._scene.remove_frame(self._scene.dag_item(state["UUID"]))
			self._scene.deserialize_frames(self._linked_frame_states)

	def redo(self) -> None:
		for state in self._selected_frame_states:
			self._scene.remove_frame(self._scene.dag_item(state["UUID"]))

		for state in self._selected_edge_states:
			self._scene.remove_edge(self._scene.dag_item(state["UUID"]))

		for state in self._selected_node_states:
			self._scene.remove_node(self._scene.dag_item(state["UUID"]))

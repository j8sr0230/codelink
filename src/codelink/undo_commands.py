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
		self._old_scene_dict: dict = dict()

		self._selected_nodes_idx: list[int] = [
			scene.nodes.index(item) for item in scene.selectedItems() if type(item) == NodeItem
		]
		self._selected_edges_idx: list[int] = [
			scene.edges.index(item) for item in scene.selectedItems() if type(item) == EdgeItem
		]
		self._selected_frames_idx: list[int] = [
			scene.frames.index(item) for item in scene.selectedItems() if type(item) == FrameItem
		]

	def undo(self) -> None:
		self._scene.clear_scene()
		self._scene.deserialize(self._old_scene_dict)

	def redo(self) -> None:
		self._old_scene_dict: dict = self._scene.serialize()

		for idx in self._selected_frames_idx:
			self._scene.remove_frame(self._scene.frames[idx])

		for idx in self._selected_edges_idx:
			self._scene.remove_edge(self._scene.edges[idx])

		for idx in self._selected_nodes_idx:
			self._scene.remove_node(self._scene.nodes[idx])

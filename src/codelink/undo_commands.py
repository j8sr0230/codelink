from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import importlib

import PySide2.QtWidgets as QtWidgets

from frame_item import FrameItem
from node_item import NodeItem
from edge_item import EdgeItem

if TYPE_CHECKING:
	from dag_scene import DAGScene


class DeleteSelectedCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, parent: Optional[QtWidgets.QUndoCommand] = None):
		super().__init__(parent)

		dag_scene_cls: type = getattr(importlib.import_module("dag_scene"), "DAGScene")  # Hack: Prevents cyclic import

		self._scene: DAGScene = scene
		self._undo_scene_dict: dict = self._scene.serialize()  # Serialize current scene
		self._undo_scene: Optional[DAGScene] = dag_scene_cls()  # Empty new scene instance

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

		for node in self._undo_scene.nodes:
			self._scene.add_node(node)

		for edge in self._undo_scene.edges:
			self._scene.add_edge(edge)

		for frame in self._undo_scene.frames:
			self._scene.add_frame(frame)

	def redo(self) -> None:
		for idx in self._selected_nodes_idx:
			self._scene.remove_node(self._scene.nodes[idx])

		for idx in self._selected_edges_idx:
			self._scene.remove_edge(self._scene.edges[idx])

		for idx in self._selected_frames_idx:
			self._scene.remove_frame(self._scene.frames[idx])

		self._scene.update()
		self._undo_scene.deserialize(self._undo_scene_dict)  # Deserialize undo_scene here for performance reasons

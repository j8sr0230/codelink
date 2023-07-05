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

		self._selected_nodes: list[NodeItem] = [item for item in scene.selectedItems() if type(item) == NodeItem]
		self._selected_edges: list[EdgeItem] = [item for item in scene.selectedItems() if type(item) == EdgeItem]
		self._selected_frames: list[FrameItem] = [item for item in scene.selectedItems() if type(item) == FrameItem]

	def undo(self) -> None:
		self._scene.clear()
		self._scene.update()

		self._scene.deserialize(self._old_scene_dict)

	def redo(self) -> None:
		self._old_scene_dict: dict = self._scene.serialize()

		for frame in self._selected_frames:
			self._scene.remove_frame(frame)

		for edge in self._selected_edges:
			self._scene.remove_edge(edge)

		for node in self._selected_nodes:
			self._scene.remove_node(node)

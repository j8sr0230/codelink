from __future__ import annotations
import json
from typing import TYPE_CHECKING, Union, Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from frame_item import FrameItem
from node_item import NodeItem
from edge_item import EdgeItem

if TYPE_CHECKING:
	from editor_widget import EditorWidget
	from dag_scene import DAGScene
	from pin_item import PinItem


class DeleteSelectedCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
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
			if self._scene.dag_item(state["UUID"]) is not None:
				self._scene.remove_frame(self._scene.dag_item(state["UUID"]))
		self._scene.deserialize_frames(self._linked_frame_states)

	def redo(self) -> None:
		for state in self._selected_frame_states:
			self._scene.remove_frame(self._scene.dag_item(state["UUID"]))

		for state in self._selected_edge_states:
			self._scene.remove_edge(self._scene.dag_item(state["UUID"]))

		for state in self._selected_node_states:
			self._scene.remove_node(self._scene.dag_item(state["UUID"]))


class MoveSelectedCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene

		# Copy uuid's and positions of selected nodes
		self._undo_node_positions: list[tuple[str, float, float]] = [
			(item.uuid, item.last_position.x(), item.last_position.y()) for item in self._scene.selectedItems()
			if type(item) == NodeItem
		]
		self._redo_node_positions: list[tuple[str, float, float]] = self._undo_node_positions.copy()

	def undo(self) -> None:
		for idx, pos in enumerate(self._undo_node_positions):
			node: NodeItem = self._scene.dag_item(pos[0])

			# Store current node position
			self._redo_node_positions[idx] = (pos[0], node.x(), node.y())

			# Undo node movement
			x_row: int = list(node.prop_model.properties.keys()).index("X")
			y_row: int = list(node.prop_model.properties.keys()).index("Y")

			node.prop_model.setData(
				node.prop_model.index(x_row, 1, QtCore.QModelIndex()), pos[1], 2  # QtCore.Qt.EditRole
			)
			node.prop_model.setData(
				node.prop_model.index(y_row, 1, QtCore.QModelIndex()), pos[2], 2  # QtCore.Qt.EditRole
			)

	def redo(self) -> None:
		if self._undo_node_positions != self._redo_node_positions:
			for pos in self._redo_node_positions:
				node: NodeItem = self._scene.dag_item(pos[0])

				x_row: int = list(node.prop_model.properties.keys()).index("X")
				y_row: int = list(node.prop_model.properties.keys()).index("Y")

				node.prop_model.setData(
					node.prop_model.index(x_row, 1, QtCore.QModelIndex()), pos[1], 2  # QtCore.Qt.EditRole
				)
				node.prop_model.setData(
					node.prop_model.index(y_row, 1, QtCore.QModelIndex()), pos[2], 2  # QtCore.Qt.EditRole
				)


class AddItemCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, item: Union[NodeItem, EdgeItem, FrameItem],
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._item: Union[NodeItem, EdgeItem, FrameItem] = item

	def undo(self) -> None:
		if self._scene.dag_item(self._item.uuid) is not None:
			if type(self._item) == FrameItem:
				self._scene.remove_frame(self._item)
			elif type(self._item) == EdgeItem:
				self._scene.remove_edge(self._item)
			else:
				self._scene.remove_node(self._item)

	def redo(self) -> None:
		if self._scene.dag_item(self._item.uuid) is None:
			if type(self._item) == NodeItem:
				self._scene.add_node(self._item)
			elif type(self._item) == EdgeItem:
				self._scene.add_edge(self._item)
			else:
				self._scene.add_frame(self._item)


class RemoveItemCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, item: Union[NodeItem, EdgeItem, FrameItem],
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._item: Union[NodeItem, EdgeItem, FrameItem] = item

	def undo(self) -> None:
		if type(self._item) == NodeItem:
			self._scene.add_node(self._item)
		elif type(self._item) == EdgeItem:
			self._scene.add_edge(self._item)
		else:
			self._scene.add_frame(self._item)

	def redo(self) -> None:
		if type(self._item) == FrameItem:
			self._scene.remove_frame(self._item)
		elif type(self._item) == EdgeItem:
			self._scene.remove_edge(self._item)
		else:
			self._scene.remove_node(self._item)


class NodeFromNodeCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, nodes: list[NodeItem], parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._nodes_uuids: list[str] = [node.__getstate__()["UUID"] for node in nodes]
		self._custom_node_uuid: Optional[str] = None

	def undo(self) -> None:
		custom_node: NodeItem = self._scene.dag_item(self._custom_node_uuid)
		self._scene.resolve_node(custom_node)

	def redo(self) -> None:
		nodes: list[NodeItem] = [self._scene.dag_item(uuid) for uuid in self._nodes_uuids]
		custom_node = self._scene.add_node_from_nodes(nodes)
		self._custom_node_uuid = custom_node.uuid


class ResolveNodeCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, custom_nodes: list[NodeItem], parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._custom_node_uuids: list[str] = [custom_node.uuid for custom_node in custom_nodes]
		self._sub_nodes_uuids: list[list[str]] = []

	def undo(self) -> None:
		for idx, node_uuid_list in enumerate(self._sub_nodes_uuids):
			sub_nodes: list[NodeItem] = [self._scene.dag_item(node_uuid) for node_uuid in node_uuid_list]
			custom_node: NodeItem = self._scene.add_node_from_nodes(sub_nodes)

			# Reset custom uuid an adjust sub node links appropriately
			custom_node.uuid = self._custom_node_uuids[idx]
			for sub_node in custom_node.sub_scene.nodes:
				for socket_widget in sub_node.socket_widgets:
					if socket_widget.link[0] != "" and len(sub_node.sub_scene.nodes) == 0:
						socket_widget.link = (custom_node.uuid, socket_widget.link[1])

	def redo(self) -> None:
		custom_nodes: list[NodeItem] = [self._scene.dag_item(uuid) for uuid in self._custom_node_uuids]
		for custom_node in custom_nodes:
			if len(self._sub_nodes_uuids) == 0:
				self._sub_nodes_uuids.append([node.uuid for node in custom_node.sub_scene.nodes])
			self._scene.resolve_node(custom_node)


class RerouteEdgeCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, edge: EdgeItem, undo_pin: PinItem, redo_pin: PinItem,
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._edge_uuid: str = edge.uuid
		self._undo_pin_uuid: tuple[str, int] = undo_pin.uuid()
		self._redo_pin_uuid: tuple[str, int] = redo_pin.uuid()

	def undo(self) -> None:
		edge: EdgeItem = self._scene.dag_item(self._edge_uuid)
		edge.end_pin.remove_edge(edge)
		edge.end_pin.socket_widget.update_stylesheets()

		end_pin: PinItem = self._scene.dag_item(self._undo_pin_uuid[0]).socket_widgets[self._undo_pin_uuid[1]].pin
		edge.end_pin = end_pin
		edge.end_pin.add_edge(edge)
		edge.end_pin.socket_widget.update_stylesheets()

	def redo(self) -> None:
		edge: EdgeItem = self._scene.dag_item(self._edge_uuid)
		edge.end_pin.remove_edge(edge)
		edge.end_pin.socket_widget.update_stylesheets()

		end_pin: PinItem = self._scene.dag_item(self._redo_pin_uuid[0]).socket_widgets[self._redo_pin_uuid[1]].pin
		edge.end_pin = end_pin
		edge.end_pin.add_edge(edge)
		edge.end_pin.socket_widget.update_stylesheets()


class SwitchSceneDownCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, view: EditorWidget, redo_scene: DAGScene, undo_scene: DAGScene,
			parent_node: Optional[NodeItem] = None, parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._parent_node: NodeItem = parent_node
		self._view: EditorWidget = view
		self._redo_scene: DAGScene = redo_scene
		self._undo_scene: DAGScene = undo_scene

	def undo(self) -> None:
		# Note: Parent node, and it's sub scene may be new because of undone delete operation
		parent_node: NodeItem = self._undo_scene.dag_item(self._parent_node.uuid)  # Get the newest parent node
		parent_node.sub_scene = self._view.scene()  # Replace parents sub scene with the latest scene from here
		parent_node.sub_scene.parent_node = parent_node  # Link the new sub scene to the newest parent
		self._view.setScene(self._undo_scene)
		self._view.fit_in_content()

	def redo(self) -> None:
		self._view.setScene(self._redo_scene)
		self._view.fit_in_content()


class SwitchSceneUpCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, view: EditorWidget, redo_scene: DAGScene, undo_scene: DAGScene,
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._view: EditorWidget = view
		self._redo_scene: DAGScene = redo_scene
		self._undo_scene: DAGScene = undo_scene

	def undo(self) -> None:
		self._view.setScene(self._undo_scene)
		self._view.fit_in_content()

	def redo(self) -> None:
		self._view.setScene(self._redo_scene)
		self._view.fit_in_content()


class ToggleNodeCollapseCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, node: NodeItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._node_uuid: str = node.uuid

	def undo(self) -> None:
		self.redo()

	def redo(self) -> None:
		node: NodeItem = self._scene.dag_item(self._node_uuid)
		collapse_state: bool = not node.prop_model.properties["Collapse State"]
		collapse_mode_row: int = list(node.prop_model.properties.keys()).index("Collapse State")

		# noinspection PyTypeChecker
		node.prop_model.setData(
			node.prop_model.index(collapse_mode_row, 1, QtCore.QModelIndex()),
			collapse_state, QtCore.Qt.EditRole
		)


class ResizeNodeCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, node: NodeItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._node_uuid: str = node.uuid
		self._undo_width: int = node.last_width
		self._redo_width: int = node.boundingRect().width()

	def undo(self) -> None:
		node: NodeItem = self._scene.dag_item(self._node_uuid)

		width_row: int = list(node.prop_model.properties.keys()).index("Width")
		node.prop_model.setData(
			node.prop_model.index(width_row, 1, QtCore.QModelIndex()), self._undo_width, 2  # QtCore.Qt.EditRole
		)

	def redo(self) -> None:
		node: NodeItem = self._scene.dag_item(self._node_uuid)

		if self._undo_width != self._redo_width:
			width_row: int = list(node.prop_model.properties.keys()).index("Width")

			node.prop_model.setData(
				node.prop_model.index(width_row, 1, QtCore.QModelIndex()), self._redo_width, 2  # QtCore.Qt.EditRole
			)


class PasteClipboardCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._clipboard_state: dict = json.loads(QtWidgets.QApplication.clipboard().text())

	def undo(self) -> None:
		print("undo paste")

	def redo(self) -> None:
		# TODO: Generate new uuids for all items an crosslink them
		nodes: list[NodeItem] = self._scene.deserialize_nodes(self._clipboard_state["Nodes"])
		self._scene.deserialize_edges(self._clipboard_state["Edges"])
		self._scene.deserialize_frames(self._clipboard_state["Frames"])

		mouse_pos: QtCore.QPointF = self._scene.views()[0].mapToScene(
			self._scene.views()[0].mapFromParent(QtGui.QCursor.pos())
		)

		scene_bbox: QtCore.QRectF = self._scene.bounding_rect(nodes)
		scene_center: QtCore.QPointF = QtCore.QPointF(
			scene_bbox.x() + scene_bbox.width() / 2,
			scene_bbox.y() + scene_bbox.height() / 2
		)
		dx: float = mouse_pos.x() - scene_center.x()
		dy: float = mouse_pos.y() - scene_center.y()

		for node in nodes:
			node.setPos(dx + node.x(), dy + node.y())

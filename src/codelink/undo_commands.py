from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional, Any, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from utils import find_key_values, replace_key_values
from frame_item import FrameItem
from node_item import NodeItem
from edge_item import EdgeItem

if TYPE_CHECKING:
	from editor_widget import EditorWidget
	from dag_scene import DAGScene
	from pin_item import PinItem


class AddNodeCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, node: NodeItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._node: NodeItem = node

	def undo(self) -> None:
		self._scene.remove_node(self._node)

	def redo(self) -> None:
		self._scene.clearSelection()
		self._scene.add_node(self._node)
		self._node.setSelected(True)


class AddGrpNodeCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, grp_node: NodeItem, sub_nodes: list[NodeItem],
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._grp_node: NodeItem = grp_node
		self._sub_nodes: list[NodeItem] = sub_nodes

	def undo(self) -> None:
		self._scene.clearSelection()
		self._scene.resolve_grp_node(self._grp_node)

	def redo(self) -> None:
		self._scene.clearSelection()
		self._scene.add_node_grp(self._grp_node, self._sub_nodes)


class RemoveFromFrameCommand(QtWidgets.QUndoCommand):
	def __init__(self, node: NodeItem, frame: FrameItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._node: NodeItem = node
		self._frame: FrameItem = frame

	def undo(self) -> None:
		self._node.parent_frame = self._frame
		self._frame.framed_nodes.append(self._node)

	def redo(self) -> None:
		self._node.remove_from_frame()


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


class AddEdgeCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, edge: EdgeItem, parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._edge_state: dict = edge.__getstate__()

	def undo(self) -> None:
		self._scene.remove_edge(self._scene.dag_item(self._edge_state["UUID"]))

	def redo(self) -> None:
		if self._scene.dag_item(self._edge_state["UUID"]) is None:
			self._scene.deserialize_edges([self._edge_state])


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


class RemoveEdgeCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, edge: EdgeItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._edge_state: dict = edge.__getstate__()

	def undo(self) -> None:
		self._scene.deserialize_edges([self._edge_state])

	def redo(self) -> None:
		self._scene.remove_edge(self._scene.dag_item(self._edge_state["UUID"]))


class AddFrameCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, selected_nodes: list[NodeItem], parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._frame_uuid: str = ""
		self._selected_uuids: list[str] = [node.uuid for node in selected_nodes]

		self._old_parent_frames: dict[str, str] = {}
		for node in selected_nodes:
			if node.parent_frame is not None:
				self._old_parent_frames[node.uuid] = node.parent_frame.uuid
			else:
				self._old_parent_frames[node.uuid] = ""

	def undo(self) -> None:
		self._scene.remove_frame(self._scene.dag_item(self._frame_uuid))
		for node_uuid, old_frame_uuid in self._old_parent_frames.items():
			node: NodeItem = self._scene.dag_item(node_uuid)
			old_parent_frame: Optional[FrameItem] = self._scene.dag_item(old_frame_uuid)
			if old_parent_frame is not None:
				old_parent_frame.framed_nodes.append(node)
				node.parent_frame = old_parent_frame

	def redo(self) -> None:
		print("scene", self._scene)

		new_frame: FrameItem = self._scene.add_frame_from_nodes(
			[self._scene.dag_item(uuid) for uuid in self._selected_uuids]
		)
		if self._frame_uuid == "":
			self._frame_uuid = new_frame.uuid
		else:
			self._scene.dag_item(new_frame.uuid).uuid = self._frame_uuid

		self._scene.clearSelection()
		new_frame.setSelected(True)


class DeleteSelectedCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._selected_node_states: list[dict] = []
		self._selected_edge_states: list[dict] = []
		self._selected_frame_states: list[dict] = []
		self._linked_frame_states: list[dict] = []

		# Copy states of selected and linked items
		selected_nodes: list[NodeItem] = [item for item in scene.selectedItems() if isinstance(item, NodeItem)]

		selected_edges: set[EdgeItem] = {item for item in scene.selectedItems() if type(item) == EdgeItem}
		for node in selected_nodes:
			for socket_widget in node.socket_widgets:
				for edge in socket_widget.pin.edges:
					selected_edges.add(edge)

		selected_frames: set[FrameItem] = {item for item in scene.selectedItems() if type(item) == FrameItem}

		linked_frames: set[FrameItem] = {
			item.parent_frame for item in scene.selectedItems() if (
					isinstance(item, NodeItem) and
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
			if isinstance(item, NodeItem)
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


class SwitchSceneDownCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, view: EditorWidget, scene: DAGScene, parent_node_uuid: str,
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._view: EditorWidget = view
		self._scene: DAGScene = scene
		self._parent_node_uuid: str = parent_node_uuid

	def undo(self) -> None:
		self._view.setScene(self._scene)
		self._view.fit_in_content()

	def redo(self) -> None:
		print("sub", self._scene.dag_item(self._parent_node_uuid).sub_scene)
		self._view.setScene(self._scene.dag_item(self._parent_node_uuid).sub_scene)
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


class PasteClipboardCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene

		self._clipboard_state: dict = json.loads(QtWidgets.QApplication.clipboard().text())
		self._past_pos: QtCore.QPointF = self._scene.views()[0].mapToScene(
			self._scene.views()[0].mapFromParent(QtGui.QCursor.pos())
		)
		self._nodes: list[NodeItem] = []
		self._edges: list[EdgeItem] = []
		self._frames: list[FrameItem] = []

		# Replacement uuid map
		uuid_map: dict[str] = {
			uuid: QtCore.QUuid().createUuid().toString() for uuid in find_key_values(self._clipboard_state, "UUID")
		}

		# Replaces old uuids with new ones in clipboard state
		for k, v in uuid_map.items():
			replace_key_values(self._clipboard_state, "UUID", k, v)
			replace_key_values(self._clipboard_state, "Link", k, v)
			replace_key_values(self._clipboard_state, "Start Node UUID", k, v)
			replace_key_values(self._clipboard_state, "End Node UUID", k, v)
			replace_key_values(self._clipboard_state, "Framed Nodes UUID's", k, v)

	def undo(self) -> None:
		for frame in self._frames:
			self._scene.remove_frame(self._scene.dag_item(frame.uuid))
		for edge in self._edges:
			self._scene.remove_edge(self._scene.dag_item(edge.uuid))
		for node in self._nodes:
			self._scene.remove_node(self._scene.dag_item(node.uuid))

	def redo(self) -> None:
		self._nodes: list[NodeItem] = self._scene.deserialize_nodes(self._clipboard_state["Nodes"])
		self._edges: list[EdgeItem] = self._scene.deserialize_edges(self._clipboard_state["Edges"])
		self._frames: list[FrameItem] = self._scene.deserialize_frames(self._clipboard_state["Frames"])

		scene_bbox: QtCore.QRectF = self._scene.bounding_rect(self._nodes)
		scene_center: QtCore.QPointF = QtCore.QPointF(
			scene_bbox.x() + scene_bbox.width() / 2,
			scene_bbox.y() + scene_bbox.height() / 2
		)
		dx: float = self._past_pos.x() - scene_center.x()
		dy: float = self._past_pos.y() - scene_center.y()

		for node in self._nodes:
			node.setPos(dx + node.x(), dy + node.y())

		self._scene.clearSelection()
		to_be_selected: list[Any] = cast(list[QtWidgets.QGraphicsItem], self._nodes) + cast(
			list[QtWidgets.QGraphicsItem], self._frames)
		for item in to_be_selected:
			item.setSelected(True)

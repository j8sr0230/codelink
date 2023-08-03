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


class RemoveNodeFromFrameCommand(QtWidgets.QUndoCommand):
	def __init__(self, node: NodeItem, frame: FrameItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._node: NodeItem = node
		self._frame: FrameItem = frame

	def undo(self) -> None:
		self._node.parent_frame = self._frame
		self._frame.framed_nodes.append(self._node)

	def redo(self) -> None:
		self._node.remove_from_frame()


class ResolveGrpNodeCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, grp_node: NodeItem, parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._grp_node: NodeItem = grp_node
		self._sub_nodes: list[NodeItem] = grp_node.sub_scene.nodes

	def undo(self) -> None:
		self._scene.add_node_grp(self._grp_node, self._sub_nodes)

	def redo(self) -> None:
		self._scene.resolve_grp_node(self._grp_node)


class ToggleNodeCollapseCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, node: NodeItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._node = node

	def undo(self) -> None:
		self.redo()

	def redo(self) -> None:
		new_collapse_state: bool = not self._node.prop_model.properties["Collapse State"]
		collapse_mode_row: int = list(self._node.prop_model.properties.keys()).index("Collapse State")

		# noinspection PyTypeChecker
		self._node.prop_model.setData(
			self._node.prop_model.index(collapse_mode_row, 1, QtCore.QModelIndex()),
			new_collapse_state, QtCore.Qt.EditRole
		)


class ResizeNodeCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, node: NodeItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._node: NodeItem = node
		self._undo_width: int = node.last_width
		self._redo_width: int = node.boundingRect().width()

	def undo(self) -> None:
		width_row: int = list(self._node.prop_model.properties.keys()).index("Width")
		self._node.prop_model.setData(
			self._node.prop_model.index(width_row, 1, QtCore.QModelIndex()), self._undo_width, 2
		)

	def redo(self) -> None:
		if self._undo_width != self._redo_width:
			width_row: int = list(self._node.prop_model.properties.keys()).index("Width")

			self._node.prop_model.setData(
				self._node.prop_model.index(width_row, 1, QtCore.QModelIndex()), self._redo_width, 2
			)


class MoveNodesCommand(QtWidgets.QUndoCommand):
	def __init__(self, nodes: list[NodeItem], parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._nodes: list[NodeItem] = nodes
		self._undo_positions: dict[NodeItem, tuple[float, float]] = dict()
		for node in self._nodes:
			self._undo_positions[node] = (node.last_position.x(), node.last_position.y())

		self._redo_positions: dict[NodeItem, tuple[float, float]] = dict()

	def undo(self) -> None:
		for node, pos in self._undo_positions.items():
			self._redo_positions[node] = (node.x(), node.y())
			x_row: int = list(node.prop_model.properties.keys()).index("X")
			y_row: int = list(node.prop_model.properties.keys()).index("Y")
			node.prop_model.setData(node.prop_model.index(x_row, 1, QtCore.QModelIndex()), pos[0], 2)
			node.prop_model.setData(node.prop_model.index(y_row, 1, QtCore.QModelIndex()), pos[1], 2)

	def redo(self) -> None:
		for node, pos in self._redo_positions.items():
			x_row: int = list(node.prop_model.properties.keys()).index("X")
			y_row: int = list(node.prop_model.properties.keys()).index("Y")
			node.prop_model.setData(node.prop_model.index(x_row, 1, QtCore.QModelIndex()), pos[0], 2)
			node.prop_model.setData(node.prop_model.index(y_row, 1, QtCore.QModelIndex()), pos[1], 2)


class RemoveNodeCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, node: NodeItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._node: NodeItem = node

	def undo(self) -> None:
		self._scene.add_node(self._node)

	def redo(self) -> None:
		self._scene.remove_node(self._node)


class AddEdgeCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, edge: EdgeItem, parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._edge: EdgeItem = edge

	def undo(self) -> None:
		self._scene.remove_edge(self._edge)

	def redo(self) -> None:
		if self._edge not in self._scene.edges:
			self._scene.add_edge(self._edge)


class RerouteEdgeCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, edge: EdgeItem, undo_pin: PinItem, redo_pin: PinItem,
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._edge: EdgeItem = edge
		self._undo_pin: PinItem = undo_pin
		self._redo_pin: PinItem = redo_pin

	def undo(self) -> None:
		self._edge.end_pin.remove_edge(self._edge)
		self._edge.end_pin.socket_widget.update_stylesheets()

		self._edge.end_pin = self._undo_pin
		self._edge.end_pin.add_edge(self._edge)
		self._edge.end_pin.socket_widget.update_stylesheets()

	def redo(self) -> None:
		self._edge.end_pin.remove_edge(self._edge)
		self._edge.end_pin.socket_widget.update_stylesheets()

		self._edge.end_pin = self._redo_pin
		self._edge.end_pin.add_edge(self._edge)
		self._edge.end_pin.socket_widget.update_stylesheets()


class RemoveEdgeCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, edge: EdgeItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._edge: EdgeItem = edge

	def undo(self) -> None:
		self._scene.add_edge(self._edge)

	def redo(self) -> None:
		self._scene.remove_edge(self._edge)


class AddFrameCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, frame: FrameItem, parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._frame: FrameItem = frame

	def undo(self) -> None:
		self._scene.remove_frame(self._frame)

	def redo(self) -> None:
		if self._frame not in self._scene.frames:
			self._scene.add_frame(self._frame)
			for node in self._frame.framed_nodes:
				node.parent_frame = self._frame
			self._frame.setSelected(True)


class RemoveFrameCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, frame: FrameItem, parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._frame: FrameItem = frame

	def undo(self) -> None:
		self._scene.add_frame(self._frame)
		for node in self._frame.framed_nodes:
			node.parent_frame = self._frame
		self._frame.setSelected(True)

	def redo(self) -> None:
		self._scene.remove_frame(self._frame)


class SwitchSceneDownCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, view: EditorWidget, scene: DAGScene, parent_node: NodeItem,
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._view: EditorWidget = view
		self._scene: DAGScene = scene
		self._parent: NodeItem = parent_node

	def undo(self) -> None:
		self._view.setScene(self._scene)
		self._view.fit_in_content()

	def redo(self) -> None:
		self._view.setScene(self._parent.sub_scene)
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

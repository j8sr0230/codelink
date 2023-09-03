# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2023 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

if TYPE_CHECKING:
	from property_model import PropertyModel
	from editor_widget import EditorWidget
	from dag_scene import DAGScene
	from frame_item import FrameItem
	from node_item import NodeItem
	from input_widgets import OptionBoxWidget
	from socket_widget import SocketWidget
	from pin_item import PinItem
	from edge_item import EdgeItem


class AddNodeCommand(QtWidgets.QUndoCommand):
	def __init__(self, scene: DAGScene, node: NodeItem, parent: Optional[QtWidgets.QUndoCommand] = None) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._node: NodeItem = node

	def undo(self) -> None:
		self._scene.remove_node(self._node)
		for node in self._scene.ends():
			cast(QtCore.SignalInstance, self._scene.dag_changed).emit(node)

	def redo(self) -> None:
		self._scene.clearSelection()
		self._scene.add_node(self._node)
		cast(QtCore.SignalInstance, self._scene.dag_changed).emit(self._node)


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
		self._scene.resolve_sub_scene(self._grp_node)

	def redo(self) -> None:
		if self._grp_node not in self._scene.nodes:
			self._scene.add_node(self._grp_node)

		self._scene.populate_sub_scene(self._grp_node, self._sub_nodes)


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
		self._scene.add_node(self._grp_node)
		self._scene.populate_sub_scene(self._grp_node, self._sub_nodes)

	def redo(self) -> None:
		self._scene.resolve_sub_scene(self._grp_node)


class AddSocketCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, node: NodeItem, socket: SocketWidget, insert_idx: int,
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._node: NodeItem = node
		self._socket = socket
		self._insert_idx: int = insert_idx

	def undo(self) -> None:
		self._node.remove_socket_widget(self._insert_idx)
		self._node.scene().clearFocus()

	def redo(self) -> None:
		self._node.insert_socket_widget(self._socket, self._insert_idx)
		self._node.scene().clearFocus()


class RemoveSocketCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, node: NodeItem, remove_idx: int, parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._node: NodeItem = node
		self._remove_idx: int = remove_idx
		self._socket = node.socket_widgets[remove_idx]

	def undo(self) -> None:
		self._node.insert_socket_widget(self._socket, self._remove_idx)
		self._node.scene().clearFocus()

	def redo(self) -> None:
		self._node.remove_socket_widget(self._remove_idx)
		self._node.scene().clearFocus()


class SetOptionIndexCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, node: NodeItem, option_box: OptionBoxWidget, undo_idx: int, redo_idx,
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._node: NodeItem = node
		self._option_box: OptionBoxWidget = option_box
		self._undo_idx: int = undo_idx
		self._redo_idx: int = redo_idx

	def undo(self) -> None:
		self._option_box.blockSignals(True)
		self._option_box.setCurrentIndex(self._undo_idx)
		self._option_box.update()
		self._option_box.blockSignals(False)
		print("here")
		print(self._node.socket_widgets)

		# cast(QtCore.SignalInstance, self._node.scene().dag_changed).emit(self._node)

	def redo(self) -> None:
		if self._option_box.currentIndex() != self._redo_idx:
			self._option_box.blockSignals(True)
			self._option_box.setCurrentIndex(self._redo_idx)
			self._option_box.update()
			self._option_box.blockSignals(False)

		cast(QtCore.SignalInstance, self._node.scene().dag_changed).emit(self._node)


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
		cast(QtCore.SignalInstance, self._scene.dag_changed).emit(self._node)

	def redo(self) -> None:
		self._scene.remove_node(self._node)
		for node in self._scene.ends():
			cast(QtCore.SignalInstance, self._scene.dag_changed).emit(node)


class AddEdgeCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, edge: EdgeItem, parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._edge: EdgeItem = edge

	def undo(self) -> None:
		self._scene.remove_edge(self._edge)
		for node in self._scene.ends():
			cast(QtCore.SignalInstance, self._scene.dag_changed).emit(node)

	def redo(self) -> None:
		if self._edge not in self._scene.edges:
			self._scene.add_edge(self._edge)
		cast(QtCore.SignalInstance, self._scene.dag_changed).emit(self._edge.end_pin.parent_node)


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
		cast(QtCore.SignalInstance, self._scene.dag_changed).emit(self._edge.end_pin.parent_node)

	def redo(self) -> None:
		self._edge.end_pin.remove_edge(self._edge)
		self._edge.end_pin.socket_widget.update_stylesheets()

		self._edge.end_pin = self._redo_pin
		self._edge.end_pin.add_edge(self._edge)
		self._edge.end_pin.socket_widget.update_stylesheets()
		cast(QtCore.SignalInstance, self._scene.dag_changed).emit(self._edge.end_pin.parent_node)


class RemoveEdgeCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, edge: EdgeItem, is_silent: bool = False,
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._edge: EdgeItem = edge
		self._is_silent: bool = is_silent

	def undo(self) -> None:
		self._scene.add_edge(self._edge)
		if not self._is_silent:
			cast(QtCore.SignalInstance, self._scene.dag_changed).emit(self._edge.end_pin.parent_node)

	def redo(self) -> None:
		self._scene.remove_edge(self._edge)
		if not self._is_silent:
			for node in self._scene.ends():
				cast(QtCore.SignalInstance, self._scene.dag_changed).emit(node)


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
		for node in self._view.scene().nodes:
			node.setEnabled(False)
		self._view.setScene(self._scene)
		self._view.fit_content()

	def redo(self) -> None:
		self._view.setScene(self._parent.sub_scene)
		for node in self._view.scene().nodes:
			node.setEnabled(True)
		self._view.fit_content()


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
		for node in self._view.scene().nodes:
			node.setEnabled(True)
		self._view.fit_content()

	def redo(self) -> None:
		for node in self._view.scene().nodes:
			node.setEnabled(False)
		self._view.setScene(self._redo_scene)
		self._view.fit_content()


class PasteClipboardCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, scene: DAGScene, nodes: list[NodeItem], edges: list[EdgeItem], frames: list[FrameItem],
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._scene: DAGScene = scene
		self._nodes: list[NodeItem] = nodes
		self._edges: list[EdgeItem] = edges
		self._frames: list[FrameItem] = frames

	def undo(self) -> None:
		for frame in self._frames:
			self._scene.remove_frame(frame)
		for edge in self._edges:
			self._scene.remove_edge(edge)
		for node in self._nodes:
			self._scene.remove_node(node)

		for node in self._scene.ends():
			cast(QtCore.SignalInstance, self._scene.dag_changed).emit(node)

	def redo(self) -> None:
		for node in self._nodes:
			if node not in self._scene.nodes:
				self._scene.add_node(node)
		for edge in self._edges:
			if edge not in self._scene.edges:
				self._scene.add_edge(edge)
		for frame in self._frames:
			if frame not in self._scene.frames:
				self._scene.add_frame(frame)
				for node in frame.framed_nodes:
					node.parent_frame = frame

		for node in self._scene.ends():
			if node in self._nodes:
				cast(QtCore.SignalInstance, self._scene.dag_changed).emit(node)


class EditModelDataCommand(QtWidgets.QUndoCommand):
	def __init__(
			self, model: PropertyModel, model_index: QtCore.QModelIndex, old_data: object, new_data: object,
			parent: Optional[QtWidgets.QUndoCommand] = None
	) -> None:
		super().__init__(parent)

		self._model: PropertyModel = model
		self._index: QtCore.QModelIndex = model_index

		self._key: str = list(self._model.properties.keys())[self._index.row()]
		self._data_type = type(self._model.properties[self._key])
		self._old_data: object = old_data
		self._new_data: object = new_data

	@property
	def model(self) -> PropertyModel:
		return self._model

	@property
	def index(self) -> QtCore.QModelIndex:
		return self._index

	@property
	def key(self) -> str:
		return self._key

	def id(self) -> int:
		return 10

	def undo(self) -> None:
		self._model.properties[self._key] = self._old_data
		cast(QtCore.SignalInstance, self._model.dataChanged).emit(self._index, self._index)
		# print("Current:", self._new_data, "New:", self._old_data)

	def redo(self) -> None:
		self._model.properties[self._key] = self._new_data
		cast(QtCore.SignalInstance, self._model.dataChanged).emit(self._index, self._index)
		# print("Current:", self._old_data, "New:", self._new_data)

	def mergeWith(self, other: QtWidgets.QUndoCommand) -> bool:
		model: PropertyModel = cast(EditModelDataCommand, other).model
		key: str = cast(EditModelDataCommand, other).key

		if model != self._model:
			return False
		if key != self._key:
			return False

		self._new_data = model.properties[key]
		return True

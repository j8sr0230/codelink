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
from typing import Optional, Union, cast
import sys
import math
import json

from dask.threaded import get

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

import networkx as nx

from nodes import *
from frame_item import FrameItem
from node_item import NodeItem
from socket_widget import SocketWidget
from pin_item import PinItem
from edge_item import EdgeItem


class DAGScene(QtWidgets.QGraphicsScene):
    node_added: QtCore.Signal = QtCore.Signal(NodeItem)
    dag_changed: QtCore.Signal = QtCore.Signal(QtWidgets.QGraphicsItem, str)

    def __init__(self, undo_stack: QtWidgets.QUndoStack, parent: Optional[QtCore.QObject] = None):
        super().__init__(QtCore.QRectF(0, 0, 64000, 64000), parent)

        # Persistent data model
        self._frames: list[FrameItem] = []
        self._nodes: list[NodeItem] = []
        self._edges: list[EdgeItem] = []

        # Non persistent data model
        self._undo_stack: QtWidgets.QUndoStack = undo_stack
        self._clipboard: QtGui.QClipboard = QtWidgets.QApplication.clipboard()
        self._parent_node: Optional[NodeItem] = None
        self._zoom_level: int = 10

        # Background
        self._grid_spacing: int = 50

        # Assets
        self._background_color: QtGui.QColor = QtGui.QColor("#1D1D1D")
        self._grid_color: QtGui.QColor = QtGui.QColor("#282828")
        self._grid_pen: QtGui.QPen = QtGui.QPen(self._grid_color)
        self._grid_pen.setWidth(5)

        # Widget setup
        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
        self.setSortCacheEnabled(False)
        self.setStickyFocus(False)

        # Listeners
        cast(QtCore.SignalInstance, self.node_added).connect(lambda node: node.update_details(self._zoom_level))
        cast(QtCore.SignalInstance, self.dag_changed).connect(self.execute_dag)

    @property
    def frames(self) -> list[FrameItem]:
        return self._frames

    @frames.setter
    def frames(self, value: list[FrameItem]) -> None:
        self._frames: list[FrameItem] = value

    @property
    def nodes(self) -> list[NodeItem]:
        return self._nodes

    @nodes.setter
    def nodes(self, value: list[NodeItem]) -> None:
        self._nodes: list[NodeItem] = value

    @property
    def edges(self) -> list[EdgeItem]:
        return self._edges

    @edges.setter
    def edges(self, value: list[EdgeItem]) -> None:
        self._edges: list[EdgeItem] = value

    @property
    def parent_node(self) -> Optional[NodeItem]:
        return self._parent_node

    @parent_node.setter
    def parent_node(self, value: Optional[NodeItem]) -> None:
        self._parent_node: Optional[NodeItem] = value

    @property
    def background_color(self) -> QtGui.QColor:
        return self._background_color

    @background_color.setter
    def background_color(self, value: QtGui.QColor) -> None:
        self._background_color: QtGui.QColor = value

    # --------------- DAG editing ---------------

    def add_frame(self, frame: FrameItem) -> FrameItem:
        if frame.uuid == "":
            frame.uuid = QtCore.QUuid.createUuid().toString()

        cast(QtCore.SignalInstance, frame.prop_model.dataChanged).connect(
            lambda start_idx, end_idx: cast(QtCore.SignalInstance, self.dag_changed).emit(
                frame, list(frame.prop_model.properties.keys())[start_idx.row()]
            )
        )

        self._frames.append(frame)
        self.addItem(frame)
        return frame

    def remove_frame(self, frame: FrameItem) -> None:
        for node in frame.framed_nodes:
            node.parent_frame = None

        self.removeItem(frame)
        self._frames.remove(frame)

    def add_node(self, node: NodeItem) -> NodeItem:
        if node.uuid == "":
            node.uuid = QtCore.QUuid.createUuid().toString()

        cast(QtCore.SignalInstance, node.prop_model.dataChanged).connect(
            lambda start_idx, end_idx: cast(QtCore.SignalInstance, self.dag_changed).emit(
                node, list(node.prop_model.properties.keys())[start_idx.row()]
            )
        )

        registered_widgets: list[SocketWidget] = [
            child for child in node.content_widget.children() if isinstance(child, SocketWidget)
        ]
        if len(registered_widgets) == 0:
            node.register_sockets()
            node.update_all()
            node.register_evals()

        self._nodes.append(node)
        self.addItem(node)
        cast(QtCore.SignalInstance, self.node_added).emit(node)

        for socket_widget in node.input_socket_widgets + node.output_socket_widgets:
            socket_widget.pin.setParentItem(node)
            cast(QtCore.SignalInstance, socket_widget.prop_model.dataChanged).connect(
                lambda start_idx, end_idx: cast(QtCore.SignalInstance, self.dag_changed).emit(
                    socket_widget.parent_node, list(socket_widget.prop_model.properties.keys())[start_idx.row()]
                )
            )

        return node

    def populate_sub_scene(self, grp_node: NodeItem, nodes: list[NodeItem]) -> NodeItem:
        sub_edges: list[EdgeItem] = []
        for edge in self._edges:
            if edge.start_pin.parentItem() in nodes and edge.end_pin.parentItem() in nodes:
                sub_edges.append(edge)

        frames: set[FrameItem] = {node.parent_frame for node in nodes if node.parent_frame is not None}
        sub_frames: list[FrameItem] = []
        for sub_frame in frames:
            framed_nodes_set: set[NodeItem] = set(sub_frame.framed_nodes)
            sub_nodes_set: set[NodeItem] = set(nodes)
            if framed_nodes_set.issubset(sub_nodes_set):
                sub_frames.append(sub_frame)

        for sub_node in nodes:
            self._nodes.remove(sub_node)
            grp_node.sub_scene.add_node(sub_node)
            sub_node.setEnabled(False)

        for sub_edge in sub_edges:
            self._edges.remove(sub_edge)
            grp_node.sub_scene.add_edge(sub_edge)

        for sub_frame in sub_frames:
            self._frames.remove(sub_frame)
            grp_node.sub_scene.add_frame(sub_frame)

        socket_map: list[tuple[int, tuple[str, int]]] = [
            (idx, socket_widget.link) for idx, socket_widget in enumerate(grp_node.socket_widgets)
        ]
        for link in socket_map:
            sub_node: NodeItem = grp_node.sub_scene.dag_item(link[1][0])
            sub_socket: SocketWidget = sub_node.socket_widgets[link[1][1]]
            sub_socket.link = (grp_node.uuid, link[0])
            sub_socket.prop_model.properties["Name"] = sub_socket.prop_model.properties["Name"] + " ^"

        for sub_node in grp_node.sub_scene.nodes:
            for socket_idx, sub_socket_widget in enumerate(sub_node.socket_widgets):
                connected_edges: list[EdgeItem] = sub_socket_widget.pin.edges
                outer_socket_edges: list[EdgeItem] = [
                    edge for edge in connected_edges if edge not in grp_node.sub_scene.edges
                ]
                if len(outer_socket_edges) > 0:
                    grp_socket_widget: SocketWidget = grp_node.socket_widgets[sub_socket_widget.link[1]]
                    while len(outer_socket_edges) > 0:
                        edge: EdgeItem = outer_socket_edges.pop()

                        sub_socket_widget.pin.remove_edge(edge)
                        grp_socket_widget.pin.add_edge(edge)

                        if sub_socket_widget.is_input:
                            edge.end_pin = grp_socket_widget.pin
                        else:
                            edge.start_pin = grp_socket_widget.pin

                        sub_socket_widget.update_all()
                        grp_socket_widget.update_all()
                        edge.sort_pins()

        grp_node.sort_socket_widgets()
        return grp_node

    def resolve_sub_scene(self, grp_node: NodeItem):
        sub_scene_bbox: QtCore.QRectF = grp_node.sub_scene.itemsBoundingRect()
        sub_scene_center: QtCore.QPointF = QtCore.QPointF(
            sub_scene_bbox.x() + sub_scene_bbox.width() / 2,
            sub_scene_bbox.y() + sub_scene_bbox.height() / 2
        )

        for sub_node in grp_node.sub_scene.nodes:
            self.add_node(sub_node)
            sub_node.setEnabled(True)
            sub_node_pos: QtCore.QPointF = QtCore.QPointF(
                sub_node.x() + (grp_node.center.x() - sub_scene_center.x()),
                sub_node.y() + (grp_node.center.y() - sub_scene_center.y())
            )
            sub_node.setPos(sub_node_pos)
            sub_node.last_position = sub_node_pos

            for socket in sub_node.socket_widgets:
                if socket.prop_model.properties["Name"].endswith(" ^"):
                    socket.prop_model.properties["Name"] = socket.prop_model.properties["Name"][0:-2]
                socket.link = ("", -1)

        for sub_edge in grp_node.sub_scene.edges:
            self.add_edge(sub_edge)

        for sub_frame in grp_node.sub_scene.frames:
            self.add_frame(sub_frame)

        for socket_widget in grp_node.socket_widgets:
            socket_link: tuple[str, int] = socket_widget.link
            sub_node: NodeItem = self.dag_item(socket_link[0])
            sub_pin: PinItem = sub_node.socket_widgets[socket_link[1]].pin

            while len(socket_widget.pin.edges) > 0:
                edge: EdgeItem = socket_widget.pin.edges.pop()
                sub_pin.add_edge(edge)

                if socket_widget.is_input:
                    edge.end_pin = sub_pin
                else:
                    edge.start_pin = sub_pin
                sub_pin.socket_widget.update_all()

        grp_node.sub_scene.frames = []
        grp_node.sub_scene.edges = []
        grp_node.sub_scene.nodes = []
        self.remove_node(grp_node)

    def remove_node(self, node: NodeItem) -> None:
        if node.has_sub_scene():
            for sub_node in node.sub_scene.nodes:
                sub_node.on_remove()
        node.on_remove()

        for socket_widget in node.input_socket_widgets + node.output_socket_widgets:
            self.removeItem(socket_widget.pin)

        # noinspection PyTypeChecker
        node.content_widget.setParent(None)
        self.removeItem(node)
        self._nodes.remove(node)

    def add_edge(self, edge: EdgeItem) -> EdgeItem:
        if edge.uuid == "":
            edge.uuid = QtCore.QUuid.createUuid().toString()

        if type(edge.start_pin) == PinItem:
            edge.start_pin.add_edge(edge)
            edge.start_pin.socket_widget.update_stylesheets()

        if type(edge.end_pin) == PinItem:
            edge.end_pin.add_edge(edge)
            edge.end_pin.socket_widget.update_stylesheets()

        self._edges.append(edge)
        self.addItem(edge)

        return edge

    def add_edge_from_pins(self, start_pin: PinItem, end_pin: Union[QtWidgets.QGraphicsItem, PinItem]) -> EdgeItem:
        edge_color: QtGui.QColor = start_pin.color
        edge: EdgeItem = EdgeItem(color=edge_color)
        edge.uuid = QtCore.QUuid.createUuid().toString()

        edge.start_pin = start_pin
        edge.start_pin.add_edge(edge)
        edge.start_pin.socket_widget.update_stylesheets()

        edge.end_pin = end_pin
        if type(end_pin) == PinItem:
            edge.end_pin.add_edge(edge)
            end_pin.socket_widget.update_stylesheets()

        self._edges.append(edge)
        self.addItem(edge)

        return edge

    def remove_edge(self, edge: EdgeItem) -> None:
        if type(edge.start_pin) == PinItem and len(edge.start_pin.edges) > 0:
            if edge in edge.start_pin.edges:
                edge.start_pin.remove_edge(edge)
                edge.start_pin.socket_widget.update_stylesheets()

        if type(edge.end_pin) == PinItem and len(edge.end_pin.edges) > 0:
            if edge in edge.end_pin.edges:
                edge.end_pin.remove_edge(edge)
                edge.end_pin.socket_widget.update_stylesheets()

        self.removeItem(edge)
        self._edges.remove(edge)

    def remove_item(self, uuid: str) -> Union[NodeItem, EdgeItem, FrameItem, None]:
        item: Union[NodeItem, EdgeItem, FrameItem] = self.dag_item(uuid)

        if isinstance(item, NodeItem):
            self.remove_node(item)
        elif type(item) == EdgeItem:
            self.remove_edge(item)
        else:
            self.remove_frame(item)

        return item

    def selection_to_clipboard(self):
        # Copy states of selected and linked items
        selected_nodes: list[NodeItem] = self.selected_nodes()
        selected_edges: list[EdgeItem] = [item for item in self.selectedItems() if (
                type(item) == EdgeItem and
                item.start_pin.parentItem() in selected_nodes and
                item.end_pin.parentItem() in selected_nodes
        )]
        selected_frames: list[FrameItem] = self.selected_frames()

        selected_node_states: list[dict] = [node.__getstate__() for node in selected_nodes]
        selected_edge_states: list[dict] = [edge.__getstate__() for edge in selected_edges]
        selected_frame_states: list[dict] = [frame.__getstate__() for frame in selected_frames]

        # Create state dict
        selection_state: dict = {
            "Nodes": selected_node_states,
            "Edges": selected_edge_states,
            "Frames": selected_frame_states
        }

        # Push mime data to clipboard
        mime_data: QtCore.QMimeData = QtCore.QMimeData()
        mime_data.setText(json.dumps(selection_state, indent=4))
        self._clipboard.setMimeData(mime_data)

    # --------------- DAG analytics ---------------

    def dag_item(self, uuid: str = "") -> Any:
        all_items: list = (
                cast(list[QtWidgets.QGraphicsItem], self._frames) +
                cast(list[QtWidgets.QGraphicsItem], self._nodes) +
                cast(list[QtWidgets.QGraphicsItem], self._edges)
        )
        result: list[Any] = [item for item in all_items if item.uuid == uuid]

        if len(result) == 1:
            return result[0]
        else:
            return None

    def selected_nodes(self) -> list[NodeItem]:
        return [item for item in self.selectedItems() if isinstance(item, NodeItem)]

    def selected_edges(self) -> list[EdgeItem]:
        return [item for item in self.selectedItems() if isinstance(item, EdgeItem)]

    def selected_frames(self) -> list[FrameItem]:
        return [item for item in self.selectedItems() if isinstance(item, FrameItem)]

    @staticmethod
    def bounding_rect(nodes: list[NodeItem], offset: int = 0) -> QtCore.QRectF:
        if len(nodes) > 0:
            x_min: float = min([node.x() for node in nodes]) - offset
            x_max: float = max([node.x() + node.boundingRect().width() for node in nodes]) + offset
            y_min: float = min([node.y() for node in nodes]) - offset
            y_max: float = max([node.y() + node.boundingRect().height() for node in nodes]) + offset
            return QtCore.QRectF(x_min, y_min, x_max - x_min, y_max - y_min)
        else:
            return QtCore.QRectF(-offset, -offset, offset, offset)

    @staticmethod
    def outside_frames(nodes: list[NodeItem]) -> list[FrameItem]:
        inside_frames: set[FrameItem] = set()
        all_frames: set[FrameItem] = {node.parent_frame for node in nodes if node.parent_frame is not None}

        for frame in all_frames:
            if set(frame.framed_nodes).issubset(nodes):
                inside_frames.add(frame)

        return list(all_frames.difference(inside_frames))

    def grp_interfaces(self, nodes: list[NodeItem]) -> set[NodeItem]:
        result: set[NodeItem] = set()
        for node in nodes:
            if node.has_sub_scene():
                if node.has_in_edges():
                    pre_pres: list[list[NodeItem]] = [pre.predecessors() for pre in node.successors()]
                    flat_pre_pres: list[NodeItem] = [node for sub_list in pre_pres for node in sub_list]
                    if set(flat_pre_pres).issubset(set(self._nodes).difference(set(nodes))):
                        result.add(node)

                if node.has_out_edges():
                    suc_succs: list[list[NodeItem]] = [suc.successors() for suc in node.predecessors()]
                    flat_suc_succs: list[NodeItem] = [node for sub_list in suc_succs for node in sub_list]
                    if set(flat_suc_succs).issubset(set(self._nodes).difference(set(nodes))):
                        result.add(node)
            else:
                if node.has_in_edges() and set(node.predecessors()).issubset(set(self._nodes).difference(set(nodes))):
                    result.add(node)
                if node.has_out_edges() and set(node.successors()).issubset(set(self._nodes).difference(set(nodes))):
                    result.add(node)

        return result

    def ends(self) -> list[NodeItem]:
        result: list[NodeItem] = []
        for node in self._nodes:
            if not node.has_out_edges():
                result.append(node)
        return result

    def _path_ends(self, current_node: NodeItem, result: list[NodeItem]) -> None:
        if len(current_node.successors()) == 0:
            result.append(current_node)
        else:
            for suc_node in current_node.successors():
                self._path_ends(suc_node, result)

    def path_ends(self, node: NodeItem) -> list[NodeItem]:
        result: list[NodeItem] = []
        self._path_ends(node, result)
        return result

    def mark_successors_invalid(self, node: NodeItem) -> None:
        node.is_invalid = True
        node.cache = [None] * len(node.evals)
        for suc_node in node.successors():
            self.mark_successors_invalid(suc_node)

    def to_dsk(self, visited_node: NodeItem, graph_dict: dict) -> dict:
        for node in visited_node.predecessors():
            self.to_dsk(node, graph_dict)

        task_inputs: list = []
        for socket_widget in visited_node.input_socket_widgets:
            if socket_widget.is_input:
                task_inputs.append(socket_widget.input_data())

        for idx, socket_widget in enumerate(visited_node.output_socket_widgets):
            if not socket_widget.is_input:
                graph_dict[socket_widget.pin] = (visited_node.evals[idx], *task_inputs)

        return graph_dict

    def to_nx(self) -> nx.DiGraph:
        nx_graph: nx.DiGraph = nx.DiGraph()
        for edge in self._edges:
            if edge.start_pin.socket_widget.is_input:
                nx_graph.add_edge(
                    edge.start_pin.parent_node,
                    edge.end_pin.parent_node
                )
            else:
                nx_graph.add_edge(
                    edge.end_pin.parent_node,
                    edge.start_pin.parent_node
                )
        return nx_graph

    def is_cyclic(self) -> bool:
        nx_graph: nx.DiGraph = self.to_nx()
        result: bool = True
        try:
            nx.find_cycle(nx_graph)
        except nx.exception.NetworkXNoCycle:
            result: bool = False
        return result

    def is_sub_scene(self) -> bool:
        return self._parent_node is not None

    def execute_dag(self, item: Union[NodeItem, FrameItem], prop_key: str = ""):
        if isinstance(item, NodeItem):
            if prop_key not in ("Name", "Color", "Collapsed", "X", "Y", "Width"):
                self.mark_successors_invalid(item)

                for end_node in self.path_ends(item):
                    dsk: dict = self.to_dsk(end_node, {})
                    for socket in end_node.output_socket_widgets:
                        get(dsk, end_node.linked_lowest_socket(socket).pin)
                        # print(get(dsk, end_node.linked_lowest_socket(socket).pin))

    # --------------- Background ---------------

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)
        self.setBackgroundBrush(self._background_color)

        if self._zoom_level is not None:
            if self._zoom_level >= 9:

                bound_box_left: int = int(math.floor(rect.left()))
                bound_box_right: int = int(math.ceil(rect.right()))
                bound_box_top: int = int(math.floor(rect.top()))
                bound_box_bottom: int = int(math.ceil(rect.bottom()))

                first_left: int = bound_box_left - (bound_box_left % self._grid_spacing)
                first_top: int = bound_box_top - (bound_box_top % self._grid_spacing)

                points: list[Optional[QtCore.QPoint]] = []
                for x in range(first_left, bound_box_right, self._grid_spacing):
                    for y in range(first_top, bound_box_bottom, self._grid_spacing):
                        points.append(QtCore.QPoint(x, y))

                painter.setPen(self._grid_pen)
                painter.drawPoints(points)

        else:
            bound_box_left: int = int(math.floor(rect.left()))
            bound_box_right: int = int(math.ceil(rect.right()))
            bound_box_top: int = int(math.floor(rect.top()))
            bound_box_bottom: int = int(math.ceil(rect.bottom()))

            first_left: int = bound_box_left - (bound_box_left % self._grid_spacing)
            first_top: int = bound_box_top - (bound_box_top % self._grid_spacing)

            points: list[Optional[QtCore.QPoint]] = []
            for x in range(first_left, bound_box_right, self._grid_spacing):
                for y in range(first_top, bound_box_bottom, self._grid_spacing):
                    points.append(QtCore.QPoint(x, y))

            painter.setPen(self._grid_pen)
            painter.drawPoints(points)

    # --------------- Callbacks ---------------

    def update_details(self, zoom_level: int):
        self._zoom_level: int = zoom_level
        for node in self._nodes:
            node.update_details(self._zoom_level)

    # --------------- Serialization ---------------

    def clear_scene(self):
        while len(self._frames) > 0:
            frame: FrameItem = self._frames[-1]
            self.remove_frame(frame)

        while len(self._edges) > 0:
            edge: EdgeItem = self._edges[-1]
            self.remove_edge(edge)

        while len(self._nodes) > 0:
            node: NodeItem = self._nodes[-1]
            self.remove_node(node)

        self.clear()
        self.update()

    def serialize_nodes(self) -> list[dict]:
        nodes_dict: list[dict] = []

        for node in self._nodes:
            nodes_dict.append(node.__getstate__())

        return nodes_dict

    def deserialize_nodes(self, nodes_dict: list[dict]) -> list[NodeItem]:
        deserialized_nodes: list[NodeItem] = []

        for node_dict in nodes_dict:

            # Create node from dict
            node_class: type = getattr(sys.modules[__name__], node_dict["Class"])
            node_pos: tuple = (node_dict["Properties"]["X"], node_dict["Properties"]["Y"])
            new_node: node_class = node_class(node_pos, self._undo_stack)
            self.add_node(new_node)

            # Reset node state
            new_node.__setstate__(node_dict)
            deserialized_nodes.append(new_node)
            self.update()

        return deserialized_nodes

    def serialize_edges(self) -> list[dict]:
        edges_dict: list[dict] = []

        for edge in self._edges:
            edges_dict.append(edge.__getstate__())

        return edges_dict

    def deserialize_edges(self, edges_dict: list[dict]) -> list[EdgeItem]:
        deserialized_edges: list[EdgeItem] = []

        for edge_dict in edges_dict:
            start_node: NodeItem = self.dag_item(edge_dict["Start Node UUID"])
            start_socket_widget: SocketWidget = start_node.socket_widgets[edge_dict["Start Socket Idx"]]
            start_pin: PinItem = start_socket_widget.pin

            end_node: NodeItem = self.dag_item(edge_dict["End Node UUID"])
            end_socket_widget: SocketWidget = end_node.socket_widgets[edge_dict["End Socket Idx"]]
            end_pin: PinItem = end_socket_widget.pin

            new_edge: EdgeItem = self.add_edge_from_pins(start_pin, end_pin)

            # Reset edge state
            new_edge.__setstate__(edge_dict)
            deserialized_edges.append(new_edge)
            self.update()

        return deserialized_edges

    def serialize_frames(self) -> list[dict]:
        frames_dict: list[dict] = []

        for frame in self._frames:
            frames_dict.append(frame.__getstate__())

        return frames_dict

    def deserialize_frames(self, frames_dict: list[dict]) -> list[FrameItem]:
        deserialized_frames: list[FrameItem] = []

        for frame_dict in frames_dict:
            framed_nodes_uuid: list[str] = frame_dict["Framed Nodes UUID's"]
            framed_nodes: list[NodeItem] = [self.dag_item(uuid) for uuid in framed_nodes_uuid]
            new_frame: FrameItem = FrameItem(framed_nodes, self._undo_stack)
            self.add_frame(new_frame)

            # Reset frame state
            new_frame.__setstate__(frame_dict)
            deserialized_frames.append(new_frame)
            self.update()

        return deserialized_frames

    def serialize(self) -> dict:
        dag_dict: dict = {
            "Nodes": self.serialize_nodes(),
            "Edges": self.serialize_edges(),
            "Frames": self.serialize_frames()
        }
        return dag_dict

    def deserialize(self, data_dict: dict) -> None:
        self.deserialize_nodes(data_dict["Nodes"])
        self.deserialize_edges(data_dict["Edges"])
        self.deserialize_frames(data_dict["Frames"])

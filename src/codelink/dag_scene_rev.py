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

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

import networkx as nx

from nodes import *
from frame_item import FrameItem
from node_item_rev import NodeItemRev
from socket_item_rev import SocketItemRev
from edge_item import EdgeItem


class DAGSceneRev(QtWidgets.QGraphicsScene):
    node_added: QtCore.Signal = QtCore.Signal(NodeItem)

    def __init__(self, undo_stack: QtWidgets.QUndoStack, parent: Optional[QtCore.QObject] = None):
        super().__init__(QtCore.QRectF(0, 0, 64000, 64000), parent)

        # Persistent data model
        self._frames: list[FrameItem] = []
        self._nodes: list[NodeItemRev] = []
        self._edges: list[EdgeItem] = []

        # Non persistent data model
        self._undo_stack: QtWidgets.QUndoStack = undo_stack
        self._parent_node: Optional[NodeItem] = None
        self._clipboard: QtGui.QClipboard = QtWidgets.QApplication.clipboard()
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

        # Listeners
        cast(QtCore.SignalInstance, self.node_added).connect(lambda node: node.update_details(self._zoom_level))

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

        self._frames.append(frame)
        self.addItem(frame)
        return frame

    def remove_frame(self, frame: FrameItem) -> None:
        for node in frame.framed_nodes:
            node.parent_frame = None

        self.removeItem(frame)
        self._frames.remove(frame)

    def add_node(self, node: NodeItemRev) -> NodeItemRev:
        if node.uuid == "":
            node.prop_model.properties["UUID"] = QtCore.QUuid.createUuid().toString()

        self._nodes.append(node)
        self.addItem(node)
        cast(QtCore.SignalInstance, self.node_added).emit(node)
        return node

    def populate_sub_scene(self, grp_node: NodeItemRev, nodes: list[NodeItemRev]) -> NodeItemRev:
        sub_edges: list[EdgeItem] = []
        for edge in self._edges:
            if edge.start_pin.parentItem() in nodes and edge.end_pin.parentItem() in nodes:
                sub_edges.append(edge)

        frames: set[FrameItem] = {node.parent_frame for node in nodes if node.parent_frame is not None}
        sub_frames: list[FrameItem] = []
        for sub_frame in frames:
            framed_nodes_set: set[NodeItemRev] = set(sub_frame.framed_nodes)
            sub_nodes_set: set[NodeItemRev] = set(nodes)
            if framed_nodes_set.issubset(sub_nodes_set):
                sub_frames.append(sub_frame)

        for sub_node in nodes:
            self._nodes.remove(sub_node)
            grp_node.sub_scene.add_node(sub_node)

        for sub_edge in sub_edges:
            self._edges.remove(sub_edge)
            grp_node.sub_scene.add_edge(sub_edge)

        for sub_frame in sub_frames:
            self._frames.remove(sub_frame)
            grp_node.sub_scene.add_frame(sub_frame)

        input_map: list[tuple[int, tuple[str, int]]] = [
            (idx, input_socket.link) for idx, input_socket in enumerate(grp_node.inputs)
        ]
        for link in input_map:
            sub_node: NodeItemRev = grp_node.sub_scene.dag_item(link[1][0])
            sub_socket: SocketItemRev = sub_node.inputs[link[1][1]]
            sub_socket.prop_model.properties["Link"] = (grp_node.uuid, link[0])
            sub_socket.prop_model.properties["Name"] = sub_socket.prop_model.properties["Name"] + " ^"

        output_map: list[tuple[int, tuple[str, int]]] = [
            (idx, output_socket.link) for idx, output_socket in enumerate(grp_node.outputs)
        ]
        for link in output_map:
            sub_node: NodeItemRev = grp_node.sub_scene.dag_item(link[1][0])
            sub_socket: SocketItemRev = sub_node.outputs[link[1][1]]
            sub_socket.prop_model.properties["Link"] = (grp_node.uuid, link[0])
            sub_socket.prop_model.properties["Name"] = sub_socket.prop_model.properties["Name"] + " ^"

        for sub_node in grp_node.sub_scene.nodes:
            for sub_input in sub_node.inputs:
                connected_edges: list[EdgeItem] = sub_input.edges
                outer_socket_edges: list[EdgeItem] = [
                    edge for edge in connected_edges if edge not in grp_node.sub_scene.edges
                ]
                if len(outer_socket_edges) > 0:
                    grp_input: SocketItemRev = grp_node.inputs[sub_input.link[1]]
                    while len(outer_socket_edges) > 0:
                        edge: EdgeItem = outer_socket_edges.pop()

                        sub_input.remove_edge(edge)
                        grp_input.add_edge(edge)
                        edge.end_pin = grp_input

                        sub_input.update_all()
                        grp_input.update_all()
                        edge.sort_pins()

            for sub_output in sub_node.outputs:
                connected_edges: list[EdgeItem] = sub_output.edges
                outer_socket_edges: list[EdgeItem] = [
                    edge for edge in connected_edges if edge not in grp_node.sub_scene.edges
                ]
                if len(outer_socket_edges) > 0:
                    grp_output: SocketItemRev = grp_node.outputs[sub_output.link[1]]
                    while len(outer_socket_edges) > 0:
                        edge: EdgeItem = outer_socket_edges.pop()

                        sub_output.remove_edge(edge)
                        grp_output.add_edge(edge)
                        edge.start_pin = grp_output

                        sub_output.update_all()
                        grp_output.update_all()
                        edge.sort_pins()

        return grp_node

    def resolve_sub_scene(self, grp_node: NodeItemRev):
        sub_scene_bbox: QtCore.QRectF = grp_node.sub_scene.itemsBoundingRect()
        sub_scene_center: QtCore.QPointF = QtCore.QPointF(
            sub_scene_bbox.x() + sub_scene_bbox.width() / 2,
            sub_scene_bbox.y() + sub_scene_bbox.height() / 2
        )

        for sub_node in grp_node.sub_scene.nodes:
            self.add_node(sub_node)
            sub_node_pos: QtCore.QPointF = QtCore.QPointF(
                sub_node.x() + (grp_node.center().x() - sub_scene_center.x()),
                sub_node.y() + (grp_node.center().y() - sub_scene_center.y())
            )
            sub_node.setPos(sub_node_pos)
            sub_node.last_position = sub_node_pos

            for socket in sub_node.inputs + sub_node.outputs:
                if socket.prop_model.properties["Name"].endswith(" ^"):
                    socket.prop_model.properties["Name"] = socket.prop_model.properties["Name"][0:-2]
                socket.prop_model.properties["link"] = ("", -1)

        for sub_edge in grp_node.sub_scene.edges:
            self.add_edge(sub_edge)

        for sub_frame in grp_node.sub_scene.frames:
            self.add_frame(sub_frame)

        for grp_input in grp_node.inputs:
            link: tuple[str, int] = grp_input.link
            sub_node: NodeItemRev = self.dag_item(link[0])
            sub_socket: SocketItemRev = sub_node.inputs[link[1]]

            while len(grp_input.edges) > 0:
                edge: EdgeItem = grp_input.edges.pop()
                sub_socket.add_edge(edge)
                edge.end_pin = sub_socket
                sub_socket.update_all()

        for grp_output in grp_node.outputs:
            link: tuple[str, int] = grp_output.link
            sub_node: NodeItemRev = self.dag_item(link[0])
            sub_socket: SocketItemRev = sub_node.inputs[link[1]]

            while len(grp_output.edges) > 0:
                edge: EdgeItem = grp_output.edges.pop()
                sub_socket.add_edge(edge)
                edge.start_pin = sub_socket
                sub_socket.update_all()

        grp_node.sub_scene.frames = []
        grp_node.sub_scene.edges = []
        grp_node.sub_scene.nodes = []
        self.remove_node(grp_node)

    def remove_node(self, node: NodeItemRev) -> None:
        if node.has_sub_scene():
            for sub_node in node.sub_scene.nodes:
                sub_node.on_remove()
        node.on_remove()

        # noinspection PyTypeChecker
        node.content_widget.setParent(None)
        self.removeItem(node)
        self._nodes.remove(node)

    def add_edge(self, edge: EdgeItem) -> EdgeItem:
        if edge.uuid == "":
            edge.uuid = QtCore.QUuid.createUuid().toString()

        if isinstance(edge.start_pin, SocketItemRev):
            edge.start_pin.add_edge(edge)
            edge.start_pin.socket_widget.update_stylesheets()

        if isinstance(edge.end_pin, SocketItemRev):
            edge.end_pin.add_edge(edge)
            edge.end_pin.socket_widget.update_stylesheets()

        self._edges.append(edge)
        self.addItem(edge)

        return edge

    def add_edge_from_pins(self, start: SocketItemRev,
                           end: Union[QtWidgets.QGraphicsItem, SocketItemRev]) -> EdgeItem:
        edge_color: QtGui.QColor = start.color
        edge: EdgeItem = EdgeItem(color=edge_color)
        edge.uuid = QtCore.QUuid.createUuid().toString()

        edge.start_pin = start
        edge.start_pin.add_edge(edge)

        edge.end_pin = end
        if isinstance(end, SocketItemRev):
            edge.end_pin.add_edge(edge)
            end.update_stylesheet()

        self._edges.append(edge)
        self.addItem(edge)

        return edge

    def remove_edge(self, edge: EdgeItem) -> None:
        if isinstance(edge.start_pin, SocketItemRev) and len(edge.start_pin.edges) > 0:
            if edge in edge.start_pin.edges:
                edge.start_pin.remove_edge(edge)
                edge.start_pin.update_stylesheet()

        if isinstance(edge.end_pin, SocketItemRev) and len(edge.end_pin.edges) > 0:
            if edge in edge.end_pin.edges:
                edge.end_pin.remove_edge(edge)
                edge.end_pin.update_stylesheet()

        self.removeItem(edge)
        self._edges.remove(edge)

    def remove_item(self, uuid: str) -> Union[NodeItemRev, EdgeItem, FrameItem, None]:
        item: Union[NodeItem, EdgeItem, FrameItem] = self.dag_item(uuid)

        if isinstance(item, NodeItemRev):
            self.remove_node(item)
        elif type(item) == EdgeItem:
            self.remove_edge(item)
        else:
            self.remove_frame(item)

        return item

    def selection_to_clipboard(self):
        # Copy states of selected and linked items
        selected_nodes: list[NodeItemRev] = self.selected_nodes()
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

    def selected_nodes(self) -> list[NodeItemRev]:
        return [item for item in self.selectedItems() if isinstance(item, NodeItem)]

    def selected_edges(self) -> list[EdgeItem]:
        return [item for item in self.selectedItems() if isinstance(item, EdgeItem)]

    def selected_frames(self) -> list[FrameItem]:
        return [item for item in self.selectedItems() if isinstance(item, FrameItem)]

    @staticmethod
    def bounding_rect(nodes: list[NodeItemRev], offset: int = 0) -> QtCore.QRectF:
        if len(nodes) > 0:
            x_min: float = min([node.x() for node in nodes]) - offset
            x_max: float = max([node.x() + node.boundingRect().width() for node in nodes]) + offset
            y_min: float = min([node.y() for node in nodes]) - offset
            y_max: float = max([node.y() + node.boundingRect().height() for node in nodes]) + offset
            return QtCore.QRectF(x_min, y_min, x_max - x_min, y_max - y_min)
        else:
            return QtCore.QRectF(-offset, -offset, offset, offset)

    @staticmethod
    def outside_frames(nodes: list[NodeItemRev]) -> list[FrameItem]:
        inside_frames: set[FrameItem] = set()
        all_frames: set[FrameItem] = {node.parent_frame for node in nodes if node.parent_frame is not None}

        for frame in all_frames:
            if set(frame.framed_nodes).issubset(nodes):
                inside_frames.add(frame)

        return list(all_frames.difference(inside_frames))

    def grp_interfaces(self, nodes: list[NodeItemRev]) -> set[NodeItem]:
        result: set[NodeItemRev] = set()
        for node in nodes:
            if node.has_sub_scene():
                if node.has_in_edges():
                    pre_pres: list[list[NodeItemRev]] = [pre.predecessors() for pre in node.successors()]
                    flat_pre_pres: list[NodeItemRev] = [node for sub_list in pre_pres for node in sub_list]
                    if set(flat_pre_pres).issubset(set(self._nodes).difference(set(nodes))):
                        result.add(node)

                if node.has_out_edges():
                    suc_succs: list[list[NodeItemRev]] = [suc.successors() for suc in node.predecessors()]
                    flat_suc_succs: list[NodeItemRev] = [node for sub_list in suc_succs for node in sub_list]
                    if set(flat_suc_succs).issubset(set(self._nodes).difference(set(nodes))):
                        result.add(node)
            else:
                if node.has_in_edges() and set(node.predecessors()).issubset(set(self._nodes).difference(set(nodes))):
                    result.add(node)
                if node.has_out_edges() and set(node.successors()).issubset(set(self._nodes).difference(set(nodes))):
                    result.add(node)

        return result

    def ends(self) -> list[NodeItemRev]:
        result: list[NodeItemRev] = []
        for node in self._nodes:
            if not node.has_out_edges():
                result.append(node)
        return result

    def to_dsk(self, visited_node: NodeItemRev, graph_dict: dict) -> dict:
        for node in visited_node.predecessors():
            self.to_dsk(node, graph_dict)

        task_inputs: list = []
        for socket in visited_node.inputs:
            task_inputs.append(socket.input_data())

        for idx, socket in enumerate(visited_node.outputs):
            graph_dict[socket] = (visited_node.evals[idx], *task_inputs)

        return graph_dict

    def to_nx(self) -> nx.DiGraph:
        nx_graph: nx.DiGraph = nx.DiGraph()
        for edge in self._edges:
            nx_graph.add_edge(edge.start_pin.parent_node, edge.end_pin.parent_node)
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
            node: NodeItemRev = self._nodes[-1]
            self.remove_node(node)

        self.clear()
        self.update()

    def serialize_nodes(self) -> list[dict]:
        nodes_dict: list[dict] = []

        for node in self._nodes:
            nodes_dict.append(node.__getstate__())

        return nodes_dict

    def deserialize_nodes(self, nodes_dict: list[dict]) -> list[NodeItemRev]:
        deserialized_nodes: list[NodeItemRev] = []

        for node_dict in nodes_dict:

            # Create node from dict
            node_class: type = getattr(sys.modules[__name__], node_dict["Class"])
            new_node: node_class = node_class(self._undo_stack)
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
            start_node: NodeItemRev = self.dag_item(edge_dict["Start Node UUID"])
            start_socket: SocketItemRev = start_node.outputs[edge_dict["Start Socket Idx"]]

            end_node: NodeItemRev = self.dag_item(edge_dict["End Node UUID"])
            end_socket: SocketItemRev = end_node.inputs[edge_dict["End Socket Idx"]]

            new_edge: EdgeItem = self.add_edge_from_pins(start_socket, end_socket)

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
            framed_nodes: list[NodeItemRev] = [self.dag_item(uuid) for uuid in framed_nodes_uuid]
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

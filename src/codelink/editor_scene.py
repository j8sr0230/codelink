from typing import Optional, Union
import importlib
import math

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

import networkx as nx

from frame_item import FrameItem
from node_item import NodeItem
from socket_widget import SocketWidget
from pin_item import PinItem
from edge_item import EdgeItem


class EditorScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent: Optional[QtCore.QObject] = None):
        super().__init__(QtCore.QRectF(0, 0, 64000, 64000), parent)

        self._nodes: list[NodeItem] = []
        self._edges: list[EdgeItem] = []
        self._frames: list[FrameItem] = []

        self._parent_custom_node: Optional[NodeItem] = None

        self._grid_spacing: int = 50
        self._background_color: QtGui.QColor = QtGui.QColor("#1D1D1D")
        self._grid_color: QtGui.QColor = QtGui.QColor("#282828")
        self._grid_pen: QtGui.QPen = QtGui.QPen(self._grid_color)
        self._grid_pen.setWidth(5)

        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
        self.setSortCacheEnabled(True)

    @property
    def nodes(self) -> list[NodeItem]:
        return self._nodes

    @nodes.setter
    def nodes(self, value: list[NodeItem]) -> None:
        self._nodes: list[NodeItem] = value

    @property
    def edges(self) -> list[EdgeItem]:
        return self._edges

    @property
    def frames(self) -> list[FrameItem]:
        return self._frames

    @edges.setter
    def edges(self, value: list[EdgeItem]) -> None:
        self._edges: list[EdgeItem] = value

    @property
    def parent_custom_node(self) -> Optional[NodeItem]:
        return self._parent_custom_node

    @parent_custom_node.setter
    def parent_custom_node(self, value: Optional[NodeItem]) -> None:
        self._parent_custom_node: Optional[NodeItem] = value

    # --- Scene manipulation ---

    def add_node(self, node: NodeItem) -> None:
        self._nodes.append(node)
        self.addItem(node)

    def remove_node(self, node: NodeItem) -> None:
        node.remove_from_frame()

        for socket_widget in node.socket_widgets:
            while len(socket_widget.pin.edges) > 0:
                edge: EdgeItem = socket_widget.pin.edges.pop()
                self.remove_edge(edge)

        # noinspection PyTypeChecker
        node.content_widget.setParent(None)
        self.removeItem(node)
        self._nodes.remove(node)

    def add_edge(self, edge: EdgeItem) -> EdgeItem:
        self._edges.append(edge)
        self.addItem(edge)
        return edge

    def add_edge_from_pins(self, start_pin: PinItem, end_pin: Union[QtWidgets.QGraphicsItem, PinItem]) -> EdgeItem:
        edge_color: QtGui.QColor = start_pin.color
        edge: EdgeItem = EdgeItem(color=edge_color)

        edge.start_pin = start_pin
        edge.start_pin.add_edge(edge)

        edge.end_pin = end_pin
        if type(end_pin) == PinItem:
            edge.end_pin.add_edge(edge)
            end_pin.socket_widget.update_stylesheets()

        edge.update()

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

    def resolve_custom_node(self, custom_node: NodeItem):
        if len(custom_node.sub_scene.nodes) > 0:
            sub_scene_bbox: QtCore.QRectF = custom_node.sub_scene.itemsBoundingRect()
            sub_scene_center: QtCore.QPointF = QtCore.QPointF(
                sub_scene_bbox.x() + sub_scene_bbox.width() / 2,
                sub_scene_bbox.y() + sub_scene_bbox.height() / 2
            )

            unzipped_nodes: list[NodeItem] = []
            for idx, node in enumerate(custom_node.sub_scene.nodes):
                self.add_node(node)
                node_pos: QtCore.QPointF = QtCore.QPointF(
                    node.x() + (custom_node.center.x() - sub_scene_center.x()),
                    node.y() + (custom_node.center.y() - sub_scene_center.y())
                )
                node.setPos(node_pos)
                unzipped_nodes.append(node)

            for edge in custom_node.sub_scene.edges:
                self.add_edge(edge)

            for frame in custom_node.sub_scene.frames:
                new_frame: FrameItem = self.add_frame_from_nodes(frame.framed_nodes)
                new_frame.__setstate__(frame.__getstate__())

            for socket_idx, socket_widget in enumerate(custom_node.socket_widgets):
                while len(socket_widget.pin.edges) > 0:
                    edge: EdgeItem = socket_widget.pin.edges.pop()
                    if str(socket_idx) in custom_node.pin_map.keys():
                        target_node: NodeItem = unzipped_nodes[
                            custom_node.pin_map[str(socket_idx)][0]
                        ]
                        target_socket: SocketWidget = target_node.socket_widgets[
                            custom_node.pin_map[str(socket_idx)][1]
                        ]

                        target_socket.pin.add_edge(edge)

                        if target_socket.is_input:
                            edge.end_pin = target_socket.pin
                        else:
                            edge.start_pin = target_socket.pin

                        edge.sort_pins()
                        target_socket.update_all()
                        target_socket.update()

            # if custom_node.parent_frame is not None and all([node.parent_frame is None for node in unzipped_nodes]):
            #     for node in unzipped_nodes:
            #         node.parent_frame = custom_node.parent_frame
            #         node.parent_frame.framed_nodes.append(node)

            self.remove_node(custom_node)

    def add_frame(self, frame_item: FrameItem) -> None:
        self._frames.append(frame_item)
        self.addItem(frame_item)

    def add_frame_from_nodes(self, nodes: list[NodeItem]) -> FrameItem:
        frame_item: FrameItem = FrameItem(framed_nodes=nodes)
        for node in nodes:
            node.parent_frame = frame_item

        self._frames.append(frame_item)
        self.addItem(frame_item)
        self.clearSelection()

        return frame_item

    def remove_frame(self, frame_item: FrameItem) -> None:
        for node in frame_item.framed_nodes:
            node.parent_frame = None

        self.removeItem(frame_item)
        self._frames.remove(frame_item)

    # --- Digraph analytics ---

    def graph_ends(self) -> list[NodeItem]:
        result: list[NodeItem] = []
        for node in self._nodes:
            if not node.has_out_edges():
                result.append(node)
        return result

    def graph_to_dsk(self, visited_node: NodeItem, graph_dict: dict) -> dict:
        for node in visited_node.predecessors():
            self.graph_to_dsk(node, graph_dict)

        task_inputs: list = []
        for socket_widget in visited_node.input_socket_widgets:
            if socket_widget.is_input:
                task_inputs.append(socket_widget.input_data())

        for idx, socket_widget in enumerate(visited_node.output_socket_widgets):
            if not socket_widget.is_input:
                graph_dict[socket_widget.pin] = (visited_node.evals[idx], *task_inputs)

        return graph_dict

    def graph_to_nx(self) -> nx.DiGraph:
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

    def is_graph_cyclic(self) -> bool:
        nx_graph: nx.DiGraph = self.graph_to_nx()
        result: bool = True
        try:
            nx.find_cycle(nx_graph)
        except nx.exception.NetworkXNoCycle:
            result: bool = False
        return result

    # --- Background and serialization ---

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)

        self.setBackgroundBrush(self._background_color)

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

    def serialize_nodes(self) -> list[dict]:
        nodes_dict: list[dict] = []

        for node in self._nodes:
            nodes_dict.append(node.__getstate__())

        return nodes_dict

    def deserialize_nodes(self, nodes_dict: list[dict]) -> None:
        for node_dict in nodes_dict:
            # Create node from dict
            node_props: dict = node_dict["Properties"]
            node_class = getattr(importlib.import_module("node_item"), node_props["Class"])
            new_node: node_class = node_class()
            self.add_node(new_node)

            # Reset node state
            new_node.__setstate__(node_dict)
            new_node.update()
            self.update()

    def serialize_edges(self) -> list[dict]:
        edges_dict: list[dict] = []

        for edge in self._edges:
            edges_dict.append(edge.__getstate__())

        return edges_dict

    def deserialize_edges(self, edges_dict: list[dict]):
        for edge_dict in edges_dict:
            start_node: NodeItem = self._nodes[edge_dict["Start Node Idx"]]
            start_socket_widget: SocketWidget = start_node.socket_widgets[edge_dict["Start Socket Idx"]]
            start_pin: PinItem = start_socket_widget.pin

            end_node: NodeItem = self._nodes[edge_dict["End Node Idx"]]
            end_socket_widget: SocketWidget = end_node.socket_widgets[edge_dict["End Socket Idx"]]
            end_pin: PinItem = end_socket_widget.pin

            self.add_edge_from_pins(start_pin, end_pin)
            start_socket_widget.update_all()
            end_socket_widget.update_all()
            self.update()

    def serialize_frames(self) -> list[dict]:
        frames_dict: list[dict] = []

        for frame in self._frames:
            frames_dict.append(frame.__getstate__())

        return frames_dict

    def deserialize_frames(self, frames_dict: list[dict]) -> None:
        for frame_dict in frames_dict:
            framed_nodes_idx: list[int] = frame_dict["Framed Nodes"]
            framed_nodes: list[NodeItem] = [self._nodes[idx] for idx in framed_nodes_idx]
            new_frame: FrameItem = self.add_frame_from_nodes(framed_nodes)

            # Reset node state
            new_frame.__setstate__(frame_dict)
            self.update()

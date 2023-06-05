from typing import Optional
import math
import importlib

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

import networkx as nx

from node_item import NodeItem
from socket_widget import SocketWidget
from pin_item import PinItem
from edge_item import EdgeItem


class EditorScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent: Optional[QtCore.QObject] = None):
        super().__init__(QtCore.QRectF(0, 0, 64000, 64000), parent)

        self._nodes: list[NodeItem] = []
        self._edges: list[EdgeItem] = []

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

    @edges.setter
    def edges(self, value: list[EdgeItem]) -> None:
        self._edges: list[EdgeItem] = value

    # --- Scene manipulation ---

    def add_node(self, node: NodeItem) -> None:
        self._nodes.append(node)
        self.addItem(node)

    def remove_node(self, node: NodeItem) -> None:
        # noinspection PyTypeChecker
        node.content_widget.setParent(None)
        self.removeItem(node)
        self._nodes.remove(node)

    def add_edge(self, start_pin: PinItem, end_pin: QtWidgets.QGraphicsItem) -> EdgeItem:
        edge_color: QtGui.QColor = start_pin.color
        edge: EdgeItem = EdgeItem(color=edge_color)

        edge.start_pin = start_pin
        edge.start_pin.add_edge(edge)

        edge.end_pin = end_pin
        if type(end_pin) == PinItem:
            edge.end_pin.add_edge(edge)

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
            nx_graph.add_edge(
                edge.start_pin.parent_node,
                edge.end_pin.parent_node
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
            NodeClass = getattr(importlib.import_module("node_item"), node_props["Class"])
            new_node: NodeClass = NodeClass()
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

            self.add_edge(start_pin, end_pin)
            start_socket_widget.update_all()
            end_socket_widget.update_all()
            self.update()

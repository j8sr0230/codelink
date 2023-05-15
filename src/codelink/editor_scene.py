from typing import Optional
import math
import importlib

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from node_item import NodeItem
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

    @property
    def nodes(self) -> list[NodeItem]:
        return self._nodes

    @nodes.setter
    def nodes(self, value: list[NodeItem]) -> None:
        self._nodes: list[NodeItem] = value

    def add_node(self, node: NodeItem) -> None:
        self._nodes.append(node)
        self.addItem(node)

    def remove_node(self, node: NodeItem) -> None:
        self._nodes.remove(node)
        self.removeItem(node)

    def add_edge(self, edge: EdgeItem) -> None:
        self._edges.append(edge)
        self.addItem(edge)

    def remove_edge(self, edge: EdgeItem) -> None:
        self._edges.remove(edge)
        self.removeItem(edge)

    def graph_ends(self) -> list[NodeItem]:
        result: list[NodeItem] = []
        for node in self._nodes:
            if not node.has_out_edges():
                result.append(node)
        return result

    def _is_node_cyclic(self, visited_node: NodeItem) -> bool:
        visited_node.visited_count += 1

        if visited_node.visited_count > len(visited_node.successors()) + 1:
            return True

        temp_res: list[bool] = []
        for node in visited_node.predecessors():
            temp_res.append(self._is_node_cyclic(node))
        return any(temp_res)

    def is_node_cyclic(self, visited_node: NodeItem) -> bool:
        for node in self._nodes:
            node.visited_count = 0
        return self._is_node_cyclic(visited_node)

    def is_graph_cyclic(self) -> bool:
        temp_res: list[bool] = []
        for node in self._nodes:
            temp_res.append(self.is_node_cyclic(node))
        return any(temp_res)

    def graph_to_dict(self, visited_node: NodeItem, graph_dict: dict) -> dict:
        for node in visited_node.predecessors():
            self.graph_to_dict(node, graph_dict)

        task_inputs: list = []
        for socket_widget in visited_node.input_socket_widgets:
            if socket_widget.is_input:
                task_inputs.append(socket_widget.input_data())

        for idx, socket_widget in enumerate(visited_node.output_socket_widgets):
            if not socket_widget.is_input:
                graph_dict[socket_widget] = (visited_node.evals[idx], *task_inputs)

        return graph_dict

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
            nodes_dict.append(node.prop_model.__getstate__())

        return nodes_dict

    def deserialize_nodes(self, nodes_dict: list[dict]) -> None:
        for node_dict in nodes_dict:
            NodeClass = getattr(importlib.import_module("node_item"), node_dict["Class"])
            new_node: NodeClass = NodeClass()
            new_node.prop_model.properties = node_dict
            self.add_node(new_node)
            new_node.setPos(QtCore.QPointF(int(node_dict["X"]), int(node_dict["Y"])))

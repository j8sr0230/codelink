from typing import Optional, Any, Union, cast
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


class DAGScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent: Optional[QtCore.QObject] = None):
        super().__init__(QtCore.QRectF(0, 0, 64000, 64000), parent)

        # Scene items
        self._frames: list[FrameItem] = []
        self._nodes: list[NodeItem] = []
        self._edges: list[EdgeItem] = []

        # Reference to parent node, if scene is sub scene
        self._parent_node: Optional[NodeItem] = None

        # Background
        self._grid_spacing: int = 50

        # Assets
        self._background_color: QtGui.QColor = QtGui.QColor("#1D1D1D")
        self._grid_color: QtGui.QColor = QtGui.QColor("#282828")
        self._grid_pen: QtGui.QPen = QtGui.QPen(self._grid_color)
        self._grid_pen.setWidth(5)

        # Widget setup
        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
        self.setSortCacheEnabled(True)

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

    # --------------- DAG editing ---------------

    def add_frame(self, frame: FrameItem) -> FrameItem:
        if frame.uuid == "":
            frame.uuid = QtCore.QUuid.createUuid().toString()

        self._frames.append(frame)
        self.addItem(frame)
        return frame

    def add_frame_from_nodes(self, nodes: list[NodeItem]) -> FrameItem:
        frame: FrameItem = FrameItem(framed_nodes=nodes)
        frame.uuid = QtCore.QUuid.createUuid().toString()

        for node in nodes:
            node.parent_frame = frame

        self._frames.append(frame)
        self.addItem(frame)
        self.clearSelection()

        return frame

    def remove_frame(self, frame_item: FrameItem) -> None:
        for node in frame_item.framed_nodes:
            node.parent_frame = None

        self.removeItem(frame_item)
        self._frames.remove(frame_item)

    def add_node(self, node: NodeItem) -> NodeItem:
        if node.uuid == "":
            node.uuid = QtCore.QUuid.createUuid().toString()

        self._nodes.append(node)
        self.addItem(node)
        return node

    def add_node_from_nodes(self, nodes: list[NodeItem]) -> NodeItem:
        selected_edges: list[EdgeItem] = []
        for edge in self._edges:
            if edge.start_pin.parentItem() in nodes and edge.end_pin.parentItem() in nodes:
                selected_edges.append(edge)

        sub_frames: set[FrameItem] = {node.parent_frame for node in nodes if node.parent_frame is not None}
        inner_sub_frames: list[FrameItem] = []
        for sub_frame in sub_frames:
            framed_nodes_set: set[NodeItem] = set(sub_frame.framed_nodes)
            selected_nodes_set: set[NodeItem] = set(nodes)
            if framed_nodes_set.issubset(selected_nodes_set):
                inner_sub_frames.append(sub_frame)

        # Calculate selection center
        selection_rect: QtCore.QRectF = self.bounding_rect(nodes)
        selection_center_x: float = selection_rect.x() + selection_rect.width() / 2
        selection_center_y: float = selection_rect.y() + selection_rect.height() / 2

        sub_nodes_dict: list[dict] = [node.__getstate__() for node in nodes]
        sub_edges_dict: list[dict] = [sub_edge.__getstate__() for sub_edge in selected_edges]
        sub_frames_dict: list[dict] = [sub_frame.__getstate__() for sub_frame in inner_sub_frames]

        # Add custom node, remove predefined socket widgets and save sub graph
        custom_node: NodeItem = NodeItem()
        custom_node.sub_scene.parent_node = custom_node
        self.add_node(custom_node)
        custom_node.clear_socket_widgets()
        custom_node.sub_scene.deserialize_nodes(sub_nodes_dict)
        custom_node.sub_scene.deserialize_edges(sub_edges_dict)
        custom_node.sub_scene.deserialize_frames(sub_frames_dict)
        custom_node.prop_model.setData(
            custom_node.prop_model.index(0, 1, QtCore.QModelIndex()), "Custom Node", 2  # QtCore.Qt.EditRole
        )

        # Generate input and output widgets for custom node and reconnect edges
        for node_idx, node in enumerate(nodes):
            for socket_idx, socket_widget in enumerate(node.socket_widgets):
                connected_edges: list[EdgeItem] = socket_widget.pin.edges
                outer_socket_edges: list[EdgeItem] = [
                    edge for edge in connected_edges if edge not in selected_edges
                ]
                if len(outer_socket_edges) > 0:
                    new_socket_widget: SocketWidget = socket_widget.__copy__()
                    new_socket_widget.parent_node = custom_node
                    new_socket_widget.pin.setParentItem(custom_node)
                    new_socket_widget.link = (node.uuid, socket_idx)

                    linked_sub_node: NodeItem = custom_node.sub_scene.dag_item(socket_widget.parent_node.uuid)
                    linked_sub_socket_widget: SocketWidget = linked_sub_node.socket_widgets[socket_idx]
                    linked_sub_socket_widget.link = (custom_node.uuid, len(custom_node.socket_widgets))

                    custom_node.add_socket_widget(new_socket_widget, len(custom_node.socket_widgets))

                    while len(socket_widget.pin.edges) > 0:
                        edge: EdgeItem = socket_widget.pin.edges.pop()

                        if edge in outer_socket_edges:
                            new_socket_widget.pin.add_edge(edge)

                            if socket_widget.is_input:
                                edge.end_pin = custom_node.socket_widgets[custom_node.socket_widgets.index(
                                    new_socket_widget)].pin
                            else:
                                edge.start_pin = custom_node.socket_widgets[custom_node.socket_widgets.index(
                                    new_socket_widget)].pin

                            edge.sort_pins()

                    new_socket_widget.update_all()
                    new_socket_widget.update()

        custom_node.setPos(
            selection_center_x - custom_node.boundingRect().width() / 2,
            selection_center_y - custom_node.boundingRect().height() / 2
        )

        custom_node.sort_socket_widgets()
        custom_node.update_all()

        # Remove selected nodes with inner edges
        while len(nodes) > 0:
            node: NodeItem = nodes.pop()
            self.remove_node(node)

        return custom_node

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

    def resolve_node(self, node: NodeItem):
        if node.has_sub_scene():
            sub_scene_bbox: QtCore.QRectF = node.sub_scene.itemsBoundingRect()
            sub_scene_center: QtCore.QPointF = QtCore.QPointF(
                sub_scene_bbox.x() + sub_scene_bbox.width() / 2,
                sub_scene_bbox.y() + sub_scene_bbox.height() / 2
            )

            for frame in node.sub_scene.frames:
                self.add_frame(frame)

            for sub_node in node.sub_scene.nodes:
                self.add_node(sub_node)
                node_pos: QtCore.QPointF = QtCore.QPointF(
                    sub_node.x() + (node.center.x() - sub_scene_center.x()),
                    sub_node.y() + (node.center.y() - sub_scene_center.y())
                )
                sub_node.setPos(node_pos)

            for edge in node.sub_scene.edges:
                self.add_edge(edge)

            for socket_idx, socket_widget in enumerate(node.socket_widgets):
                while socket_widget.pin.has_edges():
                    edge: EdgeItem = socket_widget.pin.edges.pop()

                    target_node: NodeItem = self.dag_item(socket_widget.link[0])
                    target_socket: SocketWidget = target_node.socket_widgets[socket_widget.link[1]]
                    target_socket.link = ("", -1)
                    target_socket.pin.add_edge(edge)

                    if target_socket.is_input:
                        edge.end_pin = target_socket.pin
                    else:
                        edge.start_pin = target_socket.pin

                    edge.sort_pins()
                    target_socket.update_all()

            self.remove_node(node)

    def add_edge(self, edge: EdgeItem) -> EdgeItem:
        if edge.uuid == "":
            edge.uuid = QtCore.QUuid.createUuid().toString()

        edge.start_pin.add_edge(edge)
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

    # --------------- DAG analytics ---------------

    @staticmethod
    def bounding_rect(nodes: list[NodeItem], offset: int = 0) -> QtCore.QRectF:
        x_min: float = min([node.x() for node in nodes]) - offset
        x_max: float = max([node.x() + node.boundingRect().width() for node in nodes]) + offset
        y_min: float = min([node.y() for node in nodes]) - offset
        y_max: float = max([node.y() + node.boundingRect().height() for node in nodes]) + offset
        return QtCore.QRectF(x_min, y_min, x_max - x_min, y_max - y_min)

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

    def ends(self) -> list[NodeItem]:
        result: list[NodeItem] = []
        for node in self._nodes:
            if not node.has_out_edges():
                result.append(node)
        return result

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

    # --------------- Background ---------------

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

    def deserialize_nodes(self, nodes_dict: list[dict]) -> None:
        for node_dict in nodes_dict:
            # Create node from dict
            node_class = getattr(importlib.import_module("node_item"), node_dict["Class"])
            new_node: node_class = node_class()
            self.add_node(new_node)

            # Reset node state
            new_node.__setstate__(node_dict)
            self.update()

    def serialize_edges(self) -> list[dict]:
        edges_dict: list[dict] = []

        for edge in self._edges:
            edges_dict.append(edge.__getstate__())

        return edges_dict

    def deserialize_edges(self, edges_dict: list[dict]):
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
            self.update()

    def serialize_frames(self) -> list[dict]:
        frames_dict: list[dict] = []

        for frame in self._frames:
            frames_dict.append(frame.__getstate__())

        return frames_dict

    def deserialize_frames(self, frames_dict: list[dict]) -> None:
        for frame_dict in frames_dict:
            framed_nodes_uuid: list[str] = frame_dict["Framed Nodes UUID's"]
            framed_nodes: list[NodeItem] = [self.dag_item(uuid) for uuid in framed_nodes_uuid]
            new_frame: FrameItem = self.add_frame_from_nodes(framed_nodes)

            # Reset frame state
            new_frame.__setstate__(frame_dict)
            self.update()

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

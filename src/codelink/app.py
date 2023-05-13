import os
import sys
import math
import pickle
from typing import Optional, Any, Union

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from dask.threaded import get

from property_model import PropertyModel
from property_widget import PropertyView
from item_delegates import BooleanDelegate
from socket_item import SocketItem
from socket_widget import SocketWidget
from edge_item import EdgeItem
from cutter_item import CutterItem
from node_item import NodeItem


class NodeEditorScene(QtWidgets.QGraphicsScene):
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


class NodeEditorView(QtWidgets.QGraphicsView):
    def __init__(self, scene: QtWidgets.QGraphicsScene = None, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(scene, parent)

        self._lm_pressed: bool = False
        self._mm_pressed: bool = False
        self._rm_pressed: bool = False
        self._mode: str = ""

        self._last_pos: QtCore.QPoint = QtCore.QPoint()
        self._last_socket: Optional[SocketItem] = None
        self._last_node: Optional[NodeItem] = None
        self._temp_edge: Optional[EdgeItem] = None
        self._cutter: Optional[CutterItem] = None

        self._zoom_level: int = 10
        self._zoom_level_range: list = [5, 10]

        self.setStyleSheet("selection-background-color: black")
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)

        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing |
                            QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)

        self._layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self._layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.setLayout(self._layout)

        self._prop_view: PropertyView = PropertyView(self)
        self._prop_view.setItemDelegateForRow(3, BooleanDelegate(self._prop_view))
        self._prop_view.setMaximumWidth(250)
        self._layout.addWidget(self._prop_view)
        self._layout.setMargin(0)
        self._layout.setSpacing(0)

        self._prop_view.hide()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:

        self._last_pos: QtCore.QPointF = self.mapToScene(event.pos())

        if event.button() == QtCore.Qt.LeftButton and self._mode == "":
            super().mousePressEvent(event)

            self._lm_pressed: bool = True

            if type(self.itemAt(event.pos())) == SocketItem:
                self._last_socket: QtWidgets.QGraphicsItem = self.itemAt(event.pos())

                if (not self._last_socket.socket_widget.is_input or
                        (self._last_socket.socket_widget.is_input and not self._last_socket.has_edges())):
                    self._mode: str = "EDGE_ADD"
                    self._temp_edge: EdgeItem = EdgeItem(color=self._last_socket.color)
                    self._temp_edge.start_socket = self._last_socket

                    temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                    temp_target.setPen(QtGui.QPen(QtGui.QColor("black")))
                    temp_target.setBrush(self._last_socket.color)
                    temp_target.setPos(self._last_socket.parentItem().mapToScene(self._last_socket.center()))
                    temp_target.setZValue(-1)

                    self._temp_edge.end_socket = temp_target
                    self.scene().add_edge(self._temp_edge)

                if self._last_socket.socket_widget.is_input and self._last_socket.has_edges():
                    self._mode: str = "EDGE_EDIT"

                    self._temp_edge: EdgeItem = self._last_socket.edges[-1]
                    connected_sockets: list[QtWidgets.QGraphicsItem] = [
                        self._temp_edge.start_socket,
                        self._temp_edge.end_socket
                    ]
                    for socket in connected_sockets:
                        socket.remove_edge(self._temp_edge)

                    temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                    temp_target.setPen(QtGui.QPen(QtGui.QColor("black")))
                    temp_target.setBrush(self._last_socket.color)
                    temp_target.setPos(self._last_socket.parentItem().mapToScene(self._last_socket.center()))
                    temp_target.setZValue(-1)

                    self._temp_edge.end_socket = temp_target
                    self._mode = "EDGE_ADD"

        if event.button() == QtCore.Qt.MiddleButton and self._mode == "":
            super().mousePressEvent(event)

            self._mode: str = "SCENE_DRAG"
            self._mm_pressed: bool = True
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeAllCursor)

        if event.button() == QtCore.Qt.RightButton and self._mode == "":
            self._rm_pressed: bool = True
            if event.modifiers() == QtCore.Qt.ShiftModifier:
                self._mode: str = "EDGE_CUT"
                self._cutter: CutterItem = CutterItem(start=self._last_pos, end=self._last_pos)
                self.scene().addItem(self._cutter)
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
            else:
                super().mousePressEvent(event)

                if type(self.itemAt(event.pos())) == NodeItem:
                    self.scene().clearSelection()

                    self._last_node: NodeItem = self.itemAt(event.pos())
                    self._mode: str = "NODE_SELECTED"
                    self._last_node.setSelected(True)
                    self._prop_view.setModel(self._last_node.prop_model)
                    self._prop_view.show()
                else:
                    self._prop_view.hide()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)

        if self._mode == "EDGE_ADD":
            if type(self.itemAt(event.pos())) == SocketItem:
                snapping_pos: QtCore.QPointF = self.itemAt(event.pos()).parentItem().mapToScene(
                    self.itemAt(event.pos()).pos()
                )
                snap_x: float = snapping_pos.x() + self.itemAt(event.pos()).size / 2
                snap_y: float = snapping_pos.y() + self.itemAt(event.pos()).size / 2
                self._temp_edge.end_socket.setPos(snap_x, snap_y)
            else:
                self._temp_edge.end_socket.setPos(self.mapToScene(event.pos()))

        if self._mode == "SCENE_DRAG":
            current_pos: QtCore.QPoint = self.mapToScene(event.pos())
            pos_delta: QtCore.QPoint = current_pos - self._last_pos
            self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
            self.translate(pos_delta.x(), pos_delta.y())
            self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        if self._mode == "EDGE_CUT":
            current_pos: QtCore.QPoint = self.mapToScene(event.pos())
            self._cutter.end_point = current_pos

            selected_items: list[QtWidgets.QGraphicsItem] = self.scene().collidingItems(self._cutter)

            for item in selected_items:
                if type(item) is EdgeItem:
                    connected_sockets: list[QtWidgets.QGraphicsItem] = [
                        item.start_socket,
                        item.end_socket
                    ]
                    for socket in connected_sockets:
                        socket.remove_edge(item)
                        socket.socket_widget.update_stylesheets()

                    self.scene().remove_edge(item)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        if self._mode == "EDGE_ADD":
            if type(self.itemAt(event.pos())) == SocketItem:
                self._temp_edge.end_socket = self.itemAt(event.pos())

                # Validate edge here!
                socket_type_start: object = self._temp_edge.start_socket.socket_widget.socket_type
                socket_type_end: object = self._temp_edge.end_socket.socket_widget.socket_type
                if socket_type_start == socket_type_end:
                    if self._temp_edge.start_socket.parentItem() is self._temp_edge.end_socket.parentItem():
                        # Sockets of the same node
                        self.scene().remove_edge(self._temp_edge)

                    elif (self._temp_edge.start_socket.socket_widget.is_input and
                          self._temp_edge.end_socket.socket_widget.is_input):
                        # Input with input socket
                        self.scene().remove_edge(self._temp_edge)

                    elif (not self._temp_edge.start_socket.socket_widget.is_input and
                          not self._temp_edge.end_socket.socket_widget.is_input):
                        # Output with output socket
                        self.scene().remove_edge(self._temp_edge)

                    else:
                        # Maybe valid connection ...
                        self._temp_edge.start_socket.add_edge(self._temp_edge)
                        self._temp_edge.end_socket.add_edge(self._temp_edge)
                        self._temp_edge.sort_sockets()
                        self._temp_edge.end_socket.socket_widget.update_stylesheets()

                        if self.scene().is_graph_cyclic():
                            # ... if not cyclic graph
                            connected_sockets: list[QtWidgets.QGraphicsItem] = [
                                self._temp_edge.start_socket,
                                self._temp_edge.end_socket
                            ]
                            for socket in connected_sockets:
                                socket.remove_edge(self._temp_edge)
                                socket.socket_widget.update_stylesheets()

                            self.scene().remove_edge(self._temp_edge)
                else:
                    # Incompatible socket types
                    self.scene().remove_edge(self._temp_edge)
            else:
                # No target socket
                self.scene().remove_edge(self._temp_edge)

            self._last_socket.socket_widget.update_stylesheets()

            for node in self.scene().graph_ends():
                dsk: dict = self.scene().graph_to_dict(node, {})
                print(get(dsk, node.socket_widgets[-1]))

        if self._mode == "EDGE_CUT":
            self.scene().removeItem(self._cutter)

        self._lm_pressed: bool = False
        self._mm_pressed: bool = False
        self._rm_pressed: bool = False
        self._mode: str = ""
        QtWidgets.QApplication.restoreOverrideCursor()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        event.accept()

        self._last_pos = self.mapToScene(event.pos())

        if event.angleDelta().y() > 0:
            if self._zoom_level < self._zoom_level_range[1]:
                self._zoom_level += 1
                self.scale(1.25, 1.25)
        else:
            if self._zoom_level > self._zoom_level_range[0]:
                self._zoom_level -= 1
                self.scale(1 / 1.25, 1 / 1.25)

        # Hack: Fixes the scene drifting while zooming
        drifted_pos: QtCore.QPoint = self.mapToScene(event.pos())
        pos_delta: QtCore.QPoint = drifted_pos - self._last_pos
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.translate(pos_delta.x(), pos_delta.y())
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)


if __name__ == "__main__":
    # from app import PropertyModel, SocketItem, SocketWidget, EdgeItem, NodeItem, CutterItem, NodeEditorScene,
    # NodeEditorView
    #
    # if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
    #     sys.path.append(os.path.abspath(os.path.dirname(__file__)))

    QtCore.QDir.addSearchPath("icon", os.path.abspath(os.path.dirname(__file__)))

    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # app.setStyle(QtWidgets.QStyleFactory().create("Fusion"))

    node_editor_scene: NodeEditorScene = NodeEditorScene()
    node_editor_view: NodeEditorView = NodeEditorView()

    node_editor_view.setScene(node_editor_scene)
    node_editor_view.resize(1200, 600)
    node_editor_view.show()

    node_1 = NodeItem()
    node_1.setPos(QtCore.QPointF(31600, 31800))
    node_editor_scene.add_node(node_1)

    node_2 = NodeItem()
    node_2.setPos(QtCore.QPointF(32200, 32050))
    node_editor_scene.add_node(node_2)

    node_3 = NodeItem()
    node_3.setPos(QtCore.QPointF(31900, 32100))
    node_editor_scene.add_node(node_3)

    # file_path: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "my_graph.cl")
    # pickle.dump(node_1, open(file_path, "wb"))
    # node_1_copy: NodeItem = pickle.load(open(file_path, 'rb'))
    # node_editor_scene.add_node(node_1_copy)

    # Test NodesModel
    # nodes_model: NodesModel = NodesModel(nodes=[
    #     {"class_name": "BaseNode", "node_name": "Add", "node_color": "red", "node_collapsed": "False",
    #      "node_pos_x": "0", "node_pos_y": "0"},
    #     {"class_name": "BaseNode", "node_name": "Sub", "node_color": "green", "node_collapsed": "False",
    #      "node_pos_x": "10", "node_pos_y": "10"}
    # ])

    # file_path: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "nodes.pkl")
    # # pickle.dump(nodes_model.nodes, open(file_path, "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    # loaded_nodes_data: list[dict] = pickle.load(open(file_path, 'rb'))
    # loaded_model_model: NodesModel = NodesModel(nodes=loaded_nodes_data)
    #
    # loaded_model_model.dataChanged.connect(lambda top_left_idx, bottom_right_idx, roles:
    #                                        print(loaded_model_model.nodes[top_left_idx.row()]))
    # loaded_model_model.dataChanged.connect(lambda top_left_idx, bottom_right_idx, roles:
    #                                        pickle.dump(
    #                                            loaded_model_model.nodes, open(file_path, "wb"),
    #                                            protocol=pickle.HIGHEST_PROTOCOL)
    #                                        )
    #
    # nodes_view: QtWidgets.QTableView = QtWidgets.QTableView()
    # nodes_view.setModel(loaded_model_model)
    # nodes_view.show()

    sys.exit(app.exec_())

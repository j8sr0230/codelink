from typing import Optional
import json
import os

from dask.threaded import get

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_widget import PropertyWidget
from socket_item import SocketItem
from socket_widget import SocketWidget
from node_item import NodeItem
from edge_item import EdgeItem
from cutter_item import CutterItem


class EditorWidget(QtWidgets.QGraphicsView):
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
        self._layout.setMargin(0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)

        # Property scroller
        self._prop_scroller: QtWidgets.QScrollArea = QtWidgets.QScrollArea(self)
        self._prop_scroller.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._prop_scroller.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._prop_scroller.setFixedWidth(300)
        self._prop_scroller.hide()
        self._prop_scroller.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                padding: 0px;
                margin: 0px;
                border: none;
                border-radius: 0px;
            }
        """)

        self._layout.addWidget(self._prop_scroller)

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
                    temp_target.setPos(self._last_socket.parentItem().mapToScene(self._last_socket.center()))

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
                    temp_target.setPos(self._last_socket.parentItem().mapToScene(self._last_socket.center()))

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
                # Open node properties
                if type(self.itemAt(event.pos())) == NodeItem:
                    self.scene().clearSelection()
                    self._last_node: NodeItem = self.itemAt(event.pos())
                    self._last_node.setSelected(True)
                    prop_widget: PropertyWidget = PropertyWidget(
                        self._last_node,
                        width=self._prop_scroller.width(),
                        parent=self._prop_scroller
                    )
                    self._prop_scroller.setWidget(prop_widget)
                    self._prop_scroller.show()
                else:
                    self._prop_scroller.hide()

                super().mousePressEvent(event)

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

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        file_path: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "graph.json")

        if event.matches(QtGui.QKeySequence.Save):
            with open(file_path, "w", encoding="utf8") as json_file:
                json.dump(
                    {
                        "Nodes": self.scene().serialize_nodes(),
                        "Edges": self.scene().serialize_edges()
                    },
                    json_file,
                    indent=4)

        if event.matches(QtGui.QKeySequence.Open):
            self.scene().clear()
            self.scene().nodes: list[NodeItem] = []
            self._prop_scroller.hide()

            with open(file_path, "r", encoding="utf8") as json_file:
                data_dict: dict = json.load(json_file)

                self.scene().deserialize_nodes(data_dict["Nodes"])
                self.scene().deserialize_edges(data_dict["Edges"])

        if event.matches(QtGui.QKeySequence.AddTab):
            if type(self.scene().selectedItems()[0]) is NodeItem:
                selected_node_item: NodeItem = self.scene().selectedItems()[0]
                new_socket_widget: SocketWidget = SocketWidget(
                    label="N",
                    socket_type=int,
                    is_input=True,
                    parent_node=selected_node_item
                )
                selected_node_item.add_socket_widget(
                    new_socket_widget,
                    selected_node_item.socket_widgets.index(selected_node_item.input_socket_widgets[-1])+1
                )
                self._prop_scroller.hide()

        if event.matches(QtGui.QKeySequence.Cancel):
            if type(self.scene().selectedItems()[0]) is NodeItem:
                selected_node_item: NodeItem = self.scene().selectedItems()[0]

                if len(selected_node_item.input_socket_widgets) > 0:
                    selected_node_item.remove_socket_widget(
                        selected_node_item.socket_widgets.index(selected_node_item.input_socket_widgets[-1])
                    )
                    self._prop_scroller.hide()

        super().keyPressEvent(event)

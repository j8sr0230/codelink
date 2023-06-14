from typing import Optional
import json
import os
import importlib

from dask.threaded import get

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from item_delegates import StringDelegate
from editor_scene import EditorScene
from property_widget import PropertyWidget
from property_table import PropertyTable
from pin_item import PinItem
from socket_widget import SocketWidget
from node_item import NodeItem
from edge_item import EdgeItem
from cutter_item import CutterItem
from frame_item import FrameItem


class EditorWidget(QtWidgets.QGraphicsView):
    def __init__(self, scene: QtWidgets.QGraphicsScene = None, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(scene, parent)

        self._lm_pressed: bool = False
        self._mm_pressed: bool = False
        self._rm_pressed: bool = False
        self._mode: str = ""

        self._temp_scene: Optional[QtWidgets.QGraphicsScene] = None

        self._last_pos: QtCore.QPoint = QtCore.QPoint()
        self._last_pin: Optional[PinItem] = None
        self._last_node: Optional[NodeItem] = None
        self._temp_edge: Optional[EdgeItem] = None
        self._cutter: Optional[CutterItem] = None

        self._zoom_level: int = 10
        self._zoom_level_range: list = [5, 10]

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setRubberBandSelectionMode(QtCore.Qt.ContainsItemShape)
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
        self._layout.addWidget(self._prop_scroller)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self._last_pos: QtCore.QPointF = self.mapToScene(event.pos())

        if event.button() == QtCore.Qt.LeftButton and self._mode == "":
            super().mousePressEvent(event)

            self._lm_pressed: bool = True
            if type(self.itemAt(event.pos())) == NodeItem:
                pass

            if type(self.itemAt(event.pos())) == PinItem:
                self._last_pin: QtWidgets.QGraphicsItem = self.itemAt(event.pos())

                if (not self._last_pin.socket_widget.is_input or
                        (self._last_pin.socket_widget.is_input and not self._last_pin.has_edges())):
                    self._mode: str = "EDGE_ADD"

                    temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                    temp_target.setPos(self._last_pin.parentItem().mapToScene(self._last_pin.center()))
                    self._temp_edge = self.scene().add_edge_from_pins(self._last_pin, temp_target)

                if self._last_pin.socket_widget.is_input and self._last_pin.has_edges():
                    self._mode: str = "EDGE_EDIT"

                    self._temp_edge: EdgeItem = self._last_pin.edges[-1]
                    start_pin: PinItem = self._temp_edge.start_pin
                    temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                    temp_target.setPos(self._last_pin.parentItem().mapToScene(self._last_pin.center()))

                    self.scene().remove_edge(self._temp_edge)
                    self._temp_edge = self.scene().add_edge_from_pins(start_pin, temp_target)
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
                    prop_widget.focus_changed.connect(self.focus_prop_scoller)
                    self._prop_scroller.setWidget(prop_widget)
                    self._prop_scroller.show()

                elif type(self.itemAt(event.pos())) == FrameItem:
                    self.scene().clearSelection()
                    frame_item: FrameItem = self.itemAt(event.pos())
                    table_view: PropertyTable = PropertyTable()
                    table_view.setModel(frame_item.prop_model)
                    table_view.setItemDelegateForRow(1, StringDelegate(table_view))
                    table_view.setItemDelegateForRow(2, StringDelegate(table_view))
                    table_view.setFixedWidth(self._prop_scroller.width())
                    table_view.setFixedHeight(
                        table_view.model().rowCount() * table_view.rowHeight(0) +
                        table_view.horizontalHeader().height()
                    )
                    self._prop_scroller.setWidget(table_view)
                    self._prop_scroller.show()
                else:
                    self.scene().clearSelection()
                    self._prop_scroller.hide()

                super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)

        if self._mode == "EDGE_ADD":
            if type(self.itemAt(event.pos())) == PinItem:
                snapping_pos: QtCore.QPointF = self.itemAt(event.pos()).parentItem().mapToScene(
                    self.itemAt(event.pos()).pos()
                )
                snap_x: float = snapping_pos.x() + self.itemAt(event.pos()).size / 2
                snap_y: float = snapping_pos.y() + self.itemAt(event.pos()).size / 2
                self._temp_edge.end_pin.setPos(snap_x, snap_y)

                if self._temp_edge.is_valid(eval_target=self.itemAt(event.pos())):
                    self._temp_edge.color = self._temp_edge.start_pin.color
                else:
                    self._temp_edge.color = QtGui.QColor("red")
            else:
                self._temp_edge.color = self._temp_edge.start_pin.color
                self._temp_edge.end_pin.setPos(self.mapToScene(event.pos()))

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
                    self.scene().remove_edge(item)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        if self._mode == "EDGE_ADD":
            if type(self.itemAt(event.pos())) == PinItem:
                if self._temp_edge.is_valid(eval_target=self.itemAt(event.pos())):
                    self._temp_edge.end_pin = self.itemAt(event.pos())
                    self._temp_edge.end_pin.add_edge(self._temp_edge)
                    self._temp_edge.sort_pins()
                    self._temp_edge.end_pin.socket_widget.update_stylesheets()
                else:
                    self.scene().remove_edge(self._temp_edge)
            else:
                self.scene().remove_edge(self._temp_edge)

            for node in self.scene().graph_ends():
                dsk: dict = self.scene().graph_to_dsk(node, {})
                print(get(dsk, node.socket_widgets[-1].pin))

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
            while len(self.scene().edges) > 0:
                edge: EdgeItem = self.scene().edges[-1]
                self.scene().remove_edge(edge)

            while len(self.scene().nodes) > 0:
                node: NodeItem = self.scene().nodes[-1]
                self.scene().remove_node(node)

            self.scene().clear()
            self.scene().update()
            self._prop_scroller.hide()

            with open(file_path, "r", encoding="utf8") as json_file:
                data_dict: dict = json.load(json_file)

                self.scene().deserialize_nodes(data_dict["Nodes"])
                self.scene().deserialize_edges(data_dict["Edges"])

        if event.matches(QtGui.QKeySequence.AddTab):
            if self.scene().selectedItems() and len(self.scene().selectedItems()) > 0:
                if type(self.scene().selectedItems()[0]) is NodeItem:
                    selected_node_item: NodeItem = self.scene().selectedItems()[0]
                    new_socket_widget: SocketWidget = SocketWidget(
                        label="N",
                        is_input=True,
                        parent_node=selected_node_item
                    )

                    if len(selected_node_item.input_socket_widgets) > 0:
                        insert_idx: int = (
                                selected_node_item.socket_widgets.index(selected_node_item.input_socket_widgets[-1]) + 1
                        )
                    else:
                        insert_idx: int = 0

                    selected_node_item.add_socket_widget(new_socket_widget, insert_idx)
                    self._prop_scroller.hide()

        if event.matches(QtGui.QKeySequence.Cancel):
            if self.scene().selectedItems() and len(self.scene().selectedItems()) > 0:
                if type(self.scene().selectedItems()[0]) is NodeItem:
                    selected_node_item: NodeItem = self.scene().selectedItems()[0]

                    if len(selected_node_item.input_socket_widgets) > 0:
                        selected_node_item.remove_socket_widget(
                            selected_node_item.socket_widgets.index(selected_node_item.input_socket_widgets[-1])
                        )
                        self._prop_scroller.hide()

        if event.matches(QtGui.QKeySequence.Delete):
            for selected_item in self.scene().selectedItems():
                if type(selected_item) is NodeItem:
                    self.scene().remove_node(selected_item)

        if event.key() == QtCore.Qt.Key_A and event.modifiers() == QtCore.Qt.ShiftModifier:
            new_node = NodeItem()
            new_node.setPos(QtCore.QPointF(32000, 32000))
            self.scene().add_node(new_node)

        if event.key() == QtCore.Qt.Key_C and event.modifiers() == QtCore.Qt.ShiftModifier:
            # Serialize selected nodes and edges (sub graph)
            selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if type(item) == NodeItem]
            selected_edges: list[EdgeItem] = []
            for edge in self.scene().edges:
                if edge.start_pin.parentItem() in selected_nodes and edge.end_pin.parentItem() in selected_nodes:
                    selected_edges.append(edge)

            # Calculate selection center
            selection_rect: QtCore.QRectF = self.scene().selectionArea().boundingRect()
            selection_center_x: float = selection_rect.x() + selection_rect.width() / 2
            selection_center_y: float = selection_rect.y() + selection_rect.height() / 2

            sub_nodes_dict: list[dict] = []
            for node in selected_nodes:
                sub_nodes_dict.append(node.__getstate__())

            sub_edges_dict: list[dict] = []
            for edge in selected_edges:
                edge_dict_mod: dict = edge.__getstate__()

                # Reset subgraph indexing
                edge_dict_mod["Start Node Idx"] = selected_nodes.index(edge.start_pin.parentItem())
                edge_dict_mod["End Node Idx"] = selected_nodes.index(edge.end_pin.parentItem())

                sub_edges_dict.append(edge_dict_mod)

            # Add custom node, remove predefined socket widgets and save sub graph
            custom_node: NodeItem = NodeItem()
            custom_node.sub_scene.parent_custom_node = custom_node
            self.scene().add_node(custom_node)
            custom_node.clear_socket_widgets()
            custom_node.sub_scene.deserialize_nodes(sub_nodes_dict)
            custom_node.sub_scene.deserialize_edges(sub_edges_dict)
            custom_node.prop_model.setData(
                custom_node.prop_model.index(1, 1, QtCore.QModelIndex()), "Custom Node", QtCore.Qt.EditRole
            )

            # Generate input and output widgets for custom node and reconnect edges
            for node_idx, node in enumerate(selected_nodes):
                for socket_idx, socket_widget in enumerate(node.socket_widgets):
                    connected_edges: list[EdgeItem] = socket_widget.pin.edges
                    outer_socket_edges: list[EdgeItem] = [
                        edge for edge in connected_edges if edge not in selected_edges
                    ]
                    if len(outer_socket_edges) > 0:
                        new_socket_widget: SocketWidget = socket_widget.__copy__()
                        new_socket_widget.parent_node = custom_node
                        new_socket_widget.pin.setParentItem(custom_node)

                        custom_node.pin_map[str(len(custom_node.socket_widgets))] = [node_idx, socket_idx]
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

            # Remove selected nodes and inner edges
            while len(selected_edges) > 0:
                edge: EdgeItem = selected_edges.pop()
                self.scene().remove_edge(edge)

            while len(selected_nodes) > 0:
                node: NodeItem = selected_nodes.pop()
                self.scene().remove_node(node)

        if event.key() == QtCore.Qt.Key_D and event.modifiers() == QtCore.Qt.SHIFT:
            for selected_item in self.scene().selectedItems():
                if type(selected_item) is NodeItem:
                    self.scene().resolve_custom_node(selected_item)

        if event.key() == QtCore.Qt.Key_F:
            selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if type(item) == NodeItem]

            frame_item: FrameItem = FrameItem()
            self.scene().addItem(frame_item)
            frame_item.setZValue(-1)
            for node in selected_nodes:
                node.setParentItem(frame_item)

        super().keyPressEvent(event)

    @QtCore.Slot(QtWidgets.QTableView)
    def focus_prop_scoller(self, focus_target: QtWidgets.QTableView):
        x: int = focus_target.pos().x()
        y: int = focus_target.pos().y()
        self._prop_scroller.ensureVisible(x, y, xmargin=0, ymargin=200)

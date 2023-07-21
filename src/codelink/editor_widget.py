from typing import Optional, Any, cast
import importlib
import json
import os

from dask.threaded import get

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from undo_commands import (
    DeleteSelectedCommand, MoveSelectedCommand, AddItemCommand, NodeFromNodeCommand, ResolveNodeCommand,
    RemoveItemCommand, RerouteEdgeCommand, SwitchSceneDownCommand, SwitchSceneUpCommand
)
from item_delegates import StringDelegate
from property_widget import PropertyWidget
from property_table import PropertyTable
from frame_item import FrameItem
from node_item import NodeItem
from socket_widget import SocketWidget
from pin_item import PinItem
from edge_item import EdgeItem
from cutter_item import CutterItem


class EditorWidget(QtWidgets.QGraphicsView):
    zoom_level_changed: QtCore.Signal = QtCore.Signal(int)

    def __init__(self, undo_stack: QtWidgets.QUndoStack, clipboard: QtGui.QClipboard,
                 scene: QtWidgets.QGraphicsScene = None, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(scene, parent)

        # Non persistent data model
        self._undo_stack: QtWidgets.QUndoStack = undo_stack
        self._clipboard: QtGui.QClipboard = clipboard
        self._nodes_clipboard: list[dict] = []

        self._lm_pressed: bool = False
        self._mm_pressed: bool = False
        self._rm_pressed: bool = False
        self._mode: str = ""

        self._last_pos: QtCore.QPoint = QtCore.QPoint()
        self._last_pin: Optional[PinItem] = None
        self._last_node: Optional[NodeItem] = None
        self._temp_edge: Optional[EdgeItem] = None
        self._cutter: Optional[CutterItem] = None

        self._zoom_level: int = 10
        self._zoom_level_range: list = [5, 10]

        # Widget layout and setup
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setRubberBandSelectionMode(QtCore.Qt.ContainsItemShape)
        self.setAcceptDrops(True)

        self.setViewportUpdateMode(QtWidgets.QGraphicsView.NoViewportUpdate)
        self.setCacheMode(cast(QtWidgets.QGraphicsView.CacheMode, QtWidgets.QGraphicsView.CacheNone))
        self.setOptimizationFlags(QtWidgets.QGraphicsView.DontSavePainterState |
                                  QtWidgets.QGraphicsView.DontAdjustForAntialiasing)
        # self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing |
        #                     QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)

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

        # Actions
        self._delete_action: QtWidgets.QAction = QtWidgets.QAction("Delete", self)
        self._delete_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Delete))
        cast(QtCore.SignalInstance, self._delete_action.triggered).connect(self.delete_selected_node)
        self.addAction(self._delete_action)

        self._copy_action: QtWidgets.QAction = QtWidgets.QAction("Copy", self)
        self._copy_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Copy))
        cast(QtCore.SignalInstance, self._copy_action.triggered).connect(self.copy)
        self.addAction(self._copy_action)

        self._past_action: QtWidgets.QAction = QtWidgets.QAction("Paste", self)
        self._past_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Paste))
        cast(QtCore.SignalInstance, self._past_action.triggered).connect(self.paste)
        self.addAction(self._past_action)

        self._undo_action: QtWidgets.QAction = self._undo_stack.createUndoAction(self, "Undo")
        self._undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
        self.addAction(self._undo_action)

        self._redo_action: QtWidgets.QAction = self._undo_stack.createRedoAction(self, "Redo")
        self._redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
        self.addAction(self._redo_action)

        # Listeners
        cast(QtCore.SignalInstance, self.zoom_level_changed).connect(self.on_zoom_change)

    @property
    def zoom_level(self) -> int:
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, value: int) -> None:
        self._zoom_level: int = value

    # --------------- Overwrites ---------------

    def scene(self) -> Any:
        return super().scene()

    def setScene(self, scene: QtWidgets.QGraphicsScene) -> None:
        super().setScene(scene)
        self.scene().zoom_level: int = self._zoom_level

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self._last_pos: QtCore.QPointF = self.mapToScene(event.pos())

        if event.button() == QtCore.Qt.LeftButton:
            super().mousePressEvent(event)

            self._lm_pressed: bool = True

            if type(self.itemAt(event.pos())) == PinItem:
                self._last_pin: PinItem = self.itemAt(event.pos())

                if (not self._last_pin.socket_widget.is_input or
                        (self._last_pin.socket_widget.is_input and not self._last_pin.has_edges())):
                    self._mode: str = "EDGE_ADD"
                    # Forward or backward edge creation from output socket to input socket or visa verse

                    temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                    temp_target.setPos(self._last_pin.parentItem().mapToScene(self._last_pin.center()))
                    self._temp_edge = self.scene().add_edge_from_pins(self._last_pin, temp_target)

                elif self._last_pin.socket_widget.is_input and self._last_pin.has_edges():
                    self._mode: str = "EDGE_EDIT"
                    # Edge editing by unplugging an existing edge from an input socket

                    self._temp_edge: EdgeItem = self._last_pin.edges[-1]
                    temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                    temp_target.setPos(self._last_pin.parentItem().mapToScene(self._last_pin.center()))

                    self._temp_edge.end_pin.remove_edge(self._temp_edge)
                    self._temp_edge.end_pin.socket_widget.update_stylesheets()
                    self._temp_edge.end_pin = temp_target
                    self._mode = "EDGE_ADD"

        if event.button() == QtCore.Qt.MiddleButton:
            super().mousePressEvent(event)

            self._mode: str = "SCENE_DRAG"
            self._mm_pressed: bool = True
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeAllCursor)

        if event.button() == QtCore.Qt.RightButton:
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
                    cast(QtCore.SignalInstance, prop_widget.focus_changed).connect(self.focus_prop_scroller)
                    self._prop_scroller.setWidget(prop_widget)
                    self._prop_scroller.show()

                elif type(self.itemAt(event.pos())) == FrameItem:
                    self.scene().clearSelection()
                    frame_item: FrameItem = self.itemAt(event.pos())
                    table_view: PropertyTable = PropertyTable()
                    table_view.setModel(frame_item.prop_model)
                    table_view.setItemDelegateForRow(0, StringDelegate(table_view))
                    table_view.setItemDelegateForRow(1, StringDelegate(table_view))
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
                temp_pin: PinItem = self.itemAt(event.pos())
                snapping_pos: QtCore.QPointF = temp_pin.parentItem().mapToScene(
                    temp_pin.pos()
                )
                snap_x: float = snapping_pos.x() + self.itemAt(event.pos()).size / 2
                snap_y: float = snapping_pos.y() + self.itemAt(event.pos()).size / 2
                self._temp_edge.end_pin.setPos(snap_x, snap_y)

                if self._temp_edge.is_valid(eval_target=temp_pin):
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

        if event.button() == QtCore.Qt.LeftButton and self._mode not in ("EDGE_ADD", "EDGE_EDIT", "EDGE_CUT"):
            selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if type(item) == NodeItem]
            selected_nodes_moved: list[bool] = [node.moved for node in selected_nodes]

            if any(selected_nodes_moved):
                self._undo_stack.push(MoveSelectedCommand(self.scene()))
                for node in selected_nodes:
                    node.moved = False

        if self._mode == "EDGE_ADD":
            if type(self.itemAt(event.pos())) == PinItem:
                if self._temp_edge.is_valid(eval_target=self.itemAt(event.pos())):
                    self._temp_edge.end_pin = self.itemAt(event.pos())
                    self._temp_edge.end_pin.add_edge(self._temp_edge)
                    self._temp_edge.sort_pins()
                    self._temp_edge.end_pin.socket_widget.update_stylesheets()

                    if self._temp_edge.end_pin != self._last_pin and self._temp_edge.start_pin != self._last_pin:
                        # Edits edge by changing end pin
                        self._undo_stack.push(RerouteEdgeCommand(
                            self.scene(),
                            edge=self._temp_edge,
                            undo_pin=self._last_pin,
                            redo_pin=self._temp_edge.end_pin
                        ))
                    elif (self._temp_edge.end_pin == self._last_pin and self._temp_edge.start_pin != self._last_pin and
                          self._temp_edge.start_pin.socket_widget.is_input):
                        # Hack: Changing end pin to the same end pin is performed but ignored by the undone stack
                        cmd: RerouteEdgeCommand = RerouteEdgeCommand(
                            self.scene(),
                            edge=self._temp_edge,
                            undo_pin=self._last_pin,
                            redo_pin=self._temp_edge.end_pin
                        )
                        self._undo_stack.push(cmd)
                        cmd.setObsolete(True)
                        self._undo_stack.undo()

                    else:
                        # Default edge adding
                        self._undo_stack.push(AddItemCommand(self.scene(), self._temp_edge))
                else:
                    self._temp_edge.end_pin = self._last_pin
                    if self._temp_edge.end_pin != self._temp_edge.start_pin:
                        # Default invalid edge
                        self._temp_edge.color = self._temp_edge.start_pin.color
                        self._undo_stack.push(RemoveItemCommand(self.scene(), self._temp_edge))
                    else:
                        # Invalid edge with same start and end pin
                        self.scene().remove_edge(self._temp_edge)
            else:
                # If target is not a PinItem (mouse btn release in empty area)
                self._temp_edge.end_pin = self._last_pin
                if self._temp_edge.end_pin != self._temp_edge.start_pin:
                    self._undo_stack.push(RemoveItemCommand(self.scene(), self._temp_edge))
                else:
                    self.scene().remove_edge(self._temp_edge)

            # Evaluates open dag ends
            for node in self.scene().ends():
                dsk: dict = self.scene().to_dsk(node, {})
                print(get(dsk, node.socket_widgets[-1].pin))

        if self._mode == "EDGE_CUT":
            self.scene().removeItem(self._cutter)

        # Resets mouse button state, widget mode, and cursor
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

        if self._zoom_level < 8:
            self.setInteractive(False)
        else:
            self.setInteractive(True)

        cast(QtCore.SignalInstance, self.zoom_level_changed).emit(self._zoom_level)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        print("Context Menu")
        # context_menu: QtWidgets.QMenu = QtWidgets.QMenu(self)
        # context_menu.addAction(self._copy_action)
        # context_menu.exec_(event.globalPos())

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:

        if event.matches(QtGui.QKeySequence.Save):
            # Saves file
            file_path: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "graph.json")
            with open(file_path, "w", encoding="utf8") as json_file:
                json.dump(self.scene().serialize(), json_file, indent=4)

        if event.matches(QtGui.QKeySequence.Open):
            # Opens file
            self.scene().clear_scene()
            self._undo_stack.clear()
            self._prop_scroller.hide()

            file_path: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "graph.json")
            with open(file_path, "r", encoding="utf8") as json_file:
                data_dict: dict = json.load(json_file)
                self.scene().deserialize(data_dict)

            self.fit_in_content()

        if event.matches(QtGui.QKeySequence.AddTab):
            # Adds socket to node
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
            # Removes socket from node
            if self.scene().selectedItems() and len(self.scene().selectedItems()) > 0:
                if type(self.scene().selectedItems()[0]) is NodeItem:
                    selected_node_item: NodeItem = self.scene().selectedItems()[0]

                    if len(selected_node_item.input_socket_widgets) > 0:
                        selected_node_item.remove_socket_widget(
                            selected_node_item.socket_widgets.index(selected_node_item.input_socket_widgets[-1])
                        )
                        self._prop_scroller.hide()

                if type(self.scene().selectedItems()[0]) is FrameItem:
                    selected_frame: FrameItem = self.scene().selectedItems()[0]

                    self.scene().remove_frame(selected_frame)
                    self._prop_scroller.hide()

        if event.key() == QtCore.Qt.Key_S:
            # Prints undo stack
            for i in range(self._undo_stack.count()):
                print("Stack Item", self._undo_stack.command(i))

        if event.key() == QtCore.Qt.Key_A and event.modifiers() == QtCore.Qt.ShiftModifier:
            # Adds node to scene
            new_node = NodeItem(self._undo_stack)
            new_node.setPos(self.mapToScene(self.mapFromParent(QtGui.QCursor.pos())))
            self._undo_stack.push(AddItemCommand(self.scene(), new_node))

        if event.key() == QtCore.Qt.Key_C and event.modifiers() == QtCore.Qt.ShiftModifier:
            # Creates custom node from nodes
            selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if type(item) == NodeItem]
            self._undo_stack.push(NodeFromNodeCommand(self.scene(), selected_nodes))

        if event.key() == QtCore.Qt.Key_D and event.modifiers() == QtCore.Qt.SHIFT:
            # Resolves custom node
            self._undo_stack.push(ResolveNodeCommand(self.scene(), self.scene().selectedItems()))

        if event.key() == QtCore.Qt.Key_F:
            # Frames selected nodes
            selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if type(item) == NodeItem]
            for node in selected_nodes:
                node.remove_from_frame()

            frame: FrameItem = FrameItem(selected_nodes)
            self._undo_stack.push(AddItemCommand(self.scene(), frame))

        if event.key() == QtCore.Qt.Key_Q:
            # Opens sub scene of custom node
            selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if type(item) == NodeItem]

            if len(selected_nodes) > 0 and selected_nodes[0].has_sub_scene():
                self._undo_stack.push(SwitchSceneDownCommand(
                    self, selected_nodes[0].sub_scene, self.scene(), selected_nodes[0])
                )
                self.fit_in_content()

        if event.key() == QtCore.Qt.Key_W:
            # Steps out of sub scene
            if self.scene().parent_node:
                self._undo_stack.push(SwitchSceneUpCommand(self, self.scene().parent_node.scene(), self.scene()))
                self.fit_in_content()

        super().keyPressEvent(event)

    # --------------- Callbacks ---------------

    def delete_selected_node(self) -> None:
        self._undo_stack.push(DeleteSelectedCommand(self.scene()))

    def copy(self) -> None:
        selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if type(item) == NodeItem]
        node_dicts: list[dict] = []
        for node in selected_nodes:
            node_dicts.append(node.__getstate__())

        self._nodes_clipboard: list[dict] = node_dicts

    def paste(self) -> None:
        nodes: list[NodeItem] = []
        for node_state in self._nodes_clipboard:
            node_cls: type = getattr(importlib.import_module("node_item"), node_state["Class"])
            node: node_cls = node_cls(self._undo_stack)
            self._undo_stack.push(AddItemCommand(self.scene(), node))

            node.__setstate__(node_state)
            node.uuid = QtCore.QUuid.createUuid().toString()
            nodes.append(node)

        mouse_pos: QtCore.QPointF = self.mapToScene(self.mapFromParent(QtGui.QCursor.pos()))
        scene_bbox: QtCore.QRectF = self.scene().bounding_rect(nodes)
        scene_center: QtCore.QPointF = QtCore.QPointF(scene_bbox.x() + scene_bbox.width() / 2,
                                                      scene_bbox.y() + scene_bbox.height() / 2)
        dx: float = mouse_pos.x() - scene_center.x()
        dy: float = mouse_pos.y() - scene_center.y()
        for node in nodes:
            node.setPos(dx + self.scene().dag_item(node.uuid).x(), dy + self.scene().dag_item(node.uuid).y())

    def focus_prop_scroller(self, focus_target: QtWidgets.QTableView):
        x: int = focus_target.pos().x()
        y: int = focus_target.pos().y()
        self._prop_scroller.ensureVisible(x, y, xmargin=0, ymargin=200)

    def on_zoom_change(self, zoom_level: int) -> None:
        self.scene().update_details(zoom_level)

    def fit_in_content(self) -> None:
        top_left: QtCore.QPointF = self.mapToScene(self.sceneRect().x(), self.sceneRect().y())
        scene_bbox: QtCore.QRectF = self.scene().bounding_rect(self.scene().nodes)
        scene_center: QtCore.QPointF = QtCore.QPointF(scene_bbox.x() + scene_bbox.width() / 2,
                                                      scene_bbox.y() + scene_bbox.height() / 2)
        scale: float = self.transform().m11()
        dx: float = (top_left.x() - scene_center.x()) + ((1 / scale) * self.width() / 2)
        dy: float = (top_left.y() - scene_center.y()) + ((1 / scale) * self.height() / 2)

        self.setTransformationAnchor(self.NoAnchor)
        self.translate(dx, dy)
        self.setTransformationAnchor(self.AnchorUnderMouse)

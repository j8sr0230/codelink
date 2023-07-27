from typing import Union, Optional, Any, cast
import json
import os

from dask.threaded import get

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from undo_commands import (
    AddNodeCommand, NodeFromNodeCommand, ResolveNodeCommand,  # Node commands
    AddEdgeCommand, RerouteEdgeCommand, RemoveEdgeCommand,  # Edge commands
    AddFrameCommand,  # Frame commands
    DeleteSelectedCommand, MoveSelectedCommand,  # General item commands
    SwitchSceneDownCommand, SwitchSceneUpCommand, PasteClipboardCommand  # UI navigation commands
)
from node_reg import nodes_dict
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

    def __init__(self, undo_stack: QtWidgets.QUndoStack, scene: QtWidgets.QGraphicsScene = None,
                 parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(scene, parent)

        # Non persistent data model
        self._undo_stack: QtWidgets.QUndoStack = undo_stack

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
        self._scroll_border: int = 50

        # Widget layout and setup
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setRubberBandSelectionMode(QtCore.Qt.ContainsItemShape)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

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
        self._open_action: QtWidgets.QAction = QtWidgets.QAction("Open", self)
        self._open_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Open))
        cast(QtCore.SignalInstance, self._open_action.triggered).connect(self.open_from_file)
        self.addAction(self._open_action)

        self._save_action: QtWidgets.QAction = QtWidgets.QAction("Save As", self)
        self._save_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Save))
        cast(QtCore.SignalInstance, self._save_action.triggered).connect(self.save_to_file)
        self.addAction(self._save_action)

        self._undo_action: QtWidgets.QAction = self._undo_stack.createUndoAction(self, "Undo")
        self._undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
        self.addAction(self._undo_action)

        self._redo_action: QtWidgets.QAction = self._undo_stack.createRedoAction(self, "Redo")
        self._redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
        self.addAction(self._redo_action)

        self._fit_action: QtWidgets.QAction = QtWidgets.QAction("Fit Content", self)
        self._fit_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Find))
        cast(QtCore.SignalInstance, self._fit_action.triggered).connect(self.fit_min)
        self.addAction(self._fit_action)

        self._copy_action: QtWidgets.QAction = QtWidgets.QAction("Copy", self)
        self._copy_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Copy))
        cast(QtCore.SignalInstance, self._copy_action.triggered).connect(self.copy)
        self.addAction(self._copy_action)

        self._past_action: QtWidgets.QAction = QtWidgets.QAction("Paste", self)
        self._past_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Paste))
        cast(QtCore.SignalInstance, self._past_action.triggered).connect(self.paste)
        self.addAction(self._past_action)

        self._delete_action: QtWidgets.QAction = QtWidgets.QAction("Delete", self)
        self._delete_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Delete))
        cast(QtCore.SignalInstance, self._delete_action.triggered).connect(self.delete_selected_node)
        self.addAction(self._delete_action)

        self._create_frame_action: QtWidgets.QAction = QtWidgets.QAction("Create Frame", self)
        self._create_frame_action.setShortcut(QtGui.QKeySequence("Shift+F"))
        cast(QtCore.SignalInstance, self._create_frame_action.triggered).connect(self.create_frame)
        self.addAction(self._create_frame_action)

        self._create_custom_action: QtWidgets.QAction = QtWidgets.QAction("Create Custom", self)
        self._create_custom_action.setShortcut(QtGui.QKeySequence("Shift+C"))
        cast(QtCore.SignalInstance, self._create_custom_action.triggered).connect(self.create_custom_node)
        self.addAction(self._create_custom_action)

        self._resolve_custom_action: QtWidgets.QAction = QtWidgets.QAction("Resolve Custom", self)
        self._resolve_custom_action.setShortcut(QtGui.QKeySequence("Shift+D"))
        cast(QtCore.SignalInstance, self._resolve_custom_action.triggered).connect(self.resolve_custom_node)
        self.addAction(self._resolve_custom_action)

        self._open_sub_action: QtWidgets.QAction = QtWidgets.QAction("Open Sub Graph", self)
        self._open_sub_action.setShortcut(QtGui.QKeySequence("Shift+Q"))
        cast(QtCore.SignalInstance, self._open_sub_action.triggered).connect(self.open_sub_graph)
        self.addAction(self._open_sub_action)

        self._close_sub_action: QtWidgets.QAction = QtWidgets.QAction("Close Sub Graph", self)
        self._close_sub_action.setShortcut(QtGui.QKeySequence("Shift+W"))
        cast(QtCore.SignalInstance, self._close_sub_action.triggered).connect(self.close_sub_graph)
        self.addAction(self._close_sub_action)

        self._add_test_node_action: QtWidgets.QAction = QtWidgets.QAction("Test Node", self)
        self._add_test_node_action.setShortcut(QtGui.QKeySequence("Shift+A"))
        cast(QtCore.SignalInstance, self._add_test_node_action.triggered).connect(self.add_test_node)
        self.addAction(self._add_test_node_action)

        # Listeners
        cast(QtCore.SignalInstance, self.zoom_level_changed).connect(self.on_zoom_change)
        cast(QtCore.SignalInstance, self.customContextMenuRequested).connect(self.show_context_menu)

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

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            # Open node properties
            if isinstance(self.itemAt(event.pos()), NodeItem):
                # self.scene().clearSelection()
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
                # self.scene().clearSelection()
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

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self._last_pos: QtCore.QPointF = self.mapToScene(event.pos())

        if event.button() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.ShiftModifier:
            self._lm_pressed: bool = True
            self._mode: str = "EDGE_CUT"
            self._cutter: CutterItem = CutterItem(start=self._last_pos, end=self._last_pos)
            self.scene().addItem(self._cutter)
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        elif event.button() == QtCore.Qt.LeftButton and not event.modifiers() == QtCore.Qt.ShiftModifier:
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
            new_selection: Optional[Union[NodeItem, FrameItem]] = None  # Right click selected NodeItem od FrameItem
            if type(self.itemAt(event.pos())) == QtWidgets.QGraphicsTextItem:
                new_selection: NodeItem = self.itemAt(event.pos()).parentItem()
            elif isinstance(self.itemAt(event.pos()), NodeItem):
                new_selection: NodeItem = self.itemAt(event.pos())
            elif type(self.itemAt(event.pos())) == QtWidgets.QGraphicsProxyWidget:
                new_selection: NodeItem = self.itemAt(event.pos()).parentItem()
            elif type(self.itemAt(event.pos())) == FrameItem:
                new_selection: FrameItem = self.itemAt(event.pos())

            # Previously selected scene items
            selected_items: list[Any] = [item for item in self.scene().selectedItems() if
                                         (isinstance(item, NodeItem) or type(item) == FrameItem)]

            if new_selection is not None:
                if new_selection not in selected_items:
                    # If new_selection is new
                    self.scene().clearSelection()
                    new_selection.setSelected(True)
            else:
                self.scene().clearSelection()

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
                self.ensureVisible(self._temp_edge.end_pin, self._scroll_border, self._scroll_border)

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
                    self._undo_stack.push(RemoveEdgeCommand(self.scene(), item))

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        if event.button() == QtCore.Qt.LeftButton and self._mode not in ("EDGE_ADD", "EDGE_EDIT", "EDGE_CUT"):
            selected_nodes: list[NodeItem] = [
                item for item in self.scene().selectedItems() if isinstance(item, NodeItem)
            ]
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
                        self._undo_stack.push(AddEdgeCommand(self.scene(), self._temp_edge))
                else:
                    self._temp_edge.end_pin = self._last_pin
                    if self._temp_edge.end_pin != self._temp_edge.start_pin:
                        # Default invalid edge
                        self._temp_edge.color = self._temp_edge.start_pin.color
                        self._undo_stack.push(RemoveEdgeCommand(self.scene(), self._temp_edge))
                    else:
                        # Invalid edge with same start and end pin
                        self.scene().remove_edge(self._temp_edge)
            else:
                # If target is not a PinItem (mouse btn release in empty area)
                self._temp_edge.end_pin = self._last_pin
                if self._temp_edge.end_pin != self._temp_edge.start_pin:
                    self._undo_stack.push(RemoveEdgeCommand(self.scene(), self._temp_edge))
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

        # if self._zoom_level < 8:
        #     self.setInteractive(False)
        # else:
        #     self.setInteractive(True)

        cast(QtCore.SignalInstance, self.zoom_level_changed).emit(self._zoom_level)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:

        if event.key() == QtCore.Qt.Key_S:
            # Prints undo stack for debugging
            for i in range(self._undo_stack.count()):
                print("Stack Item", self._undo_stack.command(i))

        super().keyPressEvent(event)

    # --------------- Callbacks ---------------
    def show_context_menu(self, position: QtCore.QPoint):
        if self._mode != "EDGE_CUT":
            context_menu: QtWidgets.QMenu = QtWidgets.QMenu(self)

            # Add menu
            math_nodes: QtWidgets.QMenu = QtWidgets.QMenu(context_menu)
            math_nodes.setTitle("&Math")

            math_nodes.addAction(self._add_test_node_action)

            for name, cls, in nodes_dict.items():
                # Adds all nodes from nodes.nodes_dict
                add_node_action: QtWidgets.QAction = QtWidgets.QAction(name, self)
                add_node_action.setData(cls)
                cast(QtCore.SignalInstance, add_node_action.triggered).connect(
                    lambda: self.add_node_from_cls(add_node_action.data())
                )
                math_nodes.addAction(add_node_action)

            # Rest of context menu
            context_menu.addMenu(math_nodes)
            context_menu.addSeparator()

            context_menu.addAction(self._open_action)
            context_menu.addAction(self._save_action)
            context_menu.addAction(self._undo_action)
            context_menu.addAction(self._redo_action)
            context_menu.addAction(self._fit_action)
            context_menu.addSeparator()

            selected_items: list[Any] = self.scene().selectedItems()
            nodes_selected: bool = any(isinstance(item, NodeItem) for item in selected_items)
            frames_selected: bool = any(isinstance(item, FrameItem) for item in selected_items)

            if nodes_selected or frames_selected:
                self._delete_action.setEnabled(True)
            else:
                self._delete_action.setEnabled(False)
            context_menu.addAction(self._delete_action)

            if nodes_selected:
                self._create_frame_action.setEnabled(True)
                self._create_custom_action.setEnabled(True)
            else:
                self._create_frame_action.setEnabled(False)
                self._create_custom_action.setEnabled(False)
            context_menu.addAction(self._create_frame_action)
            context_menu.addAction(self._create_custom_action)

            if nodes_selected and [item for item in selected_items if isinstance(item, NodeItem)][0].has_sub_scene():
                self._open_sub_action.setEnabled(True)
                self._resolve_custom_action.setEnabled(True)
            else:
                self._open_sub_action.setEnabled(False)
                self._resolve_custom_action.setEnabled(False)
            context_menu.addAction(self._resolve_custom_action)
            context_menu.addAction(self._open_sub_action)

            if self.scene().parent_node is not None:
                self._close_sub_action.setEnabled(True)
            else:
                self._close_sub_action.setEnabled(False)
            context_menu.addAction(self._close_sub_action)

            context_menu.exec_(self.mapToGlobal(position))

            self._delete_action.setEnabled(True)
            self._create_frame_action.setEnabled(True)
            self._create_custom_action.setEnabled(True)
            self._resolve_custom_action.setEnabled(True)
            self._open_sub_action.setEnabled(True)
            self._close_sub_action.setEnabled(True)

    def focus_prop_scroller(self, focus_target: QtWidgets.QTableView):
        x: int = focus_target.pos().x()
        y: int = focus_target.pos().y()
        self._prop_scroller.ensureVisible(x, y, xmargin=0, ymargin=200)

    def zoom_min(self):
        while self._zoom_level > self._zoom_level_range[0]:
            self._zoom_level -= 1
            self.scale(1 / 1.25, 1 / 1.25)
        cast(QtCore.SignalInstance, self.zoom_level_changed).emit(self._zoom_level)

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

    def save_to_file(self):
        file_path: str = os.path.normpath(QtWidgets.QFileDialog.getSaveFileName(self)[0])
        # file_path: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "graph.json")

        if file_path != ".":
            with open(file_path, "w", encoding="utf8") as json_file:
                json.dump(self.scene().serialize(), json_file, indent=4)

    def open_from_file(self):
        file_path: str = os.path.normpath(QtWidgets.QFileDialog.getOpenFileName(self)[0])
        # file_path: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "graph.json")

        if file_path != ".":
            self.scene().clear_scene()
            self._undo_stack.clear()
            self._prop_scroller.hide()
            self.zoom_min()

            with open(file_path, "r", encoding="utf8") as json_file:
                data_dict: dict = json.load(json_file)
                self.scene().deserialize(data_dict)

            self.fit_in_content()

    def fit_min(self) -> None:
        self.zoom_min()
        self.fit_in_content()

    def copy(self) -> None:
        if len(self.scene().selectedItems()) > 0:
            self.scene().selection_to_clipboard()

    def paste(self) -> None:
        try:
            self._undo_stack.push(PasteClipboardCommand(self.scene()))
        except json.JSONDecodeError:
            print("Pasting failed!")

    def delete_selected_node(self) -> None:
        self._undo_stack.push(DeleteSelectedCommand(self.scene()))

    def create_custom_node(self):
        selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if isinstance(item, NodeItem)]
        self._undo_stack.push(NodeFromNodeCommand(self.scene(), selected_nodes))

    def resolve_custom_node(self):
        self._undo_stack.push(ResolveNodeCommand(self.scene(), self.scene().selectedItems()))

    def create_frame(self):
        selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if isinstance(item, NodeItem)]
        self._undo_stack.push(AddFrameCommand(self.scene(), selected_nodes))

    def open_sub_graph(self):
        selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if isinstance(item, NodeItem)]

        if len(selected_nodes) > 0 and selected_nodes[0].has_sub_scene():
            self._undo_stack.push(SwitchSceneDownCommand(
                self, selected_nodes[0].sub_scene, self.scene(), selected_nodes[0])
            )
            self.fit_in_content()

    def close_sub_graph(self):
        if self.scene().parent_node:
            self._undo_stack.push(SwitchSceneUpCommand(self, self.scene().parent_node.scene(), self.scene()))
            self.fit_in_content()

    def add_test_node(self):
        new_node = NodeItem(self._undo_stack)
        new_node.setPos(self.mapToScene(self.mapFromParent(QtGui.QCursor.pos())))
        self._undo_stack.push(AddNodeCommand(self.scene(), new_node))

    def add_node_from_cls(self, cls: type):
        new_node: cls = cls(self._undo_stack)
        new_node.setPos(self.mapToScene(self.mapFromParent(QtGui.QCursor.pos())))
        self._undo_stack.push(AddNodeCommand(self.scene(), new_node))

    def add_socket(self):
        if self.scene().selectedItems() and len(self.scene().selectedItems()) > 0:
            if isinstance(self.scene().selectedItems()[0], NodeItem):
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

    def remove_socket(self):
        if self.scene().selectedItems() and len(self.scene().selectedItems()) > 0:
            if isinstance(self.scene().selectedItems()[0], NodeItem):
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

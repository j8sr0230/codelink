from typing import Optional, Any, cast
import json
import os

from dask.threaded import get

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from item_delegates import StringDelegate
from property_widget import PropertyWidget
from property_table import PropertyTable
from pin_item import PinItem
from socket_widget import SocketWidget
from node_item import NodeItem
from edge_item import EdgeItem
from cutter_item import CutterItem
from frame_item import FrameItem
from undo_commands import (
    DeleteSelectedCommand, MoveSelectedCommand, AddItemCommand, CustomNodeCommand, RemoveItemCommand
)


class EditorWidget(QtWidgets.QGraphicsView):
    def __init__(self, scene: QtWidgets.QGraphicsScene = None, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(scene, parent)

        self._lm_pressed: bool = False
        self._mm_pressed: bool = False
        self._rm_pressed: bool = False
        self._mode: str = ""

        self._temp_scenes: list[QtWidgets.QGraphicsScene] = []

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

        # Actions
        self._delete_action: QtWidgets.QAction = QtWidgets.QAction("Delete", self)
        self._delete_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Delete))
        self._delete_action.triggered.connect(self.delete_selected_node)
        self.addAction(self._delete_action)

        self._copy_action: QtWidgets.QAction = QtWidgets.QAction("Copy", self)
        self._copy_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Copy))
        self._copy_action.triggered.connect(lambda e: print(e))
        self.addAction(self._copy_action)

        self._undo_stack: QtWidgets.QUndoStack = QtWidgets.QUndoStack(self)

        self._undo_action: QtWidgets.QAction = self._undo_stack.createUndoAction(self, "Undo")
        self._undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
        self.addAction(self._undo_action)

        self._redo_action: QtWidgets.QAction = self._undo_stack.createRedoAction(self, "Redo")
        self._redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
        self.addAction(self._redo_action)

    @property
    def undo_stack(self) -> QtWidgets.QUndoStack:
        return self._undo_stack

    def delete_selected_node(self) -> None:
        self._undo_stack.push(DeleteSelectedCommand(self.scene()))

    def scene(self) -> Any:
        return super().scene()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self._last_pos: QtCore.QPointF = self.mapToScene(event.pos())

        if event.button() == QtCore.Qt.LeftButton and self._mode == "":
            super().mousePressEvent(event)

            self._lm_pressed: bool = True

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

        if self._lm_pressed and type(self.itemAt(event.pos())) in (
                NodeItem, QtWidgets.QGraphicsTextItem, QtWidgets.QGraphicsProxyWidget
        ):
            # Addresses all NodeItem components
            self._undo_stack.push(MoveSelectedCommand(self.scene()))

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

        if self._mode == "EDGE_ADD":
            if type(self.itemAt(event.pos())) == PinItem:
                if self._temp_edge.is_valid(eval_target=self.itemAt(event.pos())):
                    self._temp_edge.end_pin = self.itemAt(event.pos())
                    self._temp_edge.end_pin.add_edge(self._temp_edge)
                    self._temp_edge.sort_pins()
                    self._temp_edge.end_pin.socket_widget.update_stylesheets()
                    # TODO: Rewiring unsolved
                    self._undo_stack.push(AddItemCommand(self.scene(), self._temp_edge))
                else:
                    self._temp_edge.end_pin = self._last_pin
                    if self._temp_edge.end_pin != self._temp_edge.start_pin:
                        self._temp_edge.color = self._temp_edge.start_pin.color
                        self._undo_stack.push(RemoveItemCommand(self.scene(), self._temp_edge))
                    else:
                        self.scene().remove_edge(self._temp_edge)
            else:
                self._temp_edge.end_pin = self._last_pin
                if self._temp_edge.end_pin != self._temp_edge.start_pin:
                    self._undo_stack.push(RemoveItemCommand(self.scene(), self._temp_edge))
                else:
                    self.scene().remove_edge(self._temp_edge)

            for node in self.scene().ends():
                dsk: dict = self.scene().to_dsk(node, {})
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

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        print("Context Menu")
        # context_menu: QtWidgets.QMenu = QtWidgets.QMenu(self)
        # context_menu.addAction(self._copy_action)
        # context_menu.exec_(event.globalPos())

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        file_path: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "graph.json")

        if event.matches(QtGui.QKeySequence.Save):
            with open(file_path, "w", encoding="utf8") as json_file:
                json.dump(self.scene().serialize(), json_file, indent=4)

        if event.matches(QtGui.QKeySequence.Open):
            self.scene().clear_scene()
            self._prop_scroller.hide()

            with open(file_path, "r", encoding="utf8") as json_file:
                data_dict: dict = json.load(json_file)
                self.scene().deserialize(data_dict)

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

                if type(self.scene().selectedItems()[0]) is FrameItem:
                    selected_frame: FrameItem = self.scene().selectedItems()[0]

                    self.scene().remove_frame(selected_frame)
                    self._prop_scroller.hide()

        if event.key() == QtCore.Qt.Key_A and event.modifiers() == QtCore.Qt.ShiftModifier:
            new_node = NodeItem()
            new_node.setPos(self.mapToScene(self.mapFromParent(QtGui.QCursor.pos())))
            self._undo_stack.push(AddItemCommand(self.scene(), new_node))

        if event.key() == QtCore.Qt.Key_C and event.modifiers() == QtCore.Qt.ShiftModifier:
            # Serialize selected nodes and edges (sub graph)
            selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if type(item) == NodeItem]
            self._undo_stack.push(CustomNodeCommand(self.scene(), selected_nodes))

        if event.key() == QtCore.Qt.Key_D and event.modifiers() == QtCore.Qt.SHIFT:
            for selected_item in self.scene().selectedItems():
                if type(selected_item) is NodeItem:
                    self.scene().resolve_node(selected_item)

        if event.key() == QtCore.Qt.Key_F:
            selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if type(item) == NodeItem]
            for node in selected_nodes:
                node.remove_from_frame()

            frame: FrameItem = FrameItem(selected_nodes)
            self._undo_stack.push(AddItemCommand(self.scene(), frame))

        if event.key() == QtCore.Qt.Key_Q:
            selected_nodes: list[NodeItem] = [item for item in self.scene().selectedItems() if type(item) == NodeItem]
            if len(selected_nodes) > 0:
                sub_scene: QtWidgets.QGraphicsScene = selected_nodes[0].sub_scene
                if len(sub_scene.nodes) > 0:
                    self._temp_scenes.append(self.scene())
                    self.setScene(sub_scene)

        if event.key() == QtCore.Qt.Key_W:
            if self.scene().parent_node:
                self.setScene(self._temp_scenes.pop())

        super().keyPressEvent(event)

    def focus_prop_scroller(self, focus_target: QtWidgets.QTableView):
        x: int = focus_target.pos().x()
        y: int = focus_target.pos().y()
        self._prop_scroller.ensureVisible(x, y, xmargin=0, ymargin=200)

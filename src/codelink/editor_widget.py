# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2023 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

from typing import Union, Optional, Any, cast
import json
import os

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from undo_commands import (
    AddNodeCommand, RemoveNodeFromFrameCommand, AddGrpNodeCommand, ResolveGrpNodeCommand, MoveNodesCommand,
    RemoveNodeCommand, AddEdgeCommand, RerouteEdgeCommand, RemoveEdgeCommand,  AddFrameCommand, RemoveFrameCommand,
    SwitchSceneDownCommand, SwitchSceneUpCommand, PasteClipboardCommand
)
from node_reg import nodes_dict
from item_delegates import StringDelegate
from property_widget import PropertyWidget
from property_table import PropertyTable
from frame_item import FrameItem
from node_item import NodeItem
from nodes.util.compound_viewer import CompoundViewer
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
        cast(QtCore.SignalInstance, self._open_action.triggered).connect(self.open)
        self.addAction(self._open_action)

        self._save_action: QtWidgets.QAction = QtWidgets.QAction("Save As", self)
        self._save_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Save))
        cast(QtCore.SignalInstance, self._save_action.triggered).connect(self.save_as)
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

        self._delete_action: QtWidgets.QAction = QtWidgets.QAction("Delete", self)
        self._delete_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Delete))
        cast(QtCore.SignalInstance, self._delete_action.triggered).connect(self.delete_selected)
        self.addAction(self._delete_action)

        self._add_frame_action: QtWidgets.QAction = QtWidgets.QAction("Add Frame", self)
        self._add_frame_action.setShortcut(QtGui.QKeySequence("Shift+F"))
        cast(QtCore.SignalInstance, self._add_frame_action.triggered).connect(self.add_frame)
        self.addAction(self._add_frame_action)

        self._add_grp_node_action: QtWidgets.QAction = QtWidgets.QAction("Add Grp Node", self)
        self._add_grp_node_action.setShortcut(QtGui.QKeySequence("Shift+C"))
        cast(QtCore.SignalInstance, self._add_grp_node_action.triggered).connect(self.add_grp_node)
        self.addAction(self._add_grp_node_action)

        self._resolve_grp_node_action: QtWidgets.QAction = QtWidgets.QAction("Resolve Grp Node", self)
        self._resolve_grp_node_action.setShortcut(QtGui.QKeySequence("Shift+D"))
        cast(QtCore.SignalInstance, self._resolve_grp_node_action.triggered).connect(self.resolve_grp_node)
        self.addAction(self._resolve_grp_node_action)

        self._open_sub_action: QtWidgets.QAction = QtWidgets.QAction("Open Sub Graph", self)
        self._open_sub_action.setShortcut(QtGui.QKeySequence("Shift+Q"))
        cast(QtCore.SignalInstance, self._open_sub_action.triggered).connect(self.open_sub_graph)
        self.addAction(self._open_sub_action)

        self._close_sub_action: QtWidgets.QAction = QtWidgets.QAction("Close Sub Graph", self)
        self._close_sub_action.setShortcut(QtGui.QKeySequence("Shift+W"))
        cast(QtCore.SignalInstance, self._close_sub_action.triggered).connect(self.close_sub_graph)
        self.addAction(self._close_sub_action)

        self._copy_action: QtWidgets.QAction = QtWidgets.QAction("Copy", self)
        self._copy_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Copy))
        cast(QtCore.SignalInstance, self._copy_action.triggered).connect(self.copy)
        self.addAction(self._copy_action)

        self._past_action: QtWidgets.QAction = QtWidgets.QAction("Paste", self)
        self._past_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Paste))
        cast(QtCore.SignalInstance, self._past_action.triggered).connect(self.paste)
        self.addAction(self._past_action)

        self._node_actions: dict[str, dict[str, QtWidgets.QAction]] = {}
        for node_category, nodes, in nodes_dict.items():
            if node_category in self._node_actions.keys():
                action_dict: dict[str, QtWidgets.QAction] = self._node_actions[node_category]
            else:
                action_dict: dict[str, list[QtWidgets.QAction]] = {}

            for node_name, node_cls, in nodes.items():
                add_node_action: QtWidgets.QAction = QtWidgets.QAction(node_name, self)
                add_node_action.setData(node_cls)
                add_node_action.triggered.connect(self.add_node_from_action)
                action_dict[node_name] = add_node_action
                self._node_actions[node_category] = action_dict

        # Listeners
        cast(QtCore.SignalInstance, self.zoom_level_changed).connect(self.on_zoom_change)
        cast(QtCore.SignalInstance, self.customContextMenuRequested).connect(self.context_menu)

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
        scene.node_added.connect(lambda node: node.update_details(self._zoom_level))

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            selected_item: Optional[Union[NodeItem, FrameItem]] = None
            if type(self.itemAt(event.pos())) == QtWidgets.QGraphicsTextItem:
                selected_item: Optional[Union[NodeItem, FrameItem]] = self.itemAt(event.pos()).parentItem()
            elif isinstance(self.itemAt(event.pos()), NodeItem) or isinstance(self.itemAt(event.pos()), FrameItem):
                selected_item: Optional[Union[NodeItem, FrameItem]] = self.itemAt(event.pos())

            if selected_item is not None:
                if isinstance(selected_item, NodeItem):
                    selected_item.setSelected(True)
                    prop_widget: PropertyWidget = PropertyWidget(
                        selected_item,
                        width=self._prop_scroller.width(),
                        parent=self._prop_scroller
                    )
                    cast(QtCore.SignalInstance, prop_widget.focus_changed).connect(self.on_prop_scroller_focus_changed)
                    self._prop_scroller.setWidget(prop_widget)
                    self._prop_scroller.show()

                elif isinstance(selected_item, FrameItem):
                    table_view: PropertyTable = PropertyTable()
                    table_view.setModel(selected_item.prop_model)
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
                    temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                    temp_target.setPos(self._last_pin.parentItem().mapToScene(self._last_pin.center()))
                    self._temp_edge = self.scene().add_edge_from_pins(self._last_pin, temp_target)

                elif self._last_pin.socket_widget.is_input and self._last_pin.has_edges():
                    self._mode: str = "EDGE_EDIT"
                    self._temp_edge: EdgeItem = self._last_pin.edges[-1]
                    temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                    temp_target.setPos(self._last_pin.parentItem().mapToScene(self._last_pin.center()))

                    self._temp_edge.end_pin.remove_edge(self._temp_edge)
                    self._temp_edge.end_pin.socket_widget.update_stylesheets()
                    self._temp_edge.end_pin = temp_target
                    self._mode = "EDGE_ADD"

        elif event.button() == QtCore.Qt.MiddleButton:
            super().mousePressEvent(event)
            self._mode: str = "SCENE_DRAG"
            self._mm_pressed: bool = True
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeAllCursor)

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
                    self._undo_stack.push(RemoveEdgeCommand(self.scene(), cast(EdgeItem, item)))

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        if event.button() == QtCore.Qt.LeftButton and self._mode not in ("EDGE_ADD", "EDGE_EDIT", "EDGE_CUT"):
            selected_nodes: list[NodeItem] = self.scene().selected_nodes()
            selected_nodes_moved: list[bool] = [node.moved for node in self.scene().selected_nodes()]

            if any(selected_nodes_moved):
                self._undo_stack.push(MoveNodesCommand(selected_nodes))
                for node in selected_nodes:
                    node.moved = False

        if self._mode == "EDGE_ADD":
            if type(self.itemAt(event.pos())) == PinItem:
                if self._temp_edge.is_valid(eval_target=self.itemAt(event.pos())):
                    self._temp_edge.end_pin = self.itemAt(event.pos())
                    self._temp_edge.end_pin.add_edge(self._temp_edge)
                    self._temp_edge.end_pin.socket_widget.update_stylesheets()

                    if self._temp_edge.end_pin != self._last_pin:
                        last_pin_is_in: bool = self._last_pin.socket_widget.is_input
                        end_pin_is_in: bool = self._temp_edge.end_pin.socket_widget.is_input
                        self._temp_edge.sort_pins()

                        if (not last_pin_is_in and end_pin_is_in) or (last_pin_is_in and not end_pin_is_in):
                            self._undo_stack.push(AddEdgeCommand(self.scene(), self._temp_edge))
                        else:
                            self._undo_stack.push(RerouteEdgeCommand(self.scene(), edge=self._temp_edge,
                                                                     undo_pin=self._last_pin,
                                                                     redo_pin=self._temp_edge.end_pin))
                        cast(QtCore.SignalInstance, self.scene().dag_changed).emit(
                            self._temp_edge.end_pin.parent_node
                        )
                else:
                    self._temp_edge.end_pin = self._last_pin
                    if self._temp_edge.end_pin != self._temp_edge.start_pin:
                        # Invalid edge because of rerouting
                        self._temp_edge.color = self._temp_edge.start_pin.color
                        self._undo_stack.push(RemoveEdgeCommand(self.scene(), self._temp_edge))
                    else:
                        # Invalid edge with same start and end pin
                        self.scene().remove_edge(self._temp_edge)

                    for node in self.scene().ends():
                        cast(QtCore.SignalInstance, self.scene().dag_changed).emit(node)
            else:
                # If target is not a PinItem (mouse btn release in empty area)
                self._temp_edge.end_pin = self._last_pin
                if self._temp_edge.end_pin != self._temp_edge.start_pin:
                    self._undo_stack.push(RemoveEdgeCommand(self.scene(), self._temp_edge))
                else:
                    self.scene().remove_edge(self._temp_edge)

                for node in self.scene().ends():
                    cast(QtCore.SignalInstance, self.scene().dag_changed).emit(node)

            # Evaluates open dag ends
            # self.scene().dag_changed.emit(self._temp_edge.end_pin.parent_node)
            # for node in self.scene().ends():
            #     dsk: dict = self.scene().to_dsk(node, {})
            #     for socket in node.output_socket_widgets:
            #         print(get(dsk, node.linked_lowest_socket(socket).pin))
            #
            #     # Pretty prints dask graph
            #     string_dsk: dict = dict()
            #     for pin, args in dsk.items():
            #         pretty_args: list = list()
            #         for arg_item in args:
            #             if hasattr(arg_item, "__name__"):
            #                 # Eval method
            #                 pretty_args.append(arg_item.__name__)
            #             elif type(arg_item) == list:
            #                 # Socket wise eval inputs
            #                 inputs: list = list()
            #                 for socket_input in arg_item:
            #                     if type(socket_input) == PinItem:
            #                         inputs.append(socket_input.socket_widget.prop_model.properties["Name"])
            #                     else:
            #                         inputs.append(socket_input)
            #                 pretty_args.append(inputs)
            #         string_dsk_key: str = pin.socket_widget.prop_model.properties["Name"]
            #         if string_dsk_key in list(string_dsk.keys()):
            #             string_dsk_key: str = string_dsk_key + str(random.randint(0, 1000))
            #         string_dsk[string_dsk_key] = str(pretty_args)
            #
            #     # print(json.dumps(string_dsk, indent=4))

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
                print("Stack Item", self._undo_stack.command(i), self._undo_stack.command(i).id())

            # Test area
            # selection: list[NodeItem] = self.scene().selected_nodes()

        super().keyPressEvent(event)

    # --------------- Menus ---------------
    def context_menu(self, position: QtCore.QPoint):
        if type(self.itemAt(position)) == PinItem:
            # Socket menu
            pin: PinItem = self.itemAt(position)
            socket_actions: list[QtWidgets.QAction] = pin.socket_widget.socket_actions()
            socket_menu: QtWidgets.QMenu = QtWidgets.QMenu(self)
            socket_menu.addActions(socket_actions)
            socket_menu.exec_(self.mapToGlobal(position))

        else:
            context_menu: QtWidgets.QMenu = QtWidgets.QMenu(self)

            # Add menu
            add_menu: QtWidgets.QMenu = QtWidgets.QMenu(context_menu)
            add_menu.setTitle("&Add")
            for node_category, nodes in self._node_actions.items():
                new_menu: QtWidgets.QMenu = QtWidgets.QMenu(add_menu)
                new_menu.setTitle(node_category)

                for node_name, node_action in nodes.items():
                    new_menu.addAction(node_action)
                add_menu.addMenu(new_menu)
            context_menu.addMenu(add_menu)
            context_menu.addSeparator()

            # Rest of context menu
            context_menu.addAction(self._open_action)
            context_menu.addAction(self._save_action)
            context_menu.addSeparator()

            # context_menu.addAction(self._undo_action)
            # context_menu.addAction(self._redo_action)
            context_menu.addAction(self._fit_action)

            selected_items: list[Any] = self.scene().selectedItems()
            nodes_selected: bool = any(isinstance(item, NodeItem) for item in selected_items)
            frames_selected: bool = any(isinstance(item, FrameItem) for item in selected_items)

            if nodes_selected or frames_selected:
                self._delete_action.setEnabled(True)
            else:
                self._delete_action.setEnabled(False)
            context_menu.addAction(self._delete_action)

            context_menu.addSeparator()

            if nodes_selected:
                self._add_frame_action.setEnabled(True)
                self._add_grp_node_action.setEnabled(True)
            else:
                self._add_frame_action.setEnabled(False)
                self._add_grp_node_action.setEnabled(False)
            context_menu.addAction(self._add_frame_action)
            context_menu.addAction(self._add_grp_node_action)

            if nodes_selected and self.scene().selected_nodes()[0].has_sub_scene():
                self._open_sub_action.setEnabled(True)
                self._resolve_grp_node_action.setEnabled(True)
            else:
                self._open_sub_action.setEnabled(False)
                self._resolve_grp_node_action.setEnabled(False)
            context_menu.addAction(self._resolve_grp_node_action)
            context_menu.addAction(self._open_sub_action)

            if self.scene().parent_node is not None:
                self._close_sub_action.setEnabled(True)
            else:
                self._close_sub_action.setEnabled(False)
            context_menu.addAction(self._close_sub_action)

            context_menu.exec_(self.mapToGlobal(position))

            self._delete_action.setEnabled(True)
            self._add_frame_action.setEnabled(True)
            self._add_grp_node_action.setEnabled(True)
            self._resolve_grp_node_action.setEnabled(True)
            self._open_sub_action.setEnabled(True)
            self._close_sub_action.setEnabled(True)

    # --------------- Viewport, focus and zoom ---------------

    def on_prop_scroller_focus_changed(self, focus_target: QtWidgets.QTableView):
        x: int = focus_target.pos().x()
        y: int = focus_target.pos().y()
        self._prop_scroller.ensureVisible(x, y, xmargin=0, ymargin=300)

    def fit_content(self) -> None:
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

    def fit_min(self) -> None:
        self.zoom_min()
        self.fit_content()

    def zoom_min(self):
        while self._zoom_level > self._zoom_level_range[0]:
            self._zoom_level -= 1
            self.scale(1 / 1.25, 1 / 1.25)
        cast(QtCore.SignalInstance, self.zoom_level_changed).emit(self._zoom_level)

    def on_zoom_change(self, zoom_level: int) -> None:
        self.scene().update_details(zoom_level)

    # --------------- Action callbacks ---------------

    def add_node_from_action(self):
        node_cls: type = self.sender().data()
        new_pos: QtCore.QPointF = self.mapToScene(self.mapFromParent(QtGui.QCursor.pos()))
        new_node: node_cls = node_cls((new_pos.x(), new_pos.y()), self._undo_stack)
        self._undo_stack.push(AddNodeCommand(self.scene(), new_node))
        cast(QtCore.SignalInstance, self.scene().dag_changed).emit(new_node)

    def open(self):
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

            self.fit_content()

    def save_as(self):
        file_path: str = os.path.normpath(QtWidgets.QFileDialog.getSaveFileName(self)[0])
        # file_path: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "graph.json")

        if file_path != ".":
            with open(file_path, "w", encoding="utf8") as json_file:
                json.dump(self.scene().serialize(), json_file, indent=4)

    def copy(self) -> None:
        if len(self.scene().selectedItems()) > 0:
            self.scene().selection_to_clipboard()

    def paste(self) -> None:

        # Yields all values corresponding to a key (i.e. "UUID") in a nested dictionary
        def find_key_values(state: dict, key: str) -> str:
            if isinstance(state, list):
                for i in state:
                    for x in find_key_values(i, key):
                        yield x

            elif isinstance(state, dict):
                if key in state:
                    yield state[key]
                for j in state.values():
                    for x in find_key_values(j, key):
                        yield x

        # Replaces all occurrences of old_value with new_value for a given key in a nested dictionary
        def replace_key_values(state: dict, key: str, old_value: str, new_value: str) -> None:
            if isinstance(state, list):
                for i in state:
                    replace_key_values(i, key, old_value, new_value)

            elif isinstance(state, dict):
                if key in state:
                    if type(state[key]) is list and key == "Link":
                        if state[key][0] == old_value:
                            state[key] = (new_value, state[key][1])
                    elif type(state[key]) is list and key == "Framed Nodes UUID's":
                        for idx, value in enumerate(state[key]):
                            if value == old_value:
                                state[key][idx] = new_value
                    else:
                        if state[key] == old_value:
                            state[key] = new_value

                for j in state.values():
                    replace_key_values(j, key, old_value, new_value)

        try:
            clipboard_state: dict = json.loads(QtWidgets.QApplication.clipboard().text())
            paste_pos: QtCore.QPointF = self.scene().views()[0].mapToScene(
                self.scene().views()[0].mapFromParent(QtGui.QCursor.pos())
            )

            # Replacement uuid map
            uuid_map: dict[str] = {
                uuid: QtCore.QUuid().createUuid().toString() for uuid in find_key_values(clipboard_state, "UUID")
            }

            # Replaces old uuids with new ones in clipboard state
            for k, v in uuid_map.items():
                replace_key_values(clipboard_state, "UUID", k, v)
                replace_key_values(clipboard_state, "Link", k, v)
                replace_key_values(clipboard_state, "Start Node UUID", k, v)
                replace_key_values(clipboard_state, "End Node UUID", k, v)
                replace_key_values(clipboard_state, "Framed Nodes UUID's", k, v)

            nodes: list[NodeItem] = self.scene().deserialize_nodes(clipboard_state["Nodes"])
            edges: list[EdgeItem] = self.scene().deserialize_edges(clipboard_state["Edges"])
            frames: list[FrameItem] = self.scene().deserialize_frames(clipboard_state["Frames"])

            scene_bbox: QtCore.QRectF = self.scene().bounding_rect(nodes)
            scene_center: QtCore.QPointF = QtCore.QPointF(
                scene_bbox.x() + scene_bbox.width() / 2,
                scene_bbox.y() + scene_bbox.height() / 2
            )
            dx: float = paste_pos.x() - scene_center.x()
            dy: float = paste_pos.y() - scene_center.y()

            for node in nodes:
                node.setPos(dx + node.x(), dy + node.y())
                node.last_position = QtCore.QPointF(dx + node.x(), dy + node.y())
                if type(node) == CompoundViewer:
                    node.compound_name = ""

            self.scene().clearSelection()
            to_be_selected: list[Any] = cast(list[QtWidgets.QGraphicsItem], nodes) + cast(
                list[QtWidgets.QGraphicsItem], frames)
            for item in to_be_selected:
                item.setSelected(True)

            self._undo_stack.push(PasteClipboardCommand(self.scene(), nodes, edges, frames))

            for node in self.scene().ends():
                if node in nodes:
                    cast(QtCore.SignalInstance, self.scene().dag_changed).emit(node)

        except json.JSONDecodeError:
            print("Pasting failed!")

    def delete_selected(self) -> None:
        nodes: list[NodeItem] = [node for node in self.scene().selected_nodes() if not node.is_grp_interface()]
        edges: list[EdgeItem] = self.scene().selected_edges()
        frames: list[FrameItem] = self.scene().selected_frames()

        linked_frames: set[FrameItem] = set()
        linked_edges: set[EdgeItem] = set()
        for node in nodes:
            if node.parent_frame is not None:
                linked_frames.add(node.parent_frame)
            for socket_widget in node.socket_widgets:
                for edge in socket_widget.pin.edges:
                    linked_edges.add(edge)

        self._undo_stack.beginMacro("Delete selected items")
        for frame in linked_frames:
            for node in nodes:
                if node in frame.framed_nodes:
                    self._undo_stack.push(RemoveNodeFromFrameCommand(node, frame))
                    if len(frame.framed_nodes) == 0:
                        self._undo_stack.push(RemoveFrameCommand(self.scene(), frame))

        for frame in frames:
            if frame in self.scene().frames:
                self._undo_stack.push(RemoveFrameCommand(self.scene(), frame))
        for edge in linked_edges.union(set(edges)):
            self._undo_stack.push(RemoveEdgeCommand(self.scene(), edge))
        for node in nodes:
            self._undo_stack.push(RemoveNodeCommand(self.scene(), node))
        self._undo_stack.endMacro()

        for node in self.scene().ends():
            cast(QtCore.SignalInstance, self.scene().dag_changed).emit(node)

    def add_grp_node(self):
        sub_nodes: list[NodeItem] = self.scene().selected_nodes()

        if len(sub_nodes) > 0:
            new_interface_nodes: set[NodeItem] = self.scene().grp_interfaces(sub_nodes)
            is_valid: bool = not any([node.has_sub_scene() for node in new_interface_nodes])

            if is_valid:
                selection_rect: QtCore.QRectF = self.scene().bounding_rect(sub_nodes)
                selection_center_x: float = selection_rect.x() + selection_rect.width() / 2
                selection_center_y: float = selection_rect.y() + selection_rect.height() / 2

                # Creates grp node
                grp_node: NodeItem = NodeItem((0, 0), self._undo_stack)
                grp_node.prop_model.properties["Name"] = "Group Node"

                self.scene().add_node(grp_node)

                # Adds socket widgets
                sub_edges: list[EdgeItem] = []
                for edge in self.scene().edges:
                    if edge.start_pin.parentItem() in sub_nodes and edge.end_pin.parentItem() in sub_nodes:
                        sub_edges.append(edge)

                for node_idx, node in enumerate(sub_nodes):
                    for socket_idx, socket_widget in enumerate(node.socket_widgets):
                        connected_edges: list[EdgeItem] = socket_widget.pin.edges
                        outer_socket_edges: list[EdgeItem] = [
                            edge for edge in connected_edges if edge not in sub_edges
                        ]

                        if len(outer_socket_edges) > 0:
                            new_socket_widget: socket_widget.__class__ = socket_widget.__class__(
                                undo_stack=self._undo_stack,
                                name=socket_widget.prop_model.properties["Name"],
                                content_value=socket_widget.prop_model.properties["Value"],
                                is_flatten=socket_widget.prop_model.properties["Flatten"],
                                is_simplify=socket_widget.prop_model.properties["Simplify"],
                                is_graft=socket_widget.prop_model.properties["Graft"],
                                is_graft_topo=socket_widget.prop_model.properties["Graft Topo"],
                                is_unwrap=socket_widget.prop_model.properties["Unwrap"],
                                is_wrap=socket_widget.prop_model.properties["Wrap"],
                                parent_node=grp_node
                            )
                            new_socket_widget.is_input = socket_widget.is_input
                            new_socket_widget.link = (node.uuid, socket_idx)
                            grp_node.insert_socket_widget(new_socket_widget, len(grp_node.socket_widgets))

                grp_node.evals = grp_node.evals * len(grp_node.output_socket_widgets)

                grp_node.setPos(
                    selection_center_x - grp_node.boundingRect().width() / 2,
                    selection_center_y - grp_node.boundingRect().height() / 2
                )
                grp_node.last_position = QtCore.QPointF(
                    selection_center_x - grp_node.boundingRect().width() / 2,
                    selection_center_y - grp_node.boundingRect().height() / 2
                )

                outside_frames: list[FrameItem] = self.scene().outside_frames(sub_nodes)
                linked_to_outside_frame: set[NodeItem] = set()
                for outside_frame in outside_frames:
                    in_both_sets: set[NodeItem] = set(outside_frame.framed_nodes).intersection(sub_nodes)
                    linked_to_outside_frame: set[NodeItem] = linked_to_outside_frame.union(in_both_sets)

                for node in linked_to_outside_frame:
                    self._undo_stack.push(RemoveNodeFromFrameCommand(node, node.parent_frame))

                self._undo_stack.push(AddGrpNodeCommand(self.scene(), grp_node, sub_nodes))

    def resolve_grp_node(self):
        if len(self.scene().selected_nodes()) > 0 and self.scene().selected_nodes()[0].has_sub_scene():
            grp_node: NodeItem = self.scene().selected_nodes()[0]
            if grp_node.parent_frame is not None:
                old_frame_uuid: str = grp_node.parent_frame.uuid
                self._undo_stack.push(RemoveNodeFromFrameCommand(grp_node, grp_node.parent_frame))
                if len(self.scene().dag_item(old_frame_uuid).framed_nodes) == 0:
                    self._undo_stack.push(RemoveFrameCommand(self.scene(), self.scene().dag_item(old_frame_uuid)))

            self._undo_stack.push(ResolveGrpNodeCommand(self.scene(), grp_node))

    def add_frame(self):
        selected_nodes: list[NodeItem] = self.scene().selected_nodes()
        if len(selected_nodes) > 0:
            for node in selected_nodes:
                if node.parent_frame is not None:
                    old_frame_uuid: str = node.parent_frame.uuid
                    self._undo_stack.push(RemoveNodeFromFrameCommand(node, node.parent_frame))
                    if len(self.scene().dag_item(old_frame_uuid).framed_nodes) == 0:
                        self._undo_stack.push(RemoveFrameCommand(self.scene(), self.scene().dag_item(old_frame_uuid)))

            frame: FrameItem = FrameItem(selected_nodes, self._undo_stack)
            for node in selected_nodes:
                node.parent_frame = frame
            self._undo_stack.push(AddFrameCommand(self.scene(), frame))

    def open_sub_graph(self):
        selected_nodes: list[NodeItem] = self.scene().selected_nodes()

        if len(selected_nodes) > 0 and selected_nodes[0].has_sub_scene():
            self._undo_stack.push(SwitchSceneDownCommand(self, self.scene(), selected_nodes[0]))
            self.fit_content()

    def close_sub_graph(self):
        if self.scene().parent_node:
            self._undo_stack.push(SwitchSceneUpCommand(self, self.scene().parent_node.scene(), self.scene()))
            self.fit_content()

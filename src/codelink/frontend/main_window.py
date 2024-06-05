#!/usr/bin/env python

# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2024 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
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

from typing import cast, Optional, Any
import sys
from pathlib import Path
import json
from functools import partial

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.node_factory import NodeFactory
from codelink.backend.tree_model import TreeModel
from codelink.backend.tree_item import TreeItem
from codelink.backend.node_item import NodeItem

from codelink.frontend.tree_view import TreeView
from codelink.frontend.graphics_scene import GraphicsScene


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._undo_stack: QtWidgets.QUndoStack = QtWidgets.QUndoStack()

        self._node_factory: NodeFactory = NodeFactory()
        self._node_factory.load_nodes(str(Path("../backend/nodes").resolve()))
        self._model: TreeModel = self.create_tree_model()

        # UI
        self.setWindowTitle("CodeLink")
        self.create_menu()

        self._graphics_view: QtWidgets.QGraphicsView = self.create_graphics_view()
        self._main_tree_view: QtWidgets.QTreeView = self.create_main_tree_view()
        self._inspection_view: QtWidgets.QTreeView = self.create_inspection_view()

    @property
    def model(self) -> TreeModel:
        return self._model

    def create_tree_model(self, file: Optional[str] = None) -> QtCore.QAbstractItemModel:
        state: Optional[dict[str, Any]] = None

        if file:
            with open(str(Path(file).resolve()), "r", encoding="utf-8") as f:
                state: dict[str, Any] = json.load(f)

        model: TreeModel = TreeModel(data=state, undo_stack=self._undo_stack)
        model.rowsInserted.connect(
            lambda parent_idx, first_row_idx, last_row_idx: print("Inserted at:", first_row_idx)
        )
        model.rowsRemoved.connect(
            lambda parent_idx, first_row_idx, last_row_idx: print("Removed at:", first_row_idx)
        )
        model.dataChanged.connect(
            lambda top_left_idx, bottom_right_idx, roles: print(
                "Changed at:", top_left_idx.row(), top_left_idx.column(), "to:",
                top_left_idx.data(roles[0]) if len(roles) > 0 else None)
        )
        return model

    def create_menu(self) -> None:
        file_menu: QtWidgets.QMenu = self.menuBar().addMenu("&File")

        open_action: QtWidgets.QAction = file_menu.addAction("&Open")
        open_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Open))
        self.addAction(open_action)
        file_menu.addAction(open_action)
        open_action.triggered.connect(self.open_file)

        save_action: QtWidgets.QAction = file_menu.addAction("&Save")
        save_action.triggered.connect(lambda: print("Save"))

        edit_menu: QtWidgets.QMenu = self.menuBar().addMenu("&Edit")

        del_action: QtWidgets.QAction = edit_menu.addAction("&Delete")
        del_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Delete))
        self.addAction(del_action)
        edit_menu.addAction(del_action)
        del_action.triggered.connect(self.delete_selection)

        undo_action: QtWidgets.QAction = self._undo_stack.createUndoAction(self, "&Undo")
        undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
        self.addAction(undo_action)
        edit_menu.addAction(undo_action)

        redo_action: QtWidgets.QAction = self._undo_stack.createRedoAction(self, "&Redo")
        redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
        self.addAction(redo_action)
        edit_menu.addAction(redo_action)

        nodes_menu: QtWidgets.QMenu = self.menuBar().addMenu("&Nodes")
        self.populate_nodes_menu(nodes_menu)

    def populate_nodes_menu(self, nodes_menu: QtWidgets.QMenu) -> None:
        def add_node(node_cls: str) -> None:
            node: NodeItem = self._node_factory.create_node(node_cls)
            self._model.append_node(node)

        for key in self._node_factory.nodes.keys():
            parent_menu: QtWidgets.QMenu = nodes_menu

            menu_titles: list[str] = key.split(".")[1:]
            pretty_titles: list[str] = [menu_title.replace("_", " ").title() for menu_title in menu_titles[:-1]]
            pretty_titles.append(menu_titles[-1])

            for idx, pretty_title in enumerate(pretty_titles):
                if pretty_title not in [action.text() for action in parent_menu.actions()]:
                    if idx < len(menu_titles) - 2:
                        parent_menu: QtWidgets.QMenu = parent_menu.addMenu(pretty_title)
                    elif idx == len(menu_titles) - 1:
                        add_action: QtWidgets.QAction = QtWidgets.QAction(pretty_title, self)
                        add_action.triggered.connect(partial(add_node, key))
                        parent_menu.addAction(add_action)
                else:
                    parent_action: QtWidgets.QAction = parent_menu.actions()[-1]
                    parent_menu: QtWidgets.QMenu = parent_action.menu()

    def create_graphics_view(self) -> QtWidgets.QGraphicsView:
        graphics_view: QtWidgets.QGraphicsView = QtWidgets.QGraphicsView()
        graphics_scene: GraphicsScene = GraphicsScene()
        graphics_view.setScene(graphics_scene)
        self.setCentralWidget(graphics_view)
        return graphics_view

    def create_main_tree_view(self) -> QtWidgets.QTreeView:
        dock: QtWidgets.QDockWidget = QtWidgets.QDockWidget("Graph View", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        main_tree_view: TreeView = TreeView()
        main_tree_view.setModel(self._model)
        main_tree_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._model.rowsInserted.connect(
            lambda: main_tree_view.expandRecursively(QtCore.QModelIndex())
        )
        main_tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        dock.setWidget(main_tree_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        return main_tree_view

    def create_inspection_view(self) -> QtWidgets.QTreeView:
        dock = QtWidgets.QDockWidget("Inspection View", self)
        inspection_view: TreeView = TreeView()
        inspection_view.setModel(self._model)
        inspection_view.setIndentation(0)
        self._model.rowsInserted.connect(
            lambda: inspection_view.expandRecursively(QtCore.QModelIndex())
        )
        dock.setWidget(inspection_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        return inspection_view

    # noinspection PyUnusedLocal
    def on_selection_changed(self, current: QtCore.QItemSelection, previous: QtCore.QItemSelection) -> None:
        if len(current.indexes()) > 0:
            index: QtCore.QModelIndex = cast(QtCore.QModelIndex, current.indexes()[0])
            tree_item: TreeItem = self._model.item_from_index(index)
            if isinstance(tree_item, NodeItem):
                self._inspection_view.setRootIndex(index)
        else:
            self._inspection_view.setRootIndex(QtCore.QModelIndex())

    def open_file(self) -> None:
        file_name: str = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open file", "./", "Json files (*.json);;All files (*.*)"
        )[0]

        try:
            self._model: TreeModel = self.create_tree_model(file=file_name)
            self.setWindowTitle(file_name)
            self._main_tree_view.setModel(self._model)
            self._main_tree_view.expandAll()
            self._inspection_view.setModel(self._model)
            self._inspection_view.expandAll()

        except (json.decoder.JSONDecodeError, IndexError, ValueError, AttributeError):
            print("File reading error")

    def delete_selection(self) -> None:
        selected_indexes: list[QtCore.QModelIndex] = self._main_tree_view.selectionModel().selectedIndexes()
        while selected_indexes:
            selected_index: QtCore.QModelIndex = selected_indexes.pop()
            if selected_index.column() == 0:
                tree_item: Optional[TreeItem] = self._model.item_from_index(selected_index)
                if isinstance(tree_item, NodeItem):
                    index: QtCore.QModelIndex = cast(QtCore.QModelIndex, selected_index)
                    self._model.removeRow(index.row(), index.parent())


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    main_window: MainWindow = MainWindow()

    main_window.model.append_node(NodeItem("Node 1"))
    main_window.model.append_node(NodeItem("Node 2"))
    main_window.model.append_node(NodeItem("Node 3"))

    main_window.show()
    sys.exit(app.exec_())

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

from typing import cast
import sys
from pathlib import Path
from functools import partial

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.node_factory import NodeFactory
from codelink.backend.tree_model import TreeModel
from codelink.backend.node_item import NodeItem

from tree_view import TreeView


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._undo_stack: QtWidgets.QUndoStack = QtWidgets.QUndoStack()

        self._node_factory: NodeFactory = NodeFactory()
        self._node_factory.load_nodes(str(Path("../backend/nodes").resolve()))

        self._model: TreeModel = TreeModel(undo_stack=self._undo_stack)
        self._model.rowsInserted.connect(
            lambda parent_idx, first_row_idx, last_row_idx: print("Inserted at:", first_row_idx)
        )
        self._model.rowsRemoved.connect(
            lambda parent_idx, first_row_idx, last_row_idx: print("Removed at:", first_row_idx)
        )
        self._model.dataChanged.connect(
            lambda top_left_idx, bottom_right_idx, roles: print(
                "Changed at:", top_left_idx.row(), top_left_idx.column(), "to:",
                top_left_idx.data(roles[0]) if len(roles) > 0 else None)
        )

        self.setWindowTitle("CodeLink")
        self.create_menu()
        self.create_central_widget()
        self.create_dock_widgets()

    def create_menu(self) -> None:
        file_menu: QtWidgets.QMenu = self.menuBar().addMenu("&File")
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
        def create_node(node_cls: str) -> None:
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
                        add_action.triggered.connect(partial(create_node, key))
                        parent_menu.addAction(add_action)
                else:
                    parent_action: QtWidgets.QAction = parent_menu.actions()[-1]
                    parent_menu: QtWidgets.QMenu = parent_action.menu()

    def create_central_widget(self) -> None:
        graphics_view: QtWidgets.QGraphicsView = QtWidgets.QGraphicsView()
        graphics_scene: QtWidgets.QGraphicsScene = QtWidgets.QGraphicsScene()
        graphics_view.setScene(graphics_scene)
        graphics_scene.addRect(
            QtCore.QRectF(-100, -50, 200, 50), QtGui.QPen("#000"), QtGui.QBrush("#fff")
        )
        self.setCentralWidget(graphics_view)

    def create_dock_widgets(self) -> None:
        dock: QtWidgets.QDockWidget = QtWidgets.QDockWidget("Graph View", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        main_tree_view: TreeView = TreeView()
        main_tree_view.setModel(self._model)
        self._model.rowsInserted.connect(
            lambda: main_tree_view.expandRecursively(QtCore.QModelIndex())
        )

        dock.setWidget(main_tree_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

        dock = QtWidgets.QDockWidget("Inspection View", self)
        inspection_tree_view: TreeView = TreeView()
        inspection_tree_view.setModel(self._model)
        inspection_tree_view.setIndentation(0)

        main_tree_view.selectionModel().selectionChanged.connect(
            lambda current, previous: inspection_tree_view.setRootIndex(
                cast(QtCore.QItemSelection, current).indexes()[0]
            )
        )

        self._model.rowsInserted.connect(
            lambda: inspection_tree_view.expandRecursively(QtCore.QModelIndex())
        )

        dock.setWidget(inspection_tree_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    def on_selection_changed(self, current, previous) -> None:
        pass

    @staticmethod
    def delete_selection() -> None:
        print("Delete selection")


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())

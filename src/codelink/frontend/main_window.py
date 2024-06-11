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
from codelink.backend.edge_item import EdgeItem
from codelink.backend.proxy_models import Level2ProxyModel, Level4ProxyModel

from codelink.frontend.tree_view import TreeView
from codelink.frontend.document_view import DocumentView


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._node_factory: NodeFactory = NodeFactory()
        self._node_factory.load_nodes(str(Path("../backend/nodes").resolve()))

        self._active_doc_model: Optional[TreeModel] = None
        self._active_undo_stack: Optional[QtWidgets.QUndoStack] = None
        self._active_doc_view: Optional[DocumentView] = None

        # UI
        self.setWindowTitle("CodeLink")
        self.resize(1280, 800)
        self.create_menu()

        self._mdi_area: QtWidgets.QMdiArea = self.create_mdi_area()
        self._main_tree_view: QtWidgets.QTreeView = self.create_main_tree_view()
        self._item_tree_view: QtWidgets.QTreeView = self.create_item_tree_view()
        self._detail_tree_view: QtWidgets.QTreeView = self.create_detail_tree_view()

    @staticmethod
    def create_tree_model(file_name: Optional[str] = None) -> QtCore.QAbstractItemModel:
        state: Optional[dict[str, Any]] = None

        if file_name:
            try:
                with open(str(Path(file_name).resolve()), "r", encoding="utf-8") as f:
                    state: dict[str, Any] = json.load(f)
            except (FileNotFoundError, json.decoder.JSONDecodeError):
                print("File loading error")

        tree_model: TreeModel = TreeModel(data=state, undo_stack=QtWidgets.QUndoStack())
        return tree_model

    def create_menu(self) -> None:
        file_menu: QtWidgets.QMenu = self.menuBar().addMenu("&File")

        new_action: QtWidgets.QAction = file_menu.addAction("&New")
        new_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.New))
        self.addAction(new_action)
        file_menu.addAction(new_action)
        new_action.triggered.connect(self.new)

        open_action: QtWidgets.QAction = file_menu.addAction("&Open")
        open_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Open))
        self.addAction(open_action)
        file_menu.addAction(open_action)
        open_action.triggered.connect(self.open)

        save_as_action: QtWidgets.QAction = file_menu.addAction("Save &As")
        save_as_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.SaveAs))
        self.addAction(save_as_action)
        file_menu.addAction(save_as_action)
        save_as_action.triggered.connect(self.save_as)

        save_action: QtWidgets.QAction = file_menu.addAction("&Save")
        save_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Save))
        self.addAction(save_action)
        file_menu.addAction(save_action)
        save_action.triggered.connect(self.save)

        exit_action: QtWidgets.QAction = file_menu.addAction("E&xit")
        file_menu.addAction(exit_action)
        exit_action.triggered.connect(QtWidgets.QApplication.quit)

        edit_menu: QtWidgets.QMenu = self.menuBar().addMenu("&Edit")

        del_action: QtWidgets.QAction = edit_menu.addAction("&Delete")
        del_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Delete))
        self.addAction(del_action)
        edit_menu.addAction(del_action)
        del_action.triggered.connect(self.delete_selection)

        # undo_action: QtWidgets.QAction = self._undo_stack.createUndoAction(self, "&Undo")
        # undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
        # self.addAction(undo_action)
        # edit_menu.addAction(undo_action)

        # redo_action: QtWidgets.QAction = self._undo_stack.createRedoAction(self, "&Redo")
        # redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
        # self.addAction(redo_action)
        # edit_menu.addAction(redo_action)

        nodes_menu: QtWidgets.QMenu = self.menuBar().addMenu("&Nodes")
        self.populate_nodes_menu(nodes_menu)

    def populate_nodes_menu(self, nodes_menu: QtWidgets.QMenu) -> None:
        def add_node(node_cls: str) -> None:
            node: NodeItem = self._node_factory.create_node(node_cls)
            self._tree_model.append_node(node)

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

    def create_mdi_area(self) -> QtWidgets.QMdiArea:
        mdi_area: QtWidgets.QMdiArea = QtWidgets.QMdiArea()
        mdi_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        mdi_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        mdi_area.setViewMode(QtWidgets.QMdiArea.TabbedView)
        mdi_area.setDocumentMode(True)
        mdi_area.setTabsClosable(True)
        mdi_area.setTabsMovable(True)

        mdi_area.subWindowActivated.connect(self.on_sub_wnd_changed)
        self.setCentralWidget(mdi_area)
        return mdi_area

    def create_main_tree_view(self) -> QtWidgets.QTreeView:
        dock: QtWidgets.QDockWidget = QtWidgets.QDockWidget("Main View", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        main_tree_view: TreeView = TreeView()
        dock.setWidget(main_tree_view)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        return main_tree_view

    def create_item_tree_view(self) -> QtWidgets.QTreeView:
        dock = QtWidgets.QDockWidget("Item View", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        item_tree_view: TreeView = TreeView()
        dock.setWidget(item_tree_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        return item_tree_view

    def create_detail_tree_view(self) -> QtWidgets.QTreeView:
        dock = QtWidgets.QDockWidget("Detail View", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        detail_view: TreeView = TreeView()
        dock.setWidget(detail_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        return detail_view

    # noinspection PyUnusedLocal
    def on_selection_changed(self, current: QtCore.QItemSelection, previous: QtCore.QItemSelection) -> None:
        if len(current.indexes()) > 0:
            index: QtCore.QModelIndex = cast(QtCore.QModelIndex, current.indexes()[0])
            if isinstance(index.model(), QtCore.QSortFilterProxyModel):
                index: QtCore.QModelIndex = index.model().mapToSource(index)

            tree_item: TreeItem = self._active_doc_model.item_from_index(index)
            if isinstance(tree_item, NodeItem) or isinstance(tree_item, EdgeItem):
                proxy_model: Level4ProxyModel = Level4ProxyModel()
                proxy_model.setSourceModel(self._active_doc_model)
                self._detail_tree_view.setModel(proxy_model)
                self._detail_tree_view.setRootIndex(proxy_model.mapFromSource(index))
                self._detail_tree_view.expandAll()
            else:
                self._detail_tree_view.setModel(None)
        else:
            self._detail_tree_view.setModel(None)

    def on_sub_wnd_changed(self, sub_wnd: QtWidgets.QMdiSubWindow) -> None:
        if len(self._mdi_area.subWindowList()) > 0 and sub_wnd:
            self._active_doc_view: DocumentView = cast(DocumentView, sub_wnd.widget())
            self._active_doc_model: TreeModel = self._active_doc_view.model
            self._active_undo_stack: QtWidgets.QUndoStack = self._active_doc_model.undo_stack

            self._main_tree_view.setModel(self._active_doc_model)
            self._main_tree_view.expandAll()
            self._main_tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

            proxy_model: Level2ProxyModel = Level2ProxyModel()
            proxy_model.setSourceModel(self._active_doc_model)
            self._item_tree_view.setModel(proxy_model)
            self._item_tree_view.expandAll()
            self._item_tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

            self._detail_tree_view.setModel(None)

            undo_action: QtWidgets.QAction = self._active_undo_stack.createUndoAction(self, "&Undo")
            undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
            self.addAction(undo_action)

            redo_action: QtWidgets.QAction = self._active_undo_stack.createRedoAction(self, "&Redo")
            redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
            self.addAction(redo_action)

    def _new(self, file_name: Optional[str] = None) -> None:
        doc_model: TreeModel = self.create_tree_model(file_name=file_name)
        doc_view: DocumentView = DocumentView(doc_model)
        doc_view.file_name = file_name
        doc_view.update()

        sub_wnd: QtWidgets.QMdiSubWindow = self._mdi_area.addSubWindow(doc_view)
        sub_wnd.showMaximized()

    def new(self) -> None:
        self._new()

    def open(self) -> None:
        file_name: tuple[str, str] = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open file", "./", "Json files (*.json);;All files (*.*)",
            options=QtWidgets.QFileDialog.DontUseNativeDialog | QtWidgets.QFileDialog.DontUseNativeDialog
        )

        QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        if file_name[0]:
            self._new(file_name=file_name[0])
        else:
            print("No file selected")

        QtGui.QGuiApplication.restoreOverrideCursor()

    def _save(self, file_name: str) -> None:
        QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        try:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(self._active_doc_model.to_dict(), f, ensure_ascii=False, indent=4)

            self._active_doc_view.file_name = file_name
            self._active_doc_view.is_modified = False
            self._active_doc_view.update()

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("File saving error")

        QtGui.QGuiApplication.restoreOverrideCursor()

    def save_as(self) -> None:
        file_name: tuple[str, str] = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save file", "./", "Json files (*.json);;All files (*.*)",
            options=QtWidgets.QFileDialog.DontUseNativeDialog | QtWidgets.QFileDialog.DontUseNativeDialog
        )

        if file_name[0]:
            self._save(file_name[0])
        else:
            print("No file selected")

    def save(self) -> None:
        if self._active_doc_view.file_name:
            self._save(self._active_doc_view.file_name)
        else:
            self.save_as()

    def delete_selection(self) -> None:
        current_widget: QtWidgets.QWidget = QtWidgets.QApplication.focusWidget()
        if isinstance(QtWidgets.QApplication.focusWidget(), TreeView):
            selected_indexes: list[QtCore.QModelIndex] = current_widget.selectionModel().selectedIndexes()

            while selected_indexes:
                selected_index: QtCore.QModelIndex = selected_indexes.pop()

                if isinstance(selected_index.model(), QtCore.QSortFilterProxyModel):
                    selected_index: QtCore.QModelIndex = selected_index.model().mapToSource(selected_index)

                if selected_index.column() == 0:
                    tree_item: Optional[TreeItem] = self._active_doc_model.item_from_index(selected_index)
                    if isinstance(tree_item, NodeItem):
                        index: QtCore.QModelIndex = cast(QtCore.QModelIndex, selected_index)
                        self._active_doc_model.removeRow(index.row(), index.parent())


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)

    main_window: MainWindow = MainWindow()

    main_window.show()
    sys.exit(app.exec_())

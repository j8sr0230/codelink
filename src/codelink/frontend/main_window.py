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

from typing import cast, Optional, Union, Callable, Any
import sys
from pathlib import Path
import json
from functools import partial

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.node_factory import NodeFactory
from codelink.backend.document_model import DocumentModel
from codelink.backend.tree_item import TreeItem
from codelink.backend.node_item import NodeItem
from codelink.backend.group_item import GroupItem
from codelink.backend.edge_item import EdgeItem
from codelink.backend.proxy_models import Level2ProxyModel, Level4ProxyModel

from codelink.frontend.tree_view import TreeView
from codelink.frontend.document_view import DocumentView


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._node_factory: NodeFactory = NodeFactory()
        self._active_doc_model: Optional[DocumentModel] = None
        self._active_doc_view: Optional[DocumentView] = None
        self._undo_group: QtWidgets.QUndoGroup = QtWidgets.QUndoGroup()

        # UI
        self.setWindowTitle("CodeLink")
        self.resize(1280, 800)

        self.create_file_menu()
        self.create_edit_menu()
        self.create_nodes_menu()

        self._action_dict: dict[str, QtWidgets.QAction] = {act.text(): act for act in self.actions()}
        self._menu_dict: dict[str, QtWidgets.QAction] = {menu.text(): menu for menu in self.menuWidget().actions()}

        self._mdi_area: QtWidgets.QMdiArea = self.create_mdi_area()
        self._doc_tree_view: TreeView = self.create_doc_tree_view()
        self._item_tree_view: TreeView = self.create_item_tree_view()
        self._detail_tree_view: TreeView = self.create_detail_tree_view()

        self.statusBar().showMessage("Ready ...")

    @staticmethod
    def connect_item_selection(sender: Union[QtWidgets.QTreeView, QtWidgets.QGraphicsView],
                               slot: Callable, enabled: bool = True) -> None:

        def get_signal(sender_obj: QtCore.QObject, signal_name: str) -> Optional[QtCore.QMetaMethod]:
            meta_obj = sender_obj.metaObject()
            for i in range(meta_obj.methodCount()):
                meta_method = meta_obj.method(i)
                if not meta_method.isValid():
                    continue
                if meta_method.methodType() == QtCore.QMetaMethod.Signal and meta_method.name() == signal_name:
                    return meta_method
            return None

        if isinstance(sender, QtWidgets.QTreeView):
            sig: QtCore.QMetaMethod = get_signal(sender.selectionModel(), "selectionChanged")
            if sig and not enabled:
                if sender.selectionModel().isSignalConnected(sig):
                    sender.selectionModel().selectionChanged.disconnect(slot)
            else:
                sender.selectionModel().selectionChanged.connect(slot)

        if isinstance(sender, QtWidgets.QGraphicsView):
            sig: QtCore.QMetaMethod = get_signal(sender, "selection_changed")
            if sig and not enabled:
                if sender.isSignalConnected(sig):
                    sender.selection_changed.disconnect(slot)
            else:
                sender.selection_changed.connect(slot)

    def create_file_menu(self) -> QtWidgets.QMenu:
        file_menu: QtWidgets.QMenu = self.menuBar().addMenu("&File")

        new_action: QtWidgets.QAction = file_menu.addAction("&New")
        new_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.New))
        self.addAction(new_action)
        file_menu.addAction(new_action)
        new_action.triggered.connect(self.on_new)

        open_action: QtWidgets.QAction = file_menu.addAction("&Open")
        open_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Open))
        self.addAction(open_action)
        file_menu.addAction(open_action)
        open_action.triggered.connect(self.on_open)

        save_as_action: QtWidgets.QAction = file_menu.addAction("Save &As")
        save_as_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.SaveAs))
        self.addAction(save_as_action)
        file_menu.addAction(save_as_action)
        save_as_action.triggered.connect(self.on_save_as)
        save_as_action.setEnabled(False)

        save_action: QtWidgets.QAction = file_menu.addAction("&Save")
        save_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Save))
        self.addAction(save_action)
        file_menu.addAction(save_action)
        save_action.triggered.connect(self.on_save)
        save_action.setEnabled(False)

        exit_action: QtWidgets.QAction = file_menu.addAction("E&xit")
        file_menu.addAction(exit_action)
        exit_action.triggered.connect(self.close)

        return file_menu

    def create_edit_menu(self) -> QtWidgets.QMenu:
        edit_menu: QtWidgets.QMenu = self.menuBar().addMenu("&Edit")

        undo_action: QtWidgets.QAction = self._undo_group.createUndoAction(self, "&Undo")
        undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
        self.addAction(undo_action)
        edit_menu.addAction(undo_action)

        redo_action: QtWidgets.QAction = self._undo_group.createRedoAction(self, "&Redo")
        redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
        self.addAction(redo_action)
        edit_menu.addAction(redo_action)

        group_action: QtWidgets.QAction = edit_menu.addAction("&Group")
        self.addAction(group_action)
        edit_menu.addAction(group_action)
        group_action.triggered.connect(self.on_group)
        group_action.setEnabled(False)

        ungroup_action: QtWidgets.QAction = edit_menu.addAction("&Ungroup")
        self.addAction(ungroup_action)
        edit_menu.addAction(ungroup_action)
        ungroup_action.triggered.connect(self.on_ungroup)
        ungroup_action.setEnabled(False)

        del_action: QtWidgets.QAction = edit_menu.addAction("&Delete")
        del_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Delete))
        self.addAction(del_action)
        edit_menu.addAction(del_action)
        del_action.triggered.connect(self.on_delete)
        del_action.setEnabled(False)

        edit_menu.addSeparator()

        pref_action: QtWidgets.QAction = edit_menu.addAction("&Preferences")
        edit_menu.addAction(pref_action)
        pref_action.triggered.connect(lambda: print("Preferences"))

        return edit_menu

    def create_nodes_menu(self) -> QtWidgets.QMenu:
        nodes_menu: QtWidgets.QMenu = self.menuBar().addMenu("&Nodes")
        self.load_nodes(node_factory=self._node_factory, nodes_path="../backend/nodes", nodes_menu=nodes_menu)

        test_action: QtWidgets.QAction = nodes_menu.addAction("&Test Data")
        nodes_menu.addAction(test_action)
        test_action.triggered.connect(self.on_test_data)

        nodes_menu.menuAction().setEnabled(False)
        return nodes_menu

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

    def create_doc_tree_view(self) -> TreeView:
        dock: QtWidgets.QDockWidget = QtWidgets.QDockWidget("Main View", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        doc_tree_view: TreeView = TreeView()
        dock.setWidget(doc_tree_view)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        return doc_tree_view

    def create_item_tree_view(self) -> TreeView:
        dock = QtWidgets.QDockWidget("Item View", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        item_tree_view: TreeView = TreeView()
        dock.setWidget(item_tree_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        return item_tree_view

    def create_detail_tree_view(self) -> TreeView:
        dock = QtWidgets.QDockWidget("Detail View", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        detail_view: TreeView = TreeView()
        dock.setWidget(detail_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        return detail_view

    def load_nodes(self, node_factory: NodeFactory, nodes_path: str, nodes_menu: QtWidgets.QMenu) -> None:
        def add_node(node_cls: str) -> None:
            node: NodeItem = node_factory.create_node(node_cls)
            self._active_doc_model.append_node(node)

        node_factory.load_nodes(str(Path(nodes_path).resolve()))
        for key in node_factory.nodes.keys():
            parent_menu: QtWidgets.QMenu = nodes_menu

            menu_titles: list[str] = key.split(".")[1:]
            pretty_titles: list[str] = [
                menu_title.replace("_", " ").title() for menu_title in menu_titles[:-1]
            ]
            pretty_titles.append(menu_titles[-1])

            for idx, pretty_title in enumerate(pretty_titles):
                if pretty_title not in [action.text() for action in parent_menu.actions()]:
                    if idx < len(menu_titles) - 2:
                        parent_menu: QtWidgets.QMenu = parent_menu.addMenu(pretty_title)
                    elif idx == len(menu_titles) - 1:
                        add_action: QtWidgets.QAction = parent_menu.addAction(pretty_title)
                        add_action.triggered.connect(partial(add_node, key))
                        parent_menu.addAction(add_action)
                else:
                    parent_action: QtWidgets.QAction = parent_menu.actions()[-1]
                    parent_menu: QtWidgets.QMenu = parent_action.menu()

    def update_detail_tree_view(self, index: QtCore.QModelIndex) -> None:
        tree_item: TreeItem = self._active_doc_model.item_from_index(index)
        if tree_item and (
                isinstance(tree_item, NodeItem) and type(tree_item) is not GroupItem
        ):
            proxy: Level4ProxyModel = Level4ProxyModel()
            proxy.setSourceModel(self._active_doc_model)
            self._detail_tree_view.setModel(proxy)
            self._detail_tree_view.setRootIndex(proxy.mapFromSource(index))
            self._detail_tree_view.expandAll()
        else:
            self._detail_tree_view.setModel(None)

    def _on_new(self, file_name: Optional[str] = None) -> None:
        state: Optional[dict[str, Any]] = None
        if file_name:
            try:
                with open(str(Path(file_name).resolve()), "r", encoding="utf-8") as f:
                    state: dict[str, Any] = json.load(f)
            except (FileNotFoundError, json.decoder.JSONDecodeError):
                print("File loading error")

        undo_stack: QtWidgets.QUndoStack = QtWidgets.QUndoStack()
        self._undo_group.addStack(undo_stack)

        doc_model: DocumentModel = DocumentModel(data=state, undo_stack=undo_stack)
        doc_model.file_name = file_name

        doc_view: DocumentView = DocumentView(doc_model)
        doc_model.rowsInserted.connect(doc_view.on_model_rows_inserted)
        cast(QtCore.SignalInstance, doc_model.begin_remove_rows).connect(doc_view.on_model_begin_remove_rows)
        doc_model.dataChanged.connect(doc_view.on_model_data_changed)
        doc_view.update()

        sub_wnd: QtWidgets.QMdiSubWindow = self._mdi_area.addSubWindow(doc_view)
        sub_wnd.showMaximized()

        parent_index: QtCore.QModelIndex = doc_model.nodes_index
        nodes_count: int = doc_model.rowCount(parent_index)
        for i in range(nodes_count):
            doc_view.on_model_rows_inserted(parent_index, i, i)

        parent_index: QtCore.QModelIndex = doc_model.edges_index
        edges_count: int = doc_model.rowCount(parent_index)
        for i in range(edges_count):
            doc_view.on_model_rows_inserted(parent_index, i, i)

        doc_view.model.modified = False
        doc_view.update()

    def on_new(self) -> None:
        self._on_new()

    def on_open(self) -> None:
        file_name: tuple[str, str] = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open file", "./", "Json files (*.json);;All files (*.*)"
        )

        QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        if file_name[0]:
            self._on_new(file_name=file_name[0])
        else:
            print("No file selected")

        QtGui.QGuiApplication.restoreOverrideCursor()

    def _on_save(self, file_name: str) -> None:
        QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        try:
            with open(str(Path(file_name).resolve()), "w", encoding="utf-8") as f:
                json.dump(self._active_doc_model.to_dict(), f, ensure_ascii=False, indent=4)

            self._active_doc_model.file_name = file_name
            self._active_doc_model.modified = False
            self._active_doc_view.update()

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("File saving error")

        QtGui.QGuiApplication.restoreOverrideCursor()

    def on_save_as(self) -> None:
        file_name: tuple[str, str] = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save file", "./", "Json files (*.json);;All files (*.*)"
        )

        if file_name[0]:
            self._on_save(file_name[0])
        else:
            print("No file selected")

    def on_save(self) -> None:
        if self._active_doc_model.file_name:
            self._on_save(self._active_doc_model.file_name)
        else:
            self.on_save_as()

    def on_group(self) -> None:
        proxy: QtCore.QSortFilterProxyModel = self._item_tree_view.model()

        selected_items: list[TreeItem] = []
        for index in self._item_tree_view.selectedIndexes():
            index: QtCore.QModelIndex = index
            selected_items.append(self._active_doc_model.item_from_index(proxy.mapToSource(index)))

        print(selected_items)

        group_item: GroupItem = GroupItem("Custom Group")
        self._active_doc_model.append_node(group_item)
        group_nodes: list[TreeItem] = group_item.child(3).children

        for item in selected_items:
            if isinstance(item, NodeItem):
                parent: TreeItem = item.parent
                parent.children.remove(item)
                group_nodes.append(item)
                # self._active_doc_view.document_gr_view.scene().removeItem(
                #     self._active_doc_view.document_gr_view.graphics_item_from_index(index)
                # )
                #parent_item.remove_child(node_item.row())

        # group_item.append_child(self._active_doc_model.item_from_index(self._active_doc_model.nodes_index))
        # group_item.append_child(self._active_doc_model.item_from_index(self._active_doc_model.edges_index))
        # group_item.append_child(self._active_doc_model.item_from_index(self._active_doc_model.frames_index))

    @staticmethod
    def on_ungroup() -> None:
        print("Ungroup")

    def on_delete(self) -> None:
        proxy: QtCore.QSortFilterProxyModel = self._item_tree_view.model()

        source_indexes: list[QtCore.QPersistentModelIndex] = []
        for index in self._item_tree_view.selectedIndexes():
            index: QtCore.QModelIndex = index
            source_indexes.append(QtCore.QPersistentModelIndex(proxy.mapToSource(index)))

        self._active_doc_model.undo_stack.beginMacro("mass delete")

        for selected_index in source_indexes:
            selected_index: QtCore.QModelIndex = QtCore.QModelIndex(selected_index)
            if selected_index.column() == 0:
                tree_item: Optional[TreeItem] = self._active_doc_model.item_from_index(selected_index)
                if isinstance(tree_item, EdgeItem):
                    index: QtCore.QModelIndex = cast(QtCore.QModelIndex, selected_index)
                    self._active_doc_model.remove_index(index)

        for selected_index in source_indexes:
            selected_index: QtCore.QModelIndex = QtCore.QModelIndex(selected_index)
            if selected_index.column() == 0:
                tree_item: Optional[TreeItem] = self._active_doc_model.item_from_index(selected_index)
                if isinstance(tree_item, NodeItem):
                    index: QtCore.QModelIndex = cast(QtCore.QModelIndex, selected_index)
                    self._active_doc_model.remove_index(index)

        self._active_doc_model.undo_stack.endMacro()

    def on_test_data(self) -> None:
        self._active_doc_model.add_test_data()

    def on_sub_wnd_changed(self, sub_wnd: QtWidgets.QMdiSubWindow) -> None:
        save_as_act: QtWidgets.QAction = self._action_dict.get("Save &As")
        save_act: QtWidgets.QAction = self._action_dict.get("&Save")
        del_act: QtWidgets.QAction = self._action_dict.get("&Delete")
        nodes_act: QtWidgets.QAction = self._menu_dict.get("&Nodes")

        del_act.setEnabled(False)

        if len(self._mdi_area.subWindowList()) > 0 and sub_wnd:
            self._active_doc_view: DocumentView = cast(DocumentView, sub_wnd.widget())
            doc_gr_view: QtWidgets.QGraphicsView = self._active_doc_view.document_gr_view
            cast(QtCore.SignalInstance, doc_gr_view.selection_changed).connect(self.on_doc_gr_view_selection_changed)

            self._active_doc_model: DocumentModel = self._active_doc_view.model
            self._undo_group.setActiveStack(self._active_doc_model.undo_stack)

            self._doc_tree_view.setModel(self._active_doc_model)
            self._doc_tree_view.selectionModel().selectionChanged.connect(self.on_doc_tree_selection_changed)
            self._doc_tree_view.expandToDepth(1)

            proxy_model: Level2ProxyModel = Level2ProxyModel()
            proxy_model.setSourceModel(self._active_doc_model)
            self._item_tree_view.setModel(proxy_model)
            self._item_tree_view.selectionModel().selectionChanged.connect(self.on_item_tree_selection_changed)
            self._item_tree_view.expandAll()

            self._detail_tree_view.setModel(None)

            save_as_act.setEnabled(True)
            save_act.setEnabled(True)
            nodes_act.setEnabled(True)

            self.statusBar().showMessage(self._active_doc_model.get_pretty_file_name())

        else:
            self._doc_tree_view.setModel(None)
            self._item_tree_view.setModel(None)
            self._detail_tree_view.setModel(None)

            save_as_act.setEnabled(False)
            save_act.setEnabled(False)
            nodes_act.setEnabled(False)

            self.statusBar().clearMessage()

    # noinspection PyUnusedLocal
    def on_doc_tree_selection_changed(self, current: QtCore.QItemSelection, previous: QtCore.QItemSelection) -> None:
        del_act: QtWidgets.QAction = self._action_dict.get("&Delete")
        del_act.setEnabled(False)
        group_act: QtWidgets.QAction = self._action_dict.get("&Group")
        group_act.setEnabled(False)
        ungroup_act: QtWidgets.QAction = self._action_dict.get("&Ungroup")
        ungroup_act.setEnabled(False)

        proxy: QtCore.QSortFilterProxyModel = self._item_tree_view.model()

        source_selection: QtCore.QItemSelection = QtCore.QItemSelection()
        for index in self._doc_tree_view.selectedIndexes():
            del_act.setEnabled(True)
            group_act.setEnabled(True)
            index: QtCore.QModelIndex = index
            source_selection.select(index, index)

        self.connect_item_selection(self._item_tree_view, self.on_item_tree_selection_changed, False)
        proxy_selection: QtCore.QItemSelection = proxy.mapSelectionFromSource(source_selection)
        self._item_tree_view.selectionModel().select(proxy_selection, QtCore.QItemSelectionModel.ClearAndSelect)
        self.connect_item_selection(self._item_tree_view, self.on_item_tree_selection_changed, True)

        doc_gr_view: QtWidgets.QGraphicsView = self._active_doc_view.document_gr_view
        self.connect_item_selection(doc_gr_view, self.on_doc_gr_view_selection_changed, False)
        self._active_doc_view.document_gr_view.select(source_selection)
        self.connect_item_selection(doc_gr_view, self.on_doc_gr_view_selection_changed, True)

        if len(source_selection.indexes()) > 0:
            self.update_detail_tree_view(cast(QtCore.QModelIndex, source_selection.indexes()[0]))

    # noinspection PyUnusedLocal
    def on_item_tree_selection_changed(self, current: QtCore.QItemSelection, previous: QtCore.QItemSelection) -> None:
        del_act: QtWidgets.QAction = self._action_dict.get("&Delete")
        del_act.setEnabled(False)
        group_act: QtWidgets.QAction = self._action_dict.get("&Group")
        group_act.setEnabled(False)
        ungroup_act: QtWidgets.QAction = self._action_dict.get("&Ungroup")
        ungroup_act.setEnabled(False)

        proxy: QtCore.QSortFilterProxyModel = self._item_tree_view.model()

        proxy_selection: QtCore.QItemSelection = QtCore.QItemSelection()
        for index in self._item_tree_view.selectedIndexes():
            del_act.setEnabled(True)
            group_act.setEnabled(True)
            index: QtCore.QModelIndex = index
            proxy_selection.select(index, index)

        self.connect_item_selection(self._doc_tree_view, self.on_doc_tree_selection_changed, False)
        source_selection: QtCore.QItemSelection = proxy.mapSelectionToSource(proxy_selection)
        self._doc_tree_view.selectionModel().select(source_selection, QtCore.QItemSelectionModel.ClearAndSelect)
        self.connect_item_selection(self._doc_tree_view, self.on_doc_tree_selection_changed, True)

        doc_gr_view: QtWidgets.QGraphicsView = self._active_doc_view.document_gr_view
        self.connect_item_selection(doc_gr_view, self.on_doc_gr_view_selection_changed, False)
        self._active_doc_view.document_gr_view.select(source_selection)
        self.connect_item_selection(doc_gr_view, self.on_doc_gr_view_selection_changed, True)

        if len(source_selection.indexes()) > 0:
            self.update_detail_tree_view(cast(QtCore.QModelIndex, source_selection.indexes()[0]))

    def on_doc_gr_view_selection_changed(self, source_selection: QtCore.QItemSelection) -> None:
        del_act: QtWidgets.QAction = self._action_dict.get("&Delete")
        del_act.setEnabled(False)
        group_act: QtWidgets.QAction = self._action_dict.get("&Group")
        group_act.setEnabled(False)
        ungroup_act: QtWidgets.QAction = self._action_dict.get("&Ungroup")
        ungroup_act.setEnabled(False)

        self.connect_item_selection(self._doc_tree_view, self.on_doc_tree_selection_changed, False)
        self._doc_tree_view.selectionModel().select(source_selection, QtCore.QItemSelectionModel.ClearAndSelect)
        self.connect_item_selection(self._doc_tree_view, self.on_doc_tree_selection_changed, True)

        self.connect_item_selection(self._item_tree_view, self.on_item_tree_selection_changed, False)
        proxy: QtCore.QSortFilterProxyModel = cast(QtCore.QSortFilterProxyModel, self._item_tree_view.model())
        proxy_selection: QtCore.QItemSelection = proxy.mapSelectionFromSource(source_selection)
        self._item_tree_view.selectionModel().select(proxy_selection, QtCore.QItemSelectionModel.ClearAndSelect)
        self.connect_item_selection(self._item_tree_view, self.on_item_tree_selection_changed, True)

        if len(source_selection.indexes()) > 0:
            del_act.setEnabled(True)
            group_act.setEnabled(True)
            self.update_detail_tree_view(cast(QtCore.QModelIndex, source_selection.indexes()[0]))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self._mdi_area.closeAllSubWindows()
        if len(self._mdi_area.subWindowList()) > 0:
            event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    main_window: MainWindow = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

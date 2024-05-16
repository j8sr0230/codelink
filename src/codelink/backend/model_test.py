from typing import cast, Any
import os
import sys
import json
from pathlib import Path
import importlib.util
import inspect

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.user_roles import UserRoles
from codelink.backend.tree_model import TreeModel
from codelink.backend.node_item import NodeItem
from codelink.backend.properties.integer_property_item import IntegerPropertyItem
from codelink.backend.edge_item import EdgeItem
from codelink.backend.delegates import TreeViewDelegate


def load_nodes_from_path(path: str, menu: QtWidgets.QMenu, parent: QtWidgets.QWidget) -> None:
    try:
        sub_paths: list[str] = os.listdir(path)
        for sub_path in sub_paths:
            abs_sub_path: str = os.path.join(path, sub_path)
            path_items: list[str] = abs_sub_path.split(os.sep)

            if len(path_items) > 0 and not path_items[-1].startswith("__"):
                if os.path.isdir(abs_sub_path):
                    sub_menu: QtWidgets.QMenu = QtWidgets.QMenu(path_items[-1].replace("_", " ").title())
                    menu.addMenu(sub_menu)
                    load_nodes_from_path(abs_sub_path, sub_menu, parent)
                else:
                    module_name: str = path_items[-1][:-3]
                    module_spec = importlib.util.spec_from_file_location(path_items[-1][:-3], abs_sub_path)
                    module = importlib.util.module_from_spec(module_spec)
                    sys.modules[module_name] = module
                    module_spec.loader.exec_module(module)

                    for name, item in inspect.getmembers(module):
                        if inspect.isclass(item):
                            if str(item).__contains__(module.__name__):
                                # noinspection PyUnusedLocal
                                cls: type = item
                                action: QtWidgets.QAction = QtWidgets.QAction(name, parent)
                                action.triggered.connect(lambda: model.append_node(cast(NodeItem, cls())))
                                menu.addAction(action)
    except FileNotFoundError as e:
        print(e)


if __name__ == "__main__":
    # Setup tree model
    model: TreeModel = TreeModel()
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

    # Setup ui
    # Main window
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    main_window: QtWidgets.QMainWindow = QtWidgets.QMainWindow()
    main_window.setWindowTitle("Main Window")

    menu_bar: QtWidgets.QMenuBar = main_window.menuBar()
    nodes_menu: QtWidgets.QMenu = menu_bar.addMenu("Nodes")
    load_nodes_from_path(str(Path("./nodes").resolve()), nodes_menu, main_window)

    main_undo_action: QtWidgets.QAction = model.undo_stack.createUndoAction(main_window, "Undo")
    main_undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
    main_window.addAction(main_undo_action)
    main_redo_action: QtWidgets.QAction = model.undo_stack.createRedoAction(main_window, "Redo")
    main_redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
    main_window.addAction(main_redo_action)

    main_tree_view: QtWidgets.QTreeView = QtWidgets.QTreeView()
    main_tree_view.setModel(model)
    main_tree_view.setAlternatingRowColors(True)
    main_tree_view.setItemDelegate(TreeViewDelegate())

    model.rowsInserted.connect(
        lambda: main_tree_view.expandRecursively(QtCore.QModelIndex())
    )

    main_window.setCentralWidget(main_tree_view)
    main_window.show()

    # Inspection window
    inspection_window: QtWidgets.QMainWindow = QtWidgets.QMainWindow()
    inspection_window.setWindowTitle("Inspection Window")
    inspection_undo_action: QtWidgets.QAction = model.undo_stack.createUndoAction(inspection_window, "Undo")
    inspection_undo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Undo))
    inspection_window.addAction(main_undo_action)
    inspection_redo_action: QtWidgets.QAction = model.undo_stack.createRedoAction(inspection_window, "Redo")
    inspection_redo_action.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Redo))
    inspection_window.addAction(main_redo_action)

    second_tree_view: QtWidgets.QTreeView = QtWidgets.QTreeView()
    second_tree_view.setModel(model)
    second_tree_view.setIndentation(0)
    second_tree_view.setAlternatingRowColors(True)
    second_tree_view.setItemDelegate(TreeViewDelegate())

    main_tree_view.selectionModel().selectionChanged.connect(
        lambda current, previous: second_tree_view.setRootIndex(cast(QtCore.QItemSelection, current).indexes()[0])
    )

    model.rowsInserted.connect(
        lambda: second_tree_view.expandRecursively(QtCore.QModelIndex())
    )

    inspection_window.setCentralWidget(second_tree_view)
    inspection_window.show()

    # Populate tree model with tree items
    node_item: NodeItem = NodeItem("Node")
    node_item_idx: QtCore.QModelIndex = model.append_node(node_item)

    print(model.data(node_item_idx, UserRoles.POS))
    model.setData(node_item_idx, [5, 5], UserRoles.POS)
    print(model.data(node_item_idx, UserRoles.POS))

    print("Outputs index:", model.index_from_key("Outputs", node_item_idx))
    print()

    x_component: IntegerPropertyItem = IntegerPropertyItem(key="X", value=5)
    model.append_item(x_component, model.index(0, 0, node_item_idx))
    z_component: IntegerPropertyItem = IntegerPropertyItem(key="Z", value=99)
    model.append_item(z_component, model.index(0, 0, node_item_idx))
    y_component: IntegerPropertyItem = IntegerPropertyItem(key="Y", value=0)
    model.insert_item(1, y_component, model.index(0, 0, node_item_idx))

    edge: EdgeItem = EdgeItem(x_component.uuid, y_component.uuid)
    edge_idx: QtCore.QModelIndex = model.append_item(edge, model.edges_index)

    # (De-)Serialisation
    print(model)
    # with open("./data.json", "w", encoding="utf-8") as f:
    #     json.dump(model.to_dict(), f, ensure_ascii=False, indent=4)

    with open("./data.json", "r", encoding="utf-8") as f:
        deserialized: dict[str, Any] = json.load(f)
        restored_model: TreeModel = TreeModel(deserialized)
        print(restored_model)

        restored_nodes_idx: QtCore.QModelIndex = restored_model.index(0, 0, QtCore.QModelIndex())
        restored_node_1_idx: QtCore.QModelIndex = restored_model.index(0, 0, restored_nodes_idx)
        print(restored_node_1_idx.data(UserRoles.POS))

        restored_edges_idx: QtCore.QModelIndex = restored_model.index(1, 0, QtCore.QModelIndex())
        restored_edge_1_idx: QtCore.QModelIndex = restored_model.index(0, 0, restored_edges_idx)
        restored_source: IntegerPropertyItem = cast(
            IntegerPropertyItem, restored_model.data(restored_edge_1_idx, UserRoles.SRC)
        )
        restored_destination: IntegerPropertyItem = cast(
            IntegerPropertyItem, restored_model.data(restored_edge_1_idx, UserRoles.DEST)
        )
        print(
            restored_source.key, ":", restored_source.value, "->",
            restored_destination.key, ":", restored_destination.value
        )

    sys.exit(app.exec_())

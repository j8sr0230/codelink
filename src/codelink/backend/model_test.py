from typing import cast, Any
import os
import sys
import json
import pathlib
import importlib
import inspect

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.user_roles import UserRoles
from codelink.backend.tree_model import TreeModel
from codelink.backend.node_item_ import NodeItem
from codelink.backend.properties.integer_property_item import IntegerPropertyItem
from codelink.backend.edge_item import EdgeItem
from codelink.backend.delegates import TreeViewDelegate

from codelink.backend.nodes.node_package.node_category.node_sub_category_1.test_node_item import TestNodeItem


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

    model.append_node(TestNodeItem("Test Node"))

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

        def traverse_nodes_dir(directory: str) -> None:
            sub_dir: list[str] = os.listdir(directory)
            print(sub_dir)
            for sub in sub_dir:
                if os.path.isdir(sub):
                    traverse_nodes_dir(os.path.join(directory, sub))
                else:
                    pass  # print(sub)

        traverse_nodes_dir("." + os.sep + "nodes")

        # print()
        # root: str = "nodes"
        # menus: dict = dict()
        # for dir_path, dir_names, file_names in os.walk(root):
        #     for file_name in file_names:
        #         if file_name.endswith(".py") and not file_name.startswith("__init__"):
        #             menu_path: str = dir_path[len(root) + 1:]
        #             print(menu_path.split(os.sep))
        #
        #             file_path: str = os.path.join("codelink", "backend", dir_path, file_name)
        #             module_path: str = file_path[:-3].replace(os.sep, ".")
        #             module = importlib.import_module(module_path)
        #             for name, obj in inspect.getmembers(module):
        #                 if inspect.isclass(obj):
        #                     if str(obj).__contains__(module.__name__):
        #                         class_name: str = str(obj).split(".")[-1][:-2]
        #                         print(class_name)



    sys.exit(app.exec_())

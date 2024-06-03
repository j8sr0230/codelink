from typing import cast, Any
import sys
import json
from functools import partial
from pathlib import Path

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.user_roles import UserRoles
from codelink.backend.node_factory import NodeFactory
from codelink.backend.tree_model import TreeModel
from codelink.backend.node_item import NodeItem
from codelink.backend.properties.integer_property_item import IntegerPropertyItem
from codelink.backend.edge_item import EdgeItem
from codelink.backend.delegates import TreeViewDelegate


def populate_menu(node_factory: NodeFactory, data_model: TreeModel, menu: QtWidgets.QMenu,
                  parent: QtWidgets.QWidget) -> None:

    def create_node(node_cls: str) -> None:
        node: NodeItem = node_factory.create_node(node_cls)
        data_model.append_node(node)

    actions: list[QtWidgets.QAction] = []

    for key in node_factory.nodes.keys():
        parent_menu: QtWidgets.QMenu = menu

        menu_titles: list[str] = key.split(".")[1:]
        pretty_titles: list[str] = [menu_title.replace("_", " ").title() for menu_title in menu_titles[:-1]]
        pretty_titles.append(menu_titles[-1])

        for idx, pretty_title in enumerate(pretty_titles):
            if pretty_title not in [action.text() for action in parent_menu.actions()]:
                if idx < len(menu_titles) - 2:
                    parent_menu: QtWidgets.QMenu = parent_menu.addMenu(pretty_title)
                elif idx == len(menu_titles) - 1:
                    add_action: QtWidgets.QAction = QtWidgets.QAction(pretty_title, parent)
                    add_action.setData(key)
                    actions.append(add_action)
                    parent_menu.addAction(add_action)
            else:
                parent_action: QtWidgets.QAction = parent_menu.actions()[-1]
                parent_menu: QtWidgets.QMenu = parent_action.menu()

    for action in actions:
        action.triggered.connect(partial(create_node, action.data()))


if __name__ == "__main__":
    # Load nodes
    node_fac: NodeFactory = NodeFactory()
    node_fac.load_nodes(str(Path("../backend/nodes").resolve()))

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
    nodes_menu: QtWidgets.QMenu = menu_bar.addMenu("&Nodes")
    populate_menu(node_fac, model, nodes_menu, main_window)

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
    node_item: NodeItem = node_fac.create_node(list(node_fac.nodes.keys())[0])
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

    with open("../backend/data.json", "r", encoding="utf-8") as f:
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
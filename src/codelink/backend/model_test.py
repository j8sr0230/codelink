from typing import cast, Any
import sys
import json

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from tree_model import TreeModel
from tree_item import TreeItem
from base_item import BaseItem
from backend.node_item import NodeItem
from seperator_item import SeperatorItem
from property_item import PropertyItem
from integer_property_item import IntegerPropertyItem
from backend.edge_item import EdgeItem

from delegates import TreeViewDelegate


UUID_ROLE: int = QtCore.Qt.UserRole + 1


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
            "Changed at:", top_left_idx.row(), top_left_idx.column(), "to:", top_left_idx.data())
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
    node_sep: SeperatorItem = SeperatorItem(key="Nodes")
    nodes_idx: QtCore.QModelIndex = model.append_item(node_sep, QtCore.QModelIndex())

    node_item_1: NodeItem = NodeItem("Test Node")
    node_item_1_idx: QtCore.QModelIndex = model.append_item(node_item_1, nodes_idx)

    vector_item: PropertyItem = PropertyItem(key="Vector", value="[...]")
    vect_idx: QtCore.QModelIndex = model.append_item(vector_item, nodes_idx)

    x_component: IntegerPropertyItem = IntegerPropertyItem(key="X", value=5)
    model.append_item(x_component, vect_idx)

    z_component: IntegerPropertyItem = IntegerPropertyItem(key="Z", value=99)
    model.append_item(z_component, vect_idx)

    y_component: IntegerPropertyItem = IntegerPropertyItem(key="Y", value=0)
    model.insert_item(1, y_component, vect_idx)

    edge_sep: SeperatorItem = SeperatorItem(key="Edges")
    edges_idx: QtCore.QModelIndex = model.append_item(edge_sep, QtCore.QModelIndex())
    edge_1: EdgeItem = EdgeItem(x_component.uuid, y_component.uuid)
    edge_1_idx: QtCore.QModelIndex = model.append_item(edge_1, edges_idx)
    edge_2: EdgeItem = EdgeItem(y_component.uuid, vector_item.uuid)
    edge_2_idx: QtCore.QModelIndex = model.append_item(edge_2, edges_idx)

    frame_sep: SeperatorItem = SeperatorItem(key="Frames")
    frame_idx: QtCore.QModelIndex = model.append_item(frame_sep, QtCore.QModelIndex())

    # (De-)Serialisation
    print(model)
    # with open("./data.json", "w", encoding="utf-8") as f:
    #     json.dump(model.to_dict(), f, ensure_ascii=False, indent=4)

    with open("./data.json", "r", encoding="utf-8") as f:
        deserialized: dict[str, Any] = json.load(f)
        restored_model: TreeModel = TreeModel(deserialized)
        print(restored_model)

        restored_node_idx: QtCore.QModelIndex = restored_model.index(0, 0, QtCore.QModelIndex())
        restored_vector_idx: QtCore.QModelIndex = restored_model.index(1, 0, restored_node_idx)
        restored_z_idx: QtCore.QModelIndex = restored_model.index(2, 0, restored_vector_idx)
        restored_z_uuid: str = restored_model.data(restored_z_idx, UUID_ROLE)
        restored_item: BaseItem = cast(BaseItem, restored_model.item_from_uuid(restored_z_uuid))
        print(restored_item.key, restored_item.value)

        restored_edges_idx: QtCore.QModelIndex = restored_model.index(1, 0, QtCore.QModelIndex())
        restored_edge_1_idx: QtCore.QModelIndex = restored_model.index(0, 0, restored_edges_idx)
        restored_edge_1: TreeItem = model.item_from_index(restored_edge_1_idx)
        restored_edge_1: EdgeItem = cast(EdgeItem, restored_edge_1)
        restored_source: IntegerPropertyItem = cast(
            IntegerPropertyItem, restored_model.item_from_uuid(restored_edge_1.source_uuid)
        )
        restored_destination: IntegerPropertyItem = cast(
            IntegerPropertyItem, restored_model.item_from_uuid(restored_edge_1.destination_uuid)
        )
        print(restored_edge_1)
        print(restored_destination)
        print(
            restored_source.key, ":", restored_source.value, "->",
            restored_destination.key, ":", restored_destination.value
        )

        restored_edge_2_idx: QtCore.QModelIndex = restored_model.index(1, 0, restored_edges_idx)
        restored_edge_2: TreeItem = model.item_from_index(restored_edge_2_idx)
        restored_edge_2: EdgeItem = cast(EdgeItem, restored_edge_2)
        restored_source: IntegerPropertyItem = cast(
            IntegerPropertyItem, restored_model.item_from_uuid(restored_edge_2.source_uuid)
        )
        restored_destination: BaseItem = cast(BaseItem, restored_model.item_from_uuid(restored_edge_2.destination_uuid))
        print(restored_edge_1)
        print(
            restored_source.key, ":", restored_source.value, "->",
            restored_destination.key, ":", restored_destination.value
        )

    sys.exit(app.exec_())

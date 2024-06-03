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
        self.setWindowTitle("CodeLink")

        # Load nodes
        self._node_fac: NodeFactory = NodeFactory()
        self._node_fac.load_nodes(str(Path("../backend/nodes").resolve()))

        self._model: TreeModel = TreeModel()
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

        self._nodes_menu: QtWidgets.QMenu = self.menuBar().addMenu("&Nodes")
        self.populate_menu(self._node_fac, self._model, self._nodes_menu, self)

        self._graphics_view: QtWidgets.QGraphicsView = QtWidgets.QGraphicsView()
        self._graphics_scene: QtWidgets.QGraphicsScene = QtWidgets.QGraphicsScene()
        self._graphics_view.setScene(self._graphics_scene)
        self._graphics_scene.addRect(
            QtCore.QRectF(-100, -50, 200, 50),
            QtGui.QPen("#000"),
            QtGui.QBrush("#fff")
        )
        self.setCentralWidget(self._graphics_view)

        self.create_dock_windows()


    @staticmethod
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

    def create_dock_windows(self):
        dock: QtWidgets.QDockWidget = QtWidgets.QDockWidget("Main Tree", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        mein_tree_view: TreeView = TreeView()
        mein_tree_view.setModel(self._model)
        self._model.rowsInserted.connect(
            lambda: mein_tree_view.expandRecursively(QtCore.QModelIndex())
        )

        dock.setWidget(mein_tree_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

        dock = QtWidgets.QDockWidget("Inspection", self)
        inspection_tree_view: TreeView = TreeView()
        inspection_tree_view.setModel(self._model)
        inspection_tree_view.setIndentation(0)

        mein_tree_view.selectionModel().selectionChanged.connect(
            lambda current, previous: inspection_tree_view.setRootIndex(cast(QtCore.QItemSelection, current).indexes()[0])
        )

        self._model.rowsInserted.connect(
            lambda: inspection_tree_view.expandRecursively(QtCore.QModelIndex())
        )

        dock.setWidget(inspection_tree_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
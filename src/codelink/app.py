import os
import sys

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from app_style import APP_STYLE
from node_item import NodeItem
from editor_scene import EditorScene
from editor_widget import EditorWidget


if __name__ == "__main__":
    QtCore.QDir.addSearchPath("icon", os.path.abspath(os.path.dirname(__file__)))

    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    editor_scene: EditorScene = EditorScene()
    editor_widget: EditorWidget = EditorWidget()
    editor_widget.setStyleSheet(APP_STYLE)

    editor_widget.setScene(editor_scene)
    editor_widget.resize(1200, 600)
    editor_widget.show()

    node_1 = NodeItem()
    node_1.setPos(QtCore.QPointF(31600, 31800))
    editor_scene.add_node(node_1)

    node_2 = NodeItem()
    node_2.setPos(QtCore.QPointF(32200, 32050))
    editor_scene.add_node(node_2)

    node_3 = NodeItem()
    node_3.setPos(QtCore.QPointF(31900, 32100))
    editor_scene.add_node(node_3)

    sys.exit(app.exec_())

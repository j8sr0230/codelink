import os
import sys

import PySide2.QtCore as QtCore

import FreeCADGui

from app_style import MAIN_STYLE
from node_item import NodeItem
from graph_scene import GraphScene
from editor_widget import EditorWidget


if __name__ == "__main__":
    if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
        sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    QtCore.QDir.addSearchPath("icon", os.path.abspath(os.path.dirname(__file__)))

    fc_wnd = FreeCADGui.getMainWindow()
    editor_scene: GraphScene = GraphScene()
    editor_widget: EditorWidget = EditorWidget(parent=fc_wnd)
    editor_widget.setStyleSheet(MAIN_STYLE)

    editor_widget.setScene(editor_scene)
    editor_widget.resize(1200, 600)
    fc_wnd.node_editor = editor_widget
    fc_wnd.node_editor.show()

    node_1 = NodeItem()
    node_1.setPos(QtCore.QPointF(31600, 31800))
    editor_scene.add_node(node_1)

    node_2 = NodeItem()
    node_2.setPos(QtCore.QPointF(32200, 32050))
    editor_scene.add_node(node_2)

    node_3 = NodeItem()
    node_3.setPos(QtCore.QPointF(31900, 32100))
    editor_scene.add_node(node_3)

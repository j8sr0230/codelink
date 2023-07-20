import os
import sys

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

import FreeCADGui

from app_style import MAIN_STYLE
from node_item import NodeItem
from dag_scene import DAGScene
from editor_widget import EditorWidget


if __name__ == "__main__":
    if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
        sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    QtCore.QDir.addSearchPath("icon", os.path.abspath(os.path.dirname(__file__)))

    fc_wnd = FreeCADGui.getMainWindow()

    undo_stack: QtWidgets.QUndoStack = QtWidgets.QUndoStack()

    editor_scene: DAGScene = DAGScene(undo_stack)
    editor_widget: EditorWidget = EditorWidget(undo_stack, parent=fc_wnd)
    editor_widget.setStyleSheet(MAIN_STYLE)

    editor_widget.setScene(editor_scene)
    editor_widget.resize(1200, 600)
    fc_wnd.node_editor = editor_widget
    fc_wnd.node_editor.show()

    node_1 = NodeItem(undo_stack)
    node_1.setPos(QtCore.QPointF(31600, 31800))
    editor_scene.add_node(node_1)

    node_2 = NodeItem(undo_stack)
    node_2.setPos(QtCore.QPointF(32200, 32050))
    editor_scene.add_node(node_2)

    node_3 = NodeItem(undo_stack)
    node_3.setPos(QtCore.QPointF(31900, 32100))
    editor_scene.add_node(node_3)

import os
import sys

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from app_style import MAIN_STYLE
from node_item import NodeItem
from dag_scene import DAGScene
from editor_widget import EditorWidget


if __name__ == "__main__":
    QtCore.QDir.addSearchPath("icon", os.path.abspath(os.path.dirname(__file__)))

    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    # app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    undo_stack: QtWidgets.QUndoStack = QtWidgets.QUndoStack(app)

    # open_gl_wdg: QtWidgets.QOpenGLWidget = QtWidgets.QOpenGLWidget()

    editor_scene: DAGScene = DAGScene(undo_stack)
    editor_widget: EditorWidget = EditorWidget(undo_stack)
    editor_widget.setStyleSheet(MAIN_STYLE)

    # editor_widget.setViewport(open_gl_wdg)
    editor_widget.setScene(editor_scene)
    editor_widget.resize(1200, 600)
    editor_widget.show()

    # node_1 = NodeItem(undo_stack)
    # node_1.setPos(QtCore.QPointF(31600, 31800))
    # editor_scene.add_node(node_1)
    #
    # node_2 = NodeItem(undo_stack)
    # node_2.setPos(QtCore.QPointF(32200, 32050))
    # editor_scene.add_node(node_2)
    #
    # node_3 = NodeItem(undo_stack)
    # node_3.setPos(QtCore.QPointF(31900, 32100))
    # editor_scene.add_node(node_3)

    for i in range(25):
        for j in range(20):
            node = NodeItem(undo_stack)
            node.setPos(QtCore.QPointF(0 + i * 200, 0 + j * 200))
            editor_scene.add_node(node)

    editor_widget.fit_in_content()

    sys.exit(app.exec_())

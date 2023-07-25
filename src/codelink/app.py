import os
import sys

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from app_style import MAIN_STYLE
from editor_widget import EditorWidget
from dag_scene import DAGScene
from node_item import NodeItem


def main() -> None:
    QtCore.QDir.addSearchPath("icon", os.path.abspath(os.path.dirname(__file__)))

    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    # app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    undo_stack: QtWidgets.QUndoStack = QtWidgets.QUndoStack()

    editor_scene: DAGScene = DAGScene(undo_stack)
    editor_widget: EditorWidget = EditorWidget(undo_stack)
    editor_widget.setStyleSheet(MAIN_STYLE)

    editor_widget.setScene(editor_scene)
    editor_widget.resize(1200, 600)
    editor_widget.show()

    for i in range(5):
        for j in range(5):
            node = NodeItem(undo_stack)
            node.setPos(QtCore.QPointF(32000 + i * 200, 32000 + j * 200))
            editor_scene.add_node(node)

    editor_widget.fit_in_content()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

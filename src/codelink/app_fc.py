import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

import FreeCADGui

from path_loader import *
from app_style import MAIN_STYLE
from editor_widget import EditorWidget
from dag_scene import DAGScene
from nodes.scalar_math import ScalarMath


def main() -> None:
    if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
        sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    QtCore.QDir.addSearchPath("icon", os.path.abspath(os.path.dirname(__file__)))

    fc_wnd = FreeCADGui.getMainWindow()

    undo_stack: QtWidgets.QUndoStack = QtWidgets.QUndoStack()
    undo_stack.clear()

    editor_scene: DAGScene = DAGScene(undo_stack)
    editor_widget: EditorWidget = EditorWidget(undo_stack, parent=fc_wnd)
    editor_widget.setStyleSheet(MAIN_STYLE)

    editor_widget.setScene(editor_scene)
    editor_widget.resize(1200, 600)
    fc_wnd.node_editor = editor_widget
    fc_wnd.node_editor.show()
    editor_widget.show()

    for i in range(5):
        for j in range(5):
            node = ScalarMath(undo_stack)
            node.setPos(QtCore.QPointF(32000 + i * 200, 32000 + j * 200))
            editor_scene.add_node(node)

    editor_widget.fit_in_content()


if __name__ == "__main__":
    main()

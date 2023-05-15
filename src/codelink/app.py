import os
import sys
import json

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem
from editor_scene import EditorScene
from editor_widget import EditorWidget


if __name__ == "__main__":
    # if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
    #     sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    QtCore.QDir.addSearchPath("icon", os.path.abspath(os.path.dirname(__file__)))

    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    node_editor_scene: EditorScene = EditorScene()
    node_editor_widget: EditorWidget = EditorWidget()

    node_editor_widget.setScene(node_editor_scene)
    node_editor_widget.resize(1200, 600)
    node_editor_widget.show()

    node_1 = NodeItem()
    node_1.setPos(QtCore.QPointF(31600, 31800))
    node_editor_scene.add_node(node_1)

    node_2 = NodeItem()
    node_2.setPos(QtCore.QPointF(32200, 32050))
    node_editor_scene.add_node(node_2)

    node_3 = NodeItem()
    node_3.setPos(QtCore.QPointF(31900, 32100))
    node_editor_scene.add_node(node_3)

    # with open("graph.json", 'w', encoding='utf8') as json_file:
    #     json.dump(node_editor_scene.serialize_nodes(), json_file, indent=4)
    #
    # # for node in node_editor_scene.nodes:
    # #     node_editor_scene.remove_node(node)
    #
    # with open("graph.json", 'r', encoding='utf8') as json_file:
    #     nodes_dict: list[dict] = json.load(json_file)
    #     node_editor_scene.deserialize_nodes(nodes_dict)

    sys.exit(app.exec_())

import os
import sys
import pickle

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

    # file_path: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "my_graph.cl")
    # pickle.dump(node_1, open(file_path, "wb"))
    # node_1_copy: NodeItem = pickle.load(open(file_path, 'rb'))
    # node_editor_scene.add_node(node_1_copy)

    # Test NodesModel
    # nodes_model: NodesModel = NodesModel(nodes=[
    #     {"class_name": "BaseNode", "node_name": "Add", "node_color": "red", "node_collapsed": "False",
    #      "node_pos_x": "0", "node_pos_y": "0"},
    #     {"class_name": "BaseNode", "node_name": "Sub", "node_color": "green", "node_collapsed": "False",
    #      "node_pos_x": "10", "node_pos_y": "10"}
    # ])

    # file_path: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "nodes.pkl")
    # # pickle.dump(nodes_model.nodes, open(file_path, "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    # loaded_nodes_data: list[dict] = pickle.load(open(file_path, 'rb'))
    # loaded_model_model: NodesModel = NodesModel(nodes=loaded_nodes_data)
    #
    # loaded_model_model.dataChanged.connect(lambda top_left_idx, bottom_right_idx, roles:
    #                                        print(loaded_model_model.nodes[top_left_idx.row()]))
    # loaded_model_model.dataChanged.connect(lambda top_left_idx, bottom_right_idx, roles:
    #                                        pickle.dump(
    #                                            loaded_model_model.nodes, open(file_path, "wb"),
    #                                            protocol=pickle.HIGHEST_PROTOCOL)
    #                                        )
    #
    # nodes_view: QtWidgets.QTableView = QtWidgets.QTableView()
    # nodes_view.setModel(loaded_model_model)
    # nodes_view.show()

    sys.exit(app.exec_())

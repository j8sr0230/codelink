from typing import Any, Optional

from PySide2.QtCore import Qt, QObject, QAbstractListModel, QModelIndex


class NodeGraph(QAbstractListModel):
    def __init__(self, parent: Optional[QObject] = None, nodes: Optional[list] = None) -> None:
        super().__init__(parent)
        if nodes is None:
            nodes = []
        self.nodes = nodes

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            node = self.nodes[index.row()]
            return node

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.nodes)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            return "Nodes"
        else:
            return None


if __name__ == "__main__":
    node_graph: NodeGraph = NodeGraph()
    print(isinstance(node_graph, QAbstractListModel))

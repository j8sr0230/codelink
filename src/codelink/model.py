from typing import Any, Optional

from PySide2.QtCore import Qt, QObject, QAbstractListModel, QModelIndex


class NodeGraph(QAbstractListModel):
    def __init__(self, parent: Optional[QObject] = None, nodes: Optional[list] = None) -> None:
        super().__init__(parent)
        if nodes is None:
            nodes = []
        self.nodes = nodes

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            return "Nodes"
        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if index.isValid() and (role == Qt.DisplayRole):
            return self.nodes[index.row()]
        else:
            return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if (role == Qt.EditRole) and index.isValid() and (0 <= index.row() < len(self.nodes)):
            self.nodes[index.row()] = value
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    # def insertRows(self, row, count, parent=QModelIndex()):
    #     #
    #     #     self.beginInsertRows(QModelIndex(), row, row + count - 1)
    #     #     self.__data[row:row] = [''] * count
    #     #     self.endInsertRows()
    #     #     return True

    # def removeRows(self, row, count, parent=QModelIndex()):
    #     self.beginRemoveRows(QModelIndex(), row, row + count - 1)
    #     del self.__data[row:row + count]
    #     self.endRemoveRows()
    #     return True

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return len(self.nodes)
        else:
            return 0

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)

        if index.isValid():
            flags = flags | Qt.ItemIsEditable

        return flags


if __name__ == "__main__":
    node_graph: NodeGraph = NodeGraph()
    print(isinstance(node_graph, QAbstractListModel))

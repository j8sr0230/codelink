from typing import Any, Optional, List, Dict

from PySide2.QtCore import Qt, QObject, QModelIndex, QAbstractTableModel


class NodeTableModel(QAbstractTableModel):

    def __init__(self, parent: QObject = None, nodes: Optional[List[Dict]] = None) -> None:
        super().__init__(parent)

        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes

        self.node_properties = ["Name: list", "Task: object", "Predecessors: list", "Successors: list", "Value: object"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.nodes)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.node_properties)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.nodes):
            return None

        if not 0 <= index.column() < len(self.node_properties):
            return None

        if role == Qt.DisplayRole:
            key: str = self.node_properties[index.column()]
            return self.nodes[index.row()][key]

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role != Qt.DisplayRole:
            return None

        if not 0 <= section < len(self.node_properties):
            return None

        if orientation == Qt.Horizontal:
            return self.node_properties[index.column()]

        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.DisplayRole) -> bool:
        if role != Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.nodes) and 0 <= index.column() < len(self.node_properties):
            key: str = self.node_properties[index.column()]
            self.nodes[index.row()][key]: Any = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        # if not index.isValid():
        #     return Qt.ItemIsEnabled
        return super().flags(index) | Qt.ItemIsEditable

    def insertRows(self, row: int, count: int, parent: QModelIndex = Qt.DisplayRole) -> bool:
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.nodes.insert(position + row, {"name": "", "address": ""})

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        del self.nodes[position:position + rows]

        self.endRemoveRows()
        return True



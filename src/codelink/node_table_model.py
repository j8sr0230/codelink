import sys
from typing import Any, Optional, List, Dict

from PySide2.QtCore import Qt, QObject, QModelIndex, QByteArray, QMimeData, QAbstractTableModel
from PySide2.QtGui import QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent
from PySide2.QtWidgets import QApplication, QWidget, QAbstractItemView, QTableView, QHBoxLayout

from networkx import DiGraph


class NodeTableModel(QAbstractTableModel):

    Mimetype = "text/plain"

    def __init__(self, parent: QObject = None, nodes: Optional[List[Dict]] = None) -> None:
        super().__init__(parent)

        if nodes is None:
            self.nodes: list = []
        else:
            self.nodes: list = nodes

        self.node_properties: list = ["Name", "Task", "Predecessors", "Successors", "Value"]

        self.graph: DiGraph = DiGraph()
        self.graph.add_node("Add", task="a + b", value="")
        print(self.graph.nodes.data()["Add"])

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
            return self.nodes[index.row()][self.node_properties[index.column()]]

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role != Qt.DisplayRole:
            return None

        if not 0 <= section < len(self.node_properties):
            return None

        if orientation == Qt.Horizontal:
            return self.node_properties[section]

        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.DisplayRole) -> bool:
        if role != Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.nodes) and 0 <= index.column() < len(self.node_properties):
            self.nodes[index.row()][self.node_properties[index.column()]]: Any = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return super().flags(index) | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(QModelIndex(), row, row + count - 1)

        for i in range(count):
            self.nodes.insert(row + i, {prop_name: None for prop_name in self.node_properties})

        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self.nodes[row:row + count]
        self.endRemoveRows()
        return True

    def supportedDropActions(self):
        return Qt.CopyAction

    def mimeTypes(self):
        return [self.Mimetype]

    def mimeData(self, indexes: list) -> QMimeData:
        sortedIndexes = sorted([index for index in indexes if index.isValid()], key=lambda index: index.row())

        encoded_data: list = []
        for index in sortedIndexes:
            encoded_data.append(self.nodes[index.row()])

        mime_data = QMimeData()
        mime_data.setData(self.Mimetype, QByteArray(bytes(str(encoded_data), "utf-8")))
        return mime_data

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        if action == Qt.IgnoreAction:
            return False
        elif not data.hasFormat(self.Mimetype):
            return False
        else:
            insert_row_idx = parent.row()
            if insert_row_idx < 0:
                insert_row_idx = len(self.nodes)

            data_stream: QByteArray = data.data(self.Mimetype).data()
            data_list = list(eval(data_stream))

            for i, row_data in enumerate(data_list):
                self.insertRow(insert_row_idx + i, parent)

                for j, node_prop in enumerate(self.node_properties):
                    self.setData(self.index(insert_row_idx + i, j, parent), row_data[node_prop], Qt.EditRole)

            return True


class NodeTableView(QTableView):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.setAlternatingRowColors(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        super().dragEnterEvent(event)
        event.accept()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        super().dragLeaveEvent(event)
        event.accept()

    def dragMoveEvent(self, event: QDragMoveEvent):
        super().dragMoveEvent(event)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        super().dropEvent(event)
        event.accept()


class View(QWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.node_model_one = NodeTableModel(parent=None, nodes=[{"Name": "Add", "Task": "a + b",
                                                                  "Predecessors": "[1, 2, 3]", "Successors": "[6]",
                                                                  "Value": "12"},
                                                                 {"Name": "Sub", "Task": "a - b",
                                                                  "Predecessors": "[1, 2, 3]", "Successors": "[6]",
                                                                  "Value": "12"},
                                                                 {"Name": "Mul", "Task": "a * b",
                                                                  "Predecessors": "[1, 2, 3]", "Successors": "[6]",
                                                                  "Value": "12"},
                                                                 {"Name": "Pow", "Task": "a ^ b",
                                                                  "Predecessors": "[1, 2, 3]", "Successors": "[6]",
                                                                  "Value": "12"}])
        self.node_table_view_one = NodeTableView(parent=self)
        self.node_table_view_one.setModel(self.node_model_one)

        self.node_model_two = NodeTableModel(parent=None, nodes=[])

        self.node_table_view_two = NodeTableView(parent=self)
        self.node_table_view_two.setModel(self.node_model_two)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.node_table_view_one)
        self.main_layout.addWidget(self.node_table_view_two)

        self.setLayout(self.main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = View()
    view.show()
    sys.exit(app.exec_())

import sys
from typing import Any, Optional, List, Dict

from PySide2.QtCore import Qt, QObject, QModelIndex, QAbstractTableModel
from PySide2.QtWidgets import QWidget, QTableView, QHBoxLayout, QApplication


class NodeTableModel(QAbstractTableModel):

    def __init__(self, parent: QObject = None, nodes: Optional[List[Dict]] = None) -> None:
        super().__init__(parent)

        if nodes is None:
            self.nodes: list = []
        else:
            self.nodes: list = nodes

        self.node_properties: list = ["Name", "Task", "Predecessors", "Successors", "Value"]

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
            return self.node_properties[section]

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

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(QModelIndex(), row, row + count - 1)

        for i in range(count):
            self.nodes.insert(row + i, {"Name": "", "Task": "", "Predecessors": "", "Successors": "", "Value": ""})

        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self.nodes[row:row + count]
        self.endRemoveRows()
        return True


class NodeTableView(QTableView):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        # self.setDragEnabled(True)
        # self.setAcceptDrops(True)
        # self.setDragDropMode(QAbstractItemView.DragDrop)
        # self.setDropIndicatorShown(True)
        # self.setSelectionMode(self.ExtendedSelection)

    # def dragEnterEvent(self, event: QDragEnterEvent):
    #     super().dragEnterEvent(event)
    #     # if not event.mimeData().hasText():
    #     #     event.mimeData().setText(self.currentIndex().data())
    #     event.accept()
    #
    # def dragLeaveEvent(self, event: QDragLeaveEvent):
    #     super().dragLeaveEvent(event)
    #     # print("Drop", event)
    #     event.accept()
    #
    # def dragMoveEvent(self, event: QDragMoveEvent):
    #     super().dragMoveEvent(event)
    #     # if event.mimeData().hasText():
    #     #     event.accept()
    #     # else:
    #     #     event.ignore()
    #     event.accept()
    #
    # def dropEvent(self, event: QDropEvent):
    #     super().dropEvent(event)
    #     # if event.mimeData().hasText():
    #     #     event.accept()
    #     # else:
    #     #     event.ignore()
    #     event.accept()


class View(QWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.node_model = NodeTableModel(parent=None, nodes=[{"Name": "Add", "Task": "a + b",
                                                              "Predecessors": "[1, 2, 3]", "Successors": "[6]",
                                                              "Value": "12"}])
        self.node_table = NodeTableView(parent=self)
        self.node_table.setModel(self.node_model)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.node_table)
        self.setLayout(self.main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = View()
    view.show()
    sys.exit(app.exec_())

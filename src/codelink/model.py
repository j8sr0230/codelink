import sys
from typing import Any, Optional

from PySide2.QtCore import Qt, QObject, QAbstractListModel, QModelIndex, QMimeData
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QAbstractItemView, QListView, QHBoxLayout
from PySide2.QtGui import QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent


class NodeGraphModel(QAbstractListModel):

    Mimetype = "application/vnd.row.list"

    def __init__(self, parent: Optional[QObject] = None, nodes: Optional[list] = None) -> None:
        super().__init__(parent)
        if nodes is None:
            nodes = []
        self._nodes = nodes

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            return "Nodes"
        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if index.isValid() and (role == Qt.DisplayRole):
            return self._nodes[index.row()]
        else:
            return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if (role == Qt.EditRole) and index.isValid() and (0 <= index.row() < len(self._nodes)):
            self._nodes[index.row()] = value
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(parent, row, row + count - 1)
        self._nodes[row:row] = [None] * count
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self._nodes[row:row + count]
        self.endRemoveRows()
        return True

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._nodes)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)

        if index.isValid():
            flags = flags | Qt.ItemIsEditable | Qt.ItemIsDragEnabled

        return flags

    def supportedDropActions(self):
        return Qt.MoveAction

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        print("Data", data)
        if action == Qt.IgnoreAction:
            return False
        if not data.hasFormat(self.Mimetype):
            return False
        if column > 0:
            return False

        strings = str(data.data(self.Mimetype)).split("\n")
        self.insertRows(row, len(strings))
        for i, text in enumerate(strings):
            self.setData(self.index(row + i, 0), text)

        return True

    def mimeData(self, indexes: list) -> QMimeData:
        # sortedIndexes = sorted([index for index in indexes
        #                         if index.isValid()], key=lambda index: index.row())
        # encodedData = '\n'.join(self.data(index, Qt.DisplayRole)
        #                         for index in sortedIndexes)
        # mimeData = QMimeData()
        # mimeData.setData(self.Mimetype, encodedData)
        # print(mimeData)
        mimeData = super().mimeData(indexes)
        print(mimeData.data("application/vnd.row.list"))
        return mimeData

    def mimeTypes(self):
        return [self.Mimetype]


class NodeGraphListView(QListView):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(self.SingleSelection)

    def dragEnterEvent(self, event: QDragEnterEvent):
        super().dragEnterEvent(event)
        # print("Drag enter", event)

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        super().dragLeaveEvent(event)
        # print("Drag leave", event)

    def dragMoveEvent(self, event: QDragMoveEvent):
        super().dragMoveEvent(event)
        # print("Drag move", event)

    def dropEvent(self, event: QDropEvent):
        super().dropEvent(event)
        # print("Drop", event)


class View(QWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.model_one = NodeGraphModel(parent=None, nodes=["Add", "Sub", "Mult", "Div", "Pow"])
        self.node_list_one = NodeGraphListView(parent=self)
        self.node_list_one.setModel(self.model_one)

        self.model_two = NodeGraphModel(parent=None, nodes=["Test"])
        self.node_list_two = NodeGraphListView(parent=self)
        self.node_list_two.setModel(self.model_two)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.node_list_one)
        self.main_layout.addWidget(self.node_list_two)
        self.setLayout(self.main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = View()
    view.show()
    sys.exit(app.exec_())

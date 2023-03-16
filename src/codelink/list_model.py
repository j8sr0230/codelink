import sys
from typing import Any, Optional

from PySide2.QtCore import Qt, QObject, QAbstractListModel, QModelIndex, QMimeData, QByteArray
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QAbstractItemView, QListView, QHBoxLayout
from PySide2.QtGui import QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent


class NodeGraphModel(QAbstractListModel):

    Mimetype = "text/plain"

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

    def mimeTypes(self):
        return [self.Mimetype]

    def mimeData(self, indexes: list) -> QMimeData:
        sortedIndexes = sorted([index for index in indexes if index.isValid()], key=lambda index: index.row())
        encoded_data: bytes = bytes("\n".join(self.data(index, Qt.DisplayRole) for index in sortedIndexes), "utf-8")
        mime_data = QMimeData()
        mime_data.setData(self.Mimetype, QByteArray(encoded_data))
        return mime_data

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        if action == Qt.IgnoreAction:
            return False
        elif not data.hasFormat(self.Mimetype):
            return False
        elif column > 0:
            return False
        else:
            strings: list = str(data.data(self.Mimetype).data(), encoding="utf-8").split("\n")
            if row == -1:
                row = self.rowCount()

            for i, text in enumerate(strings):
                self.insertRow(row + i, parent)
                self.setData(self.index(row + i, 0, parent), text)
            return True


class NodeGraphListView(QListView):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(self.ExtendedSelection)

    def dragEnterEvent(self, event: QDragEnterEvent):
        super().dragEnterEvent(event)
        # if not event.mimeData().hasText():
        #     event.mimeData().setText(self.currentIndex().data())
        event.accept()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        super().dragLeaveEvent(event)
        # print("Drop", event)
        event.accept()

    def dragMoveEvent(self, event: QDragMoveEvent):
        super().dragMoveEvent(event)
        # if event.mimeData().hasText():
        #     event.accept()
        # else:
        #     event.ignore()
        event.accept()

    def dropEvent(self, event: QDropEvent):
        super().dropEvent(event)
        # if event.mimeData().hasText():
        #     event.accept()
        # else:
        #     event.ignore()
        event.accept()


class View(QWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.model_one = NodeGraphModel(parent=None, nodes=["Add", "Sub", "Mult", "Div", "Pow"])
        self.node_list_one = NodeGraphListView(parent=self)
        self.node_list_one.setModel(self.model_one)

        self.model_two = NodeGraphModel(parent=None, nodes=[])
        # self.model_two.insertRow(1, QModelIndex())
        # self.model_two.setData(self.model_two.index(1, 0, QModelIndex()), "Test")

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

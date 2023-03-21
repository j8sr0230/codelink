import sys, json, pickle
from typing import Any, Optional, List, Dict

from PySide2.QtCore import Qt, QObject, QModelIndex, QByteArray, QMimeData, QAbstractTableModel
from PySide2.QtGui import QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent
from PySide2.QtWidgets import QApplication, QWidget, QAbstractItemView, QTableView, QHBoxLayout

from networkx import DiGraph


class DefaultTask:
    def __init__(self, name: str = "Name") -> None:
        self.name: str = name
        self.value: Any = 0


class InputTask(DefaultTask):
    def __init__(self, name: str = "Input", a: int = 0) -> None:
        super().__init__(name)
        self.a = a

    def eval(self) -> int:
        return self.a


class NodeTableModel(QAbstractTableModel):

    Mimetype = "text/plain"

    def __init__(self, parent: QObject = None, nodes: Optional[List[Dict]] = None) -> None:
        super().__init__(parent)

        if nodes is None:
            self.nodes: list = []
        else:
            self.nodes: list = nodes

        self.node_properties: list = ["Name", "Value", "Predecessors", "Successors"]

        self.graph: DiGraph = DiGraph()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.graph.nodes())

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.node_properties)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.graph.nodes()):
            return None

        if not 0 <= index.column() < len(self.node_properties):
            return None

        if role == Qt.DisplayRole:
            task: DefaultTask = list(self.graph.nodes())[index.row()]
            if index.column() == 0:
                return task.name
            if index.column() == 1:
                return task.value
            if index.column() == 2:
                return str([pre.name for pre in self.graph.predecessors(task)])
            if index.column() == 3:
                return str([suc.name for suc in self.graph.successors(task)])

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

        if index.isValid() and 0 <= index.row() < len(self.graph.nodes()) and 0 <= index.column() < 2:
            task: DefaultTask = list(self.graph.nodes())[index.row()]
            if index.column() == 0:
                task.name = value
            else:
                task.value = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flag = super().flags(index)

        if index.column() == 0:
            return flag | Qt.ItemIsEditable | Qt.ItemIsDragEnabled

        if index.column() == 1:
            return flag | Qt.ItemIsEditable

        return flag

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        print("Insert")

        # for i in range(count):
        #     self.nodes.insert(row + i, {prop_name: None for prop_name in self.node_properties})

        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)

        for i in range(count):
            task: DefaultTask = list(self.graph.nodes())[row + i]
            self.graph.remove_node(task)

        self.endRemoveRows()
        print("Remove")
        return True

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return [self.Mimetype]

    def mimeData(self, indexes: list) -> QMimeData:
        sortedIndexes = sorted([index for index in indexes if index.isValid()], key=lambda index: index.row())

        encoded_data: list = []
        for index in sortedIndexes:
            task: DefaultTask = list(self.graph.nodes())[index.row()]
            encoded_data.append(task)

        mime_data = QMimeData()
        mime_data.setData(self.Mimetype, QByteArray(pickle.dumps(encoded_data)))
        return mime_data

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        if action == Qt.IgnoreAction:
            return False
        elif not data.hasFormat(self.Mimetype):
            return False
        else:
            if row == -1:
                row = len(self.graph.nodes())

            data_stream: QByteArray = data.data(self.Mimetype).data()
            data_obj: list = pickle.loads(data_stream)

            for i, obj in enumerate(data_obj):
                self.insertRow(row + i, parent)
                self.graph.add_node(obj)

            return True


class NodeTableView(QTableView):

    def __init__(self, parent: QWidget = None) -> None:
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
        print(event.mimeData().data)
        event.accept()


class View(QWidget):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.node_model_one = NodeTableModel(parent=None, nodes=[])
        t1 = InputTask("Input")
        self.node_model_one.graph.add_node(t1)
        t2 = InputTask("Add")
        self.node_model_one.graph.add_node(t2)
        self.node_model_one.graph.add_edge(t1, t2)

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

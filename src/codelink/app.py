from __future__ import annotations
import sys
from typing import Any

from PySide2.QtCore import QAbstractTableModel, QObject, QModelIndex, Qt
from PySide2.QtWidgets import QApplication, QTableView, QWidget, QHBoxLayout


class CodeSnippet:
    def __init__(self, name: str = "Name", data_cache: object = -1, predecessors: list[QModelIndex] = None,
                 successors: list[QModelIndex] = None) -> None:

        self.name: str = name
        self.data_cache: object = data_cache

        if predecessors is None:
            predecessors: list[QModelIndex] = []
        self.predecessors: list[QModelIndex] = predecessors

        if successors is None:
            successors: list[QModelIndex] = []
        self.successors: list[QModelIndex] = successors

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def data_cache(self) -> object:
        return self._data_cache

    @data_cache.setter
    def data_cache(self, value: object) -> None:
        self._data_cache = value

    @property
    def predecessors(self) -> list[QModelIndex]:
        return self._predecessors

    @predecessors.setter
    def predecessors(self, value: list[QModelIndex]) -> None:
        self._predecessors = value

    @property
    def successors(self) -> list[QModelIndex]:
        return self._successors

    @successors.setter
    def successors(self, value: list[QModelIndex]) -> None:
        self._successors = value

    def eval(self) -> object:
        self.data_cache = 0
        return self.data_cache

    def __eq__(self, other: CodeSnippet) -> bool:
        return self.name == other.name

    def __gt__(self, other: CodeSnippet) -> bool:
        return self.name > other.name


class CodeSnippetTableModel(QAbstractTableModel):

    def __init__(self, code_snippets: list[CodeSnippet] = None, parent: QObject = None) -> None:
        super().__init__(parent)

        if code_snippets is None:
            code_snippets = []

        self.code_snippets = code_snippets

    @property
    def code_snippets(self) -> list[CodeSnippet]:
        return self._code_snippets

    @code_snippets.setter
    def code_snippets(self, value: list[CodeSnippet]) -> None:
        self._code_snippets = value

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            return len(self.code_snippets)
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            return 4
        return 0

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.code_snippets):
            return None

        if role == Qt.DisplayRole:
            code_snippet: CodeSnippet = self.code_snippets[index.row()]

            if index.column() == 0:
                return code_snippet.name
            elif index.column() == 1:
                return str(code_snippet.data_cache)
            elif index.column() == 2:
                return str(code_snippet.predecessors)
            elif index.column() == 3:
                return str(code_snippet.successors)
            else:
                return None
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return "Name"
            elif section == 1:
                return "Data cache"
            elif section == 2:
                return "Predecessors"
            elif section == 3:
                return "Successors"
            else:
                return None
        return None

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        self.code_snippets[row:row] = [CodeSnippet()] * count
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self.code_snippets[row:row + count]
        self.endRemoveRows()
        return True

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.DisplayRole) -> bool:
        if index.isValid() and role == Qt.EditRole:
            row: int = index.row()
            code_snippet: CodeSnippet = self.code_snippets[row]

            if index.column() == 0:
                code_snippet.name = str(value)
            elif index.column() == 1:
                code_snippet.data_cache = str(value)
            elif index.column() == 2:
                code_snippet.predecessors = str(value)
            elif index.column() == 3:
                code_snippet.successors = str(value)
            else:
                return False
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemIsEditable

        return super().flags(index) | Qt.ItemIsEditable


if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = CodeSnippetTableModel(code_snippets=[CodeSnippet("Add", 1), CodeSnippet("Sub", 8)])
    model.dataChanged.connect(lambda i, j: print(i.row(), i.column()))
    print(model.code_snippets)

    view = QTableView()
    view.setModel(model)
    view.setAlternatingRowColors(True)
    view.show()

    sys.exit(app.exec_())

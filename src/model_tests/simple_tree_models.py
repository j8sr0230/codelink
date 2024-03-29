from __future__ import annotations
import sys
from typing import Any, Optional, Union, cast

from PySide2 import QtCore, QtWidgets


class TreeItem:
    def __init__(self, data: list[str],  parent: Optional[TreeItem] = None) -> None:
        self.parent_item: Optional[TreeItem] = parent
        self.item_data: list[str] = data
        self.child_items: list[TreeItem] = []

    def append_child(self, item: TreeItem) -> None:
        self.child_items.append(item)

    def child(self, row) -> TreeItem:
        return self.child_items[row]

    def child_count(self) -> int:
        return len(self.child_items)

    def column_count(self) -> int:
        return len(self.item_data)

    def data(self, column: int) -> Optional[str]:
        try:
            return self.item_data[column]
        except IndexError:
            return None

    def parent(self) -> Optional[TreeItem]:
        return self.parent_item

    def row(self) -> int:
        if self.parent_item:
            return self.parent_item.child_items.index(self)

        return 0


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, data: str, parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)

        self.rootItem: TreeItem = TreeItem(["Title", "Summary"])
        self.setup_model_data(data.split("\n"), self.rootItem)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if parent.isValid():
            return cast(TreeItem, parent.internalPointer()).column_count()
        else:
            return self.rootItem.column_count()

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Optional[str]:
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None

        item: TreeItem = cast(TreeItem, index.internalPointer())
        return item.data(index.column())

    def flags(self, index: QtCore.QModelIndex) -> Union[QtCore.Qt.ItemFlag, QtCore.Qt.ItemFlags]:
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole) -> Any:
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parent_item: TreeItem = self.rootItem
        else:
            parent_item: TreeItem = cast(TreeItem, parent.internalPointer())

        child_item: TreeItem = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item: TreeItem = cast(TreeItem, index.internalPointer())
        parent_item: TreeItem = child_item.parent()

        if parent_item == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item: TreeItem = self.rootItem
        else:
            parent_item: TreeItem = cast(TreeItem, parent.internalPointer(), )

        return parent_item.child_count()

    @staticmethod
    def setup_model_data(lines: list[str], parent: TreeItem) -> None:
        parents: list[TreeItem] = [parent]
        indentations: list[int] = [0]

        number: int = 0

        while number < len(lines):
            position = 0
            while position < len(lines[number]):
                if lines[number][position] != " ":
                    break
                position += 1

            line_data = lines[number][position:].strip()

            if line_data:
                # Read the column data from the rest of the line.
                column_data = [s for s in line_data.split("\t") if s]

                if position > indentations[-1]:
                    # The last child of the current parent is now the new
                    # parent unless the current parent has no children.

                    if parents[-1].child_count() > 0:
                        parents.append(parents[-1].child(parents[-1].child_count() - 1))
                        indentations.append(position)

                else:
                    while position < indentations[-1] and len(parents) > 0:
                        parents.pop()
                        indentations.pop()

                # Append a new item to the current parent's list of children.
                parents[-1].append_child(TreeItem(column_data, parents[-1]))

            number += 1


if __name__ == '__main__':
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)

    f: QtCore.QFile = QtCore.QFile("default.txt")
    f.open(cast(QtCore.QIODevice.OpenMode, QtCore.QIODevice.ReadOnly))
    model: TreeModel = TreeModel(str(f.readAll(), "utf-8"))
    f.close()

    view: QtWidgets.QTreeView = QtWidgets.QTreeView()
    view.setModel(model)
    view.setWindowTitle("Simple Tree Model")
    view.show()

    sys.exit(app.exec_())

from __future__ import annotations
from typing import Any, Optional, cast
import sys

from PySide2 import QtCore, QtWidgets

from ui_main_window import UiMainWindow


class TreeItem:
    def __init__(self, data, parent=None):
        self.parent_item: Optional[TreeItem] = parent
        self.item_data: list[str] = data
        self.child_items: list[TreeItem] = []

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def child_number(self):
        if self.parent_item is not None:
            return self.parent_item.child_items.index(self)
        return 0

    def column_count(self):
        return len(self.item_data)

    def data(self, column):
        return self.item_data[column]

    def insert_children(self, position, count, columns):
        if position < 0 or position > len(self.child_items):
            return False

        for row in range(count):
            data = [v for v in range(columns)]
            item: TreeItem = TreeItem(data, self)
            self.child_items.insert(position, item)

        return True

    def insert_columns(self, position, columns):
        if position < 0 or position > len(self.item_data):
            return False

        for column in range(columns):
            # self.item_data.insert(position, None)
            self.item_data.insert(position, "")

        for child in self.child_items:
            child.insert_columns(position, columns)

        return True

    def parent(self):
        return self.parent_item

    def remove_children(self, position, count):
        if position < 0 or position + count > len(self.child_items):
            return False

        for row in range(count):
            self.child_items.pop(position)

        return True

    def remove_columns(self, position, columns):
        if position < 0 or position + columns > len(self.item_data):
            return False

        for column in range(columns):
            self.item_data.pop(position)

        for child in self.child_items:
            child.remove_columns(position, columns)

        return True

    def set_data(self, column, value):
        if column < 0 or column >= len(self.item_data):
            return False

        self.item_data[column] = value

        return True


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, headers: list[str], data: str, parent: QtCore.QObject = None):
        super().__init__(parent)

        self.rootItem: TreeItem = TreeItem(headers)
        self.setup_model_data(data.split("\n"), self.rootItem)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.rootItem.column_count()

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return None

        item = self.get_item(index)
        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return 0

        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def get_item(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        parent_item: TreeItem = self.get_item(parent)
        child_item: TreeItem = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def insertColumns(self, position, columns, parent=QtCore.QModelIndex()):
        self.beginInsertColumns(parent, position, position + columns - 1)
        success = self.rootItem.insert_columns(position, columns)
        self.endInsertColumns()

        return success

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parent_item = self.get_item(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        success = parent_item.insert_children(position, rows, self.rootItem.column_count())
        self.endInsertRows()

        return success

    def parent(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item: TreeItem = self.get_item(index)
        parent_item: TreeItem = child_item.parent()

        if parent_item == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def removeColumns(self, position, columns, parent=QtCore.QModelIndex()):
        self.beginRemoveColumns(parent, position, position + columns - 1)
        success = self.rootItem.remove_columns(position, columns)
        self.endRemoveColumns()

        if self.rootItem.column_count() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parent_item = self.get_item(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parent_item.remove_children(position, rows)
        self.endRemoveRows()

        return success

    def rowCount(self, parent=QtCore.QModelIndex()):
        parent_item = self.get_item(parent)

        return parent_item.child_count()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role != QtCore.Qt.EditRole:
            return False

        item = self.get_item(index)
        result = item.set_data(index.column(), value)

        if result:
            self.dataChanged.emit(index, index)

        return result

    def setHeaderData(self, section, orientation, value, role=QtCore.Qt.EditRole):
        if role != QtCore.Qt.EditRole or orientation != QtCore.Qt.Horizontal:
            return False

        result = self.rootItem.set_data(section, value)
        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

    def setup_model_data(self, lines, parent):
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
                parent = parents[-1]
                parent.insert_children(parent.child_count(), 1,
                                       self.rootItem.column_count())
                for column in range(len(column_data)):
                    parent.child(parent.child_count() - 1).set_data(column, column_data[column])

            number += 1


class MainWindow(QtWidgets.QMainWindow, UiMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setup_ui(self)

        headers: list[str] = ["Key", "Value"]

        file = QtCore.QFile("./default.txt")
        file.open(cast(QtCore.QIODevice.OpenMode, QtCore.QIODevice.ReadOnly))
        model = TreeModel(headers, str(file.readAll(), "utf-8"))
        file.close()

        self.view.setModel(model)
        for column in range(model.columnCount(QtCore.QModelIndex())):
            self.view.resizeColumnToContents(column)

        cast(QtCore.SignalInstance, self.exit_action.triggered).connect(QtWidgets.QApplication.quit)

        self.view.selectionModel().selectionChanged.connect(self.update_actions)

        cast(QtCore.SignalInstance, self.actions_menu.aboutToShow).connect(self.update_actions)
        cast(QtCore.SignalInstance, self.insert_row_action.triggered).connect(self.insert_row)
        cast(QtCore.SignalInstance, self.insert_column_action.triggered).connect(self.insert_column)
        cast(QtCore.SignalInstance, self.remove_row_action.triggered).connect(self.remove_row)
        cast(QtCore.SignalInstance, self.remove_column_action.triggered).connect(self.remove_column)
        cast(QtCore.SignalInstance, self.insert_child_action.triggered).connect(self.insert_child)

        self.update_actions()

    def insert_child(self):
        index = self.view.selectionModel().currentIndex()
        model: TreeModel = self.view.model()

        if model.columnCount(index) == 0:
            if not model.insertColumn(0, index):
                return

        if not model.insertRow(0, index):
            return

        for column in range(model.columnCount(index)):
            child = model.index(0, column, index)
            model.setData(child, "[No data]", int(QtCore.Qt.EditRole))
            if model.headerData(column, QtCore.Qt.Horizontal) == "":
                model.setHeaderData(column, QtCore.Qt.Horizontal, "[No header]", int(QtCore.Qt.EditRole))

        self.view.selectionModel().setCurrentIndex(model.index(0, 0, index), QtCore.QItemSelectionModel.ClearAndSelect)
        self.update_actions()

    def insert_column(self, parent=QtCore.QModelIndex()):
        model = self.view.model()
        column = self.view.selectionModel().currentIndex().column()

        changed = model.insertColumn(column + 1, parent)
        if changed:
            model.setHeaderData(column + 1, QtCore.Qt.Horizontal, "[No header]", QtCore.Qt.EditRole)

        self.update_actions()

        return changed

    def insert_row(self):
        index = self.view.selectionModel().currentIndex()
        model = self.view.model()

        if not model.insertRow(index.row() + 1, index.parent()):
            return

        self.update_actions()

        for column in range(model.columnCount(index.parent())):
            child = model.index(index.row()+1, column, index.parent())
            model.setData(child, "[No data]", QtCore.Qt.EditRole)

    def remove_column(self, parent=QtCore.QModelIndex()):
        model = self.view.model()
        column = self.view.selectionModel().currentIndex().column()

        changed = model.remove_column(column, parent)

        if not parent.isValid() and changed:
            self.update_actions()

        return changed

    def remove_row(self):
        index = self.view.selectionModel().currentIndex()
        model = self.view.model()

        if model.remove_row(index.row(), index.parent()):
            self.update_actions()

    def update_actions(self):
        has_selection = not self.view.selectionModel().selection().isEmpty()
        self.remove_row_action.setEnabled(has_selection)
        self.remove_column_action.setEnabled(has_selection)

        has_current = self.view.selectionModel().currentIndex().isValid()
        self.insert_row_action.setEnabled(has_current)
        self.insert_column_action.setEnabled(has_current)

        if has_current:
            self.view.closePersistentEditor(self.view.selectionModel().currentIndex())

            row = self.view.selectionModel().currentIndex().row()
            column = self.view.selectionModel().currentIndex().column()
            if self.view.selectionModel().currentIndex().parent().isValid():
                self.statusBar().showMessage("Position: (%d,%d)" % (row, column))
            else:
                self.statusBar().showMessage("Position: (%d,%d) in top level" % (row, column))


if __name__ == '__main__':
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    window: MainWindow = MainWindow()
    window.show()
    sys.exit(app.exec_())

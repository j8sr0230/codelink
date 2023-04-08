from __future__ import annotations
import sys
import pickle
from typing import Any, Optional

from PySide2.QtCore import (Qt, QObject, QPoint, QByteArray, QMimeData, QAbstractItemModel, QAbstractTableModel,
                            QAbstractListModel, QModelIndex, QItemSelectionModel, QSortFilterProxyModel, QRegExp,
                            QAbstractProxyModel, QEvent)
from PySide2.QtWidgets import (QApplication, QWidget, QTableView, QListView, QHeaderView, QHBoxLayout, QVBoxLayout,
                               QSplitter, QLineEdit, QStyleFactory)
from PySide2.QtGui import QCursor, QIcon, QBrush


class AbstractCodeItem:
    def __init__(self, name: str = "Test", data_cache: object = -1, predecessors: Optional[list[int]] = None,
                 successors: Optional[list[int]] = None) -> None:

        self.name: str = name
        self.data_cache: object = data_cache

        if predecessors is None:
            predecessors: Optional[list[int]] = []
        self.predecessors: Optional[list[int]] = predecessors

        if successors is None:
            successors: Optional[list[int]] = []
        self.successors: Optional[list[int]] = successors

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
    def predecessors(self) -> Optional[list[int]]:
        return self._predecessors

    @predecessors.setter
    def predecessors(self, value: list[int]) -> None:
        self._predecessors = value

    @property
    def successors(self) -> Optional[list[int]]:
        return self._successors

    @successors.setter
    def successors(self, value: list[QModelIndex]) -> None:
        self._successors = value

    def eval(self) -> object:
        self.data_cache = 0
        return self.data_cache

    def __eq__(self, other: AbstractCodeItem) -> bool:
        return self.name == other.name

    def __gt__(self, other: AbstractCodeItem) -> bool:
        return self.name > other.name


class AddCodeItem(AbstractCodeItem):
    def __init__(self, name: str = "Add", data_cache: object = 0, predecessors: Optional[list[int]] = None,
                 successors: Optional[list[int]] = None) -> None:
        super().__init__(name, data_cache, predecessors, successors)


class SubCodeItem(AbstractCodeItem):
    def __init__(self, name: str = "Sub", data_cache: object = 1, predecessors: Optional[list[int]] = None,
                 successors: Optional[list[int]] = None) -> None:
        super().__init__(name, data_cache, predecessors, successors)


class MulCodeItem(AbstractCodeItem):
    def __init__(self, name: str = "Mul", data_cache: object = 2, predecessors: Optional[list[int]] = None,
                 successors: Optional[list[int]] = None) -> None:
        super().__init__(name, data_cache, predecessors, successors)


class PowCodeItem(AbstractCodeItem):
    def __init__(self, name: str = "Pow", data_cache: object = 3, predecessors: Optional[list[int]] = None,
                 successors: Optional[list[int]] = None) -> None:
        super().__init__(name, data_cache, predecessors, successors)


registered_item_classes: dict = {
    "Test": AbstractCodeItem,
    "Add": AddCodeItem,
    "Sub": SubCodeItem,
    "Mul": MulCodeItem,
    "Pow": PowCodeItem
    }


class CodeKeyListModel(QAbstractListModel):
    def __init__(self, code_item_keys: Optional[list[str]] = None, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        if code_item_keys is None:
            code_item_keys: list[str] = []
        self.code_item_keys = code_item_keys

    @property
    def code_item_keys(self) -> list[str]:
        return self._code_item_keys

    @code_item_keys.setter
    def code_item_keys(self, value: list[str]) -> None:
        self._code_item_keys = value

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            return len(self.code_item_keys)
        return 0

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.code_item_keys):
            return None

        if role == Qt.DisplayRole:
            return self.code_item_keys[index.row()]
        else:
            return None

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(parent, row, row + count - 1)
        self.code_item_keys[row:row] = [""] * count
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self.code_item_keys[row:row + count]
        self.endRemoveRows()
        return True

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if index.isValid() and role == Qt.EditRole:
            row: int = index.row()
            self.code_item_keys[row] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemIsEditable

        return super().flags(index) | Qt.ItemIsEditable | Qt.ItemIsDragEnabled

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeData(self, indexes: list) -> QMimeData:
        sorted_indexes = sorted([index for index in indexes if index.isValid()], key=lambda index: index.row())
        encoded_data: bytes = bytes("\n".join(self.data(index, Qt.DisplayRole) for index in sorted_indexes), "utf-8")
        mime_data = QMimeData()
        mime_data.setData(self.mimeTypes()[0], QByteArray(encoded_data))
        return mime_data

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        if action == Qt.IgnoreAction:
            return False
        elif not data.hasFormat(self.mimeTypes()[0]):
            return False
        elif row > len(self.code_item_keys):
            return False
        else:
            code_key_list: list[str] = str(data.data(self.mimeTypes()[0]).data(), encoding="utf-8").split("\n")
            if row == -1:
                row = self.rowCount()

            for idx, key in enumerate(code_key_list):
                self.insertRow(row + idx, parent)
                self.setData(self.index(row + idx, 0, parent), key)
            return True


class CodeItemTableModel(QAbstractTableModel):
    def __init__(self, code_items: Optional[list[AbstractCodeItem]] = None, parent: QObject = None) -> None:
        super().__init__(parent)

        if code_items is None:
            code_items: list[AbstractCodeItem] = []

        self.code_items = code_items

    @property
    def code_items(self) -> list[AbstractCodeItem]:
        return self._code_snippets

    @code_items.setter
    def code_items(self, value: list[AbstractCodeItem]) -> None:
        self._code_snippets = value

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            return len(self.code_items)
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            return 4
        return 0

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.code_items):
            return None

        if role == Qt.DisplayRole:
            code_item: AbstractCodeItem = self.code_items[index.row()]

            if index.column() == 0:
                return code_item.name
            elif index.column() == 1:
                return str(code_item.data_cache)
            elif index.column() == 2:
                return str(code_item.predecessors)
            elif index.column() == 3:
                return str(code_item.successors)
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

        if orientation == Qt.Vertical:
            return section

        return None

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        self.code_items[row:row] = [AbstractCodeItem()] * count
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self.code_items[row:row + count]
        self.endRemoveRows()
        return True

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.DisplayRole) -> bool:
        if index.isValid() and role == Qt.EditRole:
            row: int = index.row()
            code_item: AbstractCodeItem = self.code_items[row]

            if index.column() == 0:
                code_item.name = str(value)
            elif index.column() == 1:
                code_item.data_cache = str(value)
            elif index.column() == 2:
                code_item.predecessors = str(value)
            elif index.column() == 3:
                code_item.successors = str(value)
            else:
                return False
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemIsEditable

        if index.column() == 0:
            return super().flags(index) | Qt.ItemIsEditable | Qt.ItemIsDragEnabled
        else:
            return super().flags(index)

    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.MoveAction

    def mimeData(self, indexes: list) -> QMimeData:
        sorted_indexes = sorted([index for index in indexes if index.isValid()], key=lambda index: index.row())

        mime_data = QMimeData()
        mime_data.setData(self.mimeTypes()[0], QByteArray(pickle.dumps([index.row() for index in sorted_indexes])))
        return mime_data

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        if action == Qt.IgnoreAction:
            return False
        elif not data.hasFormat(self.mimeTypes()[0]):
            return False
        elif row >= len(self.code_items):
            return False
        else:
            data_stream: QByteArray = data.data(self.mimeTypes()[0]).data()

            source_rows: list = pickle.loads(data_stream)
            target_code_item: AbstractCodeItem = self.code_items[row]
            if row not in source_rows:
                if column == 2:
                    target_code_item.predecessors.extend(source_rows)
                    self.dataChanged.emit(self.index(row, 2), self.index(row, 2))
                    for idx in source_rows:
                        source_code_snippet: AbstractCodeItem = self.code_items[idx]
                        source_code_snippet.successors.append(row)
                        self.dataChanged.emit(self.index(idx, 3), self.index(idx, 3))

                elif column == 3:
                    target_code_item.successors.extend(source_rows)
                    self.dataChanged.emit(self.index(row, 3), self.index(row, 3))
                    for idx in source_rows:
                        source_code_snippet: AbstractCodeItem = self.code_items[idx]
                        source_code_snippet.predecessors.append(row)
                        self.dataChanged.emit(self.index(idx, 2), self.index(idx, 2))

                return True
            else:
                return False


class CodeItemPropertyProxy(QSortFilterProxyModel):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    def mapFromSource(self, source_index: QModelIndex) -> QModelIndex:
        return self.index(source_index.column(), source_index.row(), QModelIndex())

    def mapToSource(self, proxy_index: QModelIndex) -> QModelIndex:
        if self.sourceModel():
            return self.sourceModel().index(proxy_index.column(), proxy_index.row(), QModelIndex())
        else:
            return QModelIndex()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not self.sourceModel():
            return 0
        return self.sourceModel().rowCount()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not self.sourceModel():
            return 0
        return self.sourceModel().columnCount()

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        return self.createIndex(row, column)

    def parent(self, child: QModelIndex = QModelIndex()) -> QModelIndex:
        return QModelIndex()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if not self.sourceModel():
            return None

        if orientation == Qt.Vertical:
            orientation = Qt.Horizontal
        else:
            orientation = Qt.Vertical

        return self.sourceModel().headerData(section, orientation, role)


class CodeKeyListView(QListView):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
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


class CodeItemTableView(QTableView):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def dragEnterEvent(self, event: QDragEnterEvent):
        super().dragEnterEvent(event)
        event.accept()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        super().dragLeaveEvent(event)
        event.accept()

    def dragMoveEvent(self, event: QDragMoveEvent):
        item_idx: QModelIndex = self.indexAt(event.pos())
        self.selectionModel().select(item_idx, QItemSelectionModel.ClearAndSelect)

        super().dragMoveEvent(event)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        if event.source().__class__ is CodeItemTableView:
            super().dropEvent(event)
            event.accept()
        else:
            # Drop event from CodeKeyList
            code_key_list: list[str] = str(event.mimeData().data(event.source().model().mimeTypes()[0]).data(),
                                           encoding="utf-8").split("\n")
            target_index: QModelIndex = self.indexAt(event.pos())
            target_row: int = target_index.row()
            if target_row < 0:
                target_row = len(self.model().code_items)
            for idx, key in enumerate(code_key_list):
                self.model().insertRow(target_row + idx, QModelIndex())
                self.model().code_items[target_row + idx] = registered_item_classes[key]()
                self.model().dataChanged.emit(self.model().index(target_row, 0),
                                              self.model().index(target_row, self.model().columnCount() - 1))


class MainView(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.code_key_model: CodeKeyListModel = CodeKeyListModel(list(registered_item_classes.keys()))
        self.code_key_model.dataChanged.connect(lambda i, j: print("code_key_model changed:", i.row(), i.column(), "\n",
                                                                   code_key_model.code_item_keys))

        self.code_key_proxy_model: QSortFilterProxyModel = QSortFilterProxyModel()
        self.code_key_proxy_model.setDynamicSortFilter(True)
        self.code_key_proxy_model.setSourceModel(self.code_key_model)

        self.code_item_model: CodeItemTableModel = CodeItemTableModel(code_items=[])
        self.code_item_model.dataChanged.connect(lambda i, j: print("code_item_model changed:", i.row(), i.column(),
                                                                    self.code_item_model.code_items))

        self.code_item_proxy_model: CodeItemPropertyProxy = CodeItemPropertyProxy()
        self.code_item_proxy_model.setSourceModel(self.code_item_model)

        self.splitter: QSplitter = QSplitter()

        self.left_container: QWidget = QWidget()
        self.vertical_layout: QVBoxLayout = QVBoxLayout()
        self.vertical_layout.setMargin(0)
        self.filter_line_edit: QLineEdit = QLineEdit(parent=self.left_container)
        self.filter_line_edit.setPlaceholderText("Filter code items ...")
        self.filter_line_edit.textChanged.connect(self.filter_reg_exp_changed)
        self.code_key_view: CodeKeyListView = CodeKeyListView(parent=self.left_container)
        self.code_key_view.setModel(self.code_key_model)
        self.code_key_proxy_view: CodeKeyListView = CodeKeyListView(parent=self.left_container)
        self.code_key_proxy_view.setModel(self.code_key_proxy_model)
        self.vertical_layout.addWidget(self.filter_line_edit)
        self.vertical_layout.addWidget(self.code_key_view)
        self.vertical_layout.addWidget(self.code_key_proxy_view)
        self.left_container.setLayout(self.vertical_layout)
        self.splitter.addWidget(self.left_container)

        self.code_item_table_view: CodeItemTableView = CodeItemTableView(parent=self.splitter)
        self.code_item_table_view.setModel(self.code_item_model)
        self.code_item_table_view.selectionModel().selectionChanged.connect(self.set_prop_table_item)
        self.splitter.addWidget(self.code_item_table_view)

        self.code_item_prop_table = CodeItemTableView(parent=self.splitter)
        # self.code_item_prop_table.setModel(self.code_item_proxy_model)
        self.code_item_prop_table.horizontalHeader().hide()
        self.code_item_model.dataChanged.connect(self.reset_prop_table_model)
        self.splitter.addWidget(self.code_item_prop_table)

        self.splitter.setSizes([200, 500, 200])

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.splitter)

        self.setWindowTitle("Codelink")
        self.setLayout(self.main_layout)

    def filter_reg_exp_changed(self) -> None:
        regExp = QRegExp(self.filter_line_edit.text(), Qt.CaseInsensitive, QRegExp.PatternSyntax.RegExp)
        self.code_key_proxy_model.setFilterRegExp(regExp)

    def reset_prop_table_model(self) -> None:
        # noinspection PyTypeChecker
        self.code_item_prop_table.setModel(None)
        self.set_prop_table_item()

    def set_prop_table_item(self):
        selected_indexes: list = self.code_item_table_view.selectedIndexes()
        if len(selected_indexes) > 0:
            self.code_item_prop_table.setModel(self.code_item_proxy_model)
            selected_row: int = selected_indexes[0].row()
            for row in range(self.code_item_model.rowCount()):
                if row != selected_row:
                    self.code_item_prop_table.hideColumn(row)
                else:
                    self.code_item_prop_table.showColumn(row)
        else:
            # noinspection PyTypeChecker
            self.code_item_prop_table.setModel(None)


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    app.setStyle(QStyleFactory().create("Fusion"))

    view: QWidget = MainView()
    view.resize(1200, 400)
    view.show()

    sys.exit(app.exec_())
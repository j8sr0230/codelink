import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_table import PropertyTable


class IntegerDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:

        editor: QtWidgets.QSpinBox = QtWidgets.QSpinBox(parent)
        editor.setFrame(True)
        editor.setRange(-64000, 64000)
        editor.setSingleStep(10)
        editor.valueChanged.connect(self.commit_editor)

        if index.isValid():
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()  # Gets sender, in this case QSpinBox
        self.commitData.emit(editor)  # Emit signal of delegate

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        # noinspection PyTypeChecker
        value: int = int(index.data(QtCore.Qt.DisplayRole))
        editor.setValue(value)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        editor.interpretText()
        value = int(editor.value())
        model.setData(index, value, QtCore.Qt.EditRole | QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def eventFilter(self, editor: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Tab:
                self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.NoHint)
                return True
            else:
                return False
        else:
            return False


class BooleanDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

        self._items: list[str] = ["false", "true"]

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:

        editor: QtWidgets.QComboBox = QtWidgets.QComboBox(parent)
        editor.addItems(self._items)
        editor.currentIndexChanged.connect(self.commit_editor)

        item_list_view: QtWidgets.QAbstractItemView = editor.view()
        item_list_view.setSpacing(2)

        if index.isValid():
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()
        self.commitData.emit(editor)

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        # noinspection PyTypeChecker
        value: str = str(index.data(QtCore.Qt.DisplayRole)).lower()
        num: int = self._items.index(value)
        editor.setCurrentIndex(num)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        value: bool = eval(editor.currentText().capitalize())

        # noinspection PyTypeChecker
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def eventFilter(self, editor: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Tab:
                self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.NoHint)
                return True
            else:
                return False
        else:
            return False


class StringDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:

        editor: QtWidgets.QLineEdit = QtWidgets.QLineEdit(parent)
        editor.setFocusPolicy(QtCore.Qt.StrongFocus)
        editor.textChanged.connect(self.commit_editor)

        if index.isValid():
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()
        self.commitData.emit(editor)

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        # noinspection PyTypeChecker
        value: str = index.data(QtCore.Qt.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:

        value: str = editor.text()
        model.setData(index, value, QtCore.Qt.EditRole | QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def eventFilter(self, editor: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Tab:
                self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.NoHint)
                return True
            else:
                return False
        else:
            return False

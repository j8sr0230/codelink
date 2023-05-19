import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class IntegerDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem,
              index: QtCore.QModelIndex) -> None:

        if isinstance(self.parent(), QtWidgets.QAbstractItemView) and index.column() == 1 and type(index.data()) == int:
            self.parent().openPersistentEditor(index)

        if index.isValid() and not index.column() == 1:
            super().paint(painter, option, index)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        editor: QtWidgets.QSpinBox = QtWidgets.QSpinBox(parent)

        editor.setFrame(True)
        editor.setRange(-64000, 64000)
        editor.setSingleStep(10)
        editor.valueChanged.connect(self.commit_editor)

        editor.setStyleSheet("""
           QSpinBox {
                color: #E5E5E5;
                background-color: transparent;
                selection-background-color: #334D80;
                border-radius: 0px;
                padding-left: 3px;
                padding-right: 0px;
                padding-top: 0px;
                padding-bottom: 0px;
                margin: 0px;
                border: none;
            }
            QSpinBox:focus {
                color: #E5E5E5;
                background-color: transparent;
            }
            QSpinBox::up-arrow {
                width: 12px; 
                height: 12px;
                background-color: transparent;
                image: url(icon:images_dark-light/up_arrow_light.svg);
                /*image: url(qss:images_dark-light/down_arrow_light.svg);*/
            }
            QSpinBox::up-button{
                background-color: transparent;
            }
            QSpinBox::down-arrow {
                width: 12px; 
                height: 12px;
                background-color: transparent;           
                image: url(icon:images_dark-light/down_arrow_light.svg);
                /*image: url(qss:images_dark-light/down_arrow_light.svg);*/
            }
            QSpinBox::down-button{
                background-color: transparent;
            }
        """)

        if index.isValid() and type(index.data()) == int:
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()
        self.commitData.emit(editor)

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


class BooleanDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

        self._items: list[str] = ["False", "True"]

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem,
              index: QtCore.QModelIndex) -> None:

        if (isinstance(self.parent(), QtWidgets.QAbstractItemView) and index.column() == 1 and
                type(index.data()) == bool):
            self.parent().openPersistentEditor(index)

        if index.isValid() and not index.column() == 1:
            super().paint(painter, option, index)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        editor: QtWidgets.QComboBox = QtWidgets.QComboBox(parent)
        editor.addItems(self._items)
        editor.currentIndexChanged.connect(self.commit_editor)

        editor.setStyleSheet("""
           QComboBox {
                color: #E5E5E5;
                background-color: transparent;
                border-radius: 0px;
                padding-left: 3px;
                padding-right: 0px;
                padding-top: 0px;
                padding-bottom: 0px;
                margin: 0px;
                border: none;
            }
            QComboBox::drop-down {
                background-color: transparent;
                subcontrol-origin: border;
                subcontrol-position: top right;
                padding-left: 0px;
                padding-right: 8px;
                padding-top: 0px;
                padding-bottom: 0px;
                border-radius: 0px;
            }
            QComboBox::down-arrow {
                width: 10px; 
                height: 10px;
                image: url(icon:images_dark-light/down_arrow_light.svg);
                /*image: url(qss:images_dark-light/down_arrow_light.svg);*/
            }
            QListView{
                border: none;
            }
        """)

        item_list_view: QtWidgets.QAbstractItemView = editor.view()
        item_list_view.setSpacing(2)
        item_list_view.setStyleSheet("""
           QAbstractItemView {
                color: #E5E5E5;
                selection-color: #E5E5E5;
                background-color: #282828;
                selection-background-color: #334D80;
                margin: 0px;
                padding: 0px;
                border: none;
                border-radius: 0px;
                outline: none;
            }
        """)

        if index.isValid() and type(index.data()) == bool:
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()
        self.commitData.emit(editor)

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        # noinspection PyTypeChecker
        value: str = str(index.data(QtCore.Qt.DisplayRole))
        num: int = self._items.index(value)
        editor.setCurrentIndex(num)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        value: bool = eval(editor.currentText())

        # noinspection PyTypeChecker
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)


class StringDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem,
              index: QtCore.QModelIndex) -> None:

        if isinstance(self.parent(), QtWidgets.QAbstractItemView) and index.column() == 1 and type(index.data()) == str:
            self.parent().openPersistentEditor(index)

        if index.isValid() and not index.column() == 1:
            super().paint(painter, option, index)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        editor: QtWidgets.QLineEdit = QtWidgets.QLineEdit(parent)
        # editor.setFocusPolicy(QtCore.Qt.StrongFocus)

        editor.textChanged.connect(self.commit_editor)

        editor.setStyleSheet("""
           QLineEdit {
                color: #E5E5E5;
                background-color: transparent;
                selection-background-color: red;
                border-radius: 0px;
                padding-left: 3px;
                padding-right: 0px;
                padding-top: 0px;
                padding-bottom: 0px;
                margin: 0px;
                border: none;
            }
            QLineEdit:focus {
                color: green;
                background-color: transparent;
            }
            QLineEdit:selected {
                color: #E5E5E5;
                background-color: transparent;
            }
        """)

        if index.isValid() and type(index.data()) == str:
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

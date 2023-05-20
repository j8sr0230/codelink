import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_table import PropertyTable


class IntegerDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

        self._spin_box: QtWidgets.QSpinBox = QtWidgets.QSpinBox()
        self._spin_box.setFont(QtGui.QFont("Sans Serif", 10))
        self._spin_box.setFrame(True)
        self._spin_box.setRange(-64000, 64000)
        self._spin_box.setSingleStep(10)

        self._spin_box.setStyleSheet("""
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
        self._spin_box.valueChanged.connect(self.commit_editor)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem,
              index: QtCore.QModelIndex) -> None:

        if isinstance(self.parent(), QtWidgets.QAbstractItemView) and index.column() == 1 and type(index.data()) == int:
            self.parent().openPersistentEditor(index)

        if index.isValid() and not index.column() == 1:
            super().paint(painter, option, index)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:

        editor: QtWidgets.QWidget = QtWidgets.QWidget(parent)
        editor.setStyleSheet("background-color: transparent")
        editor_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        editor_layout.setSpacing(0)
        editor_layout.setMargin(0)
        editor_layout.addWidget(self._spin_box)
        editor.setLayout(editor_layout)

        if index.isValid() and type(index.data()) == int:
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()  # Gets sender, in this case QSpinBox
        self.commitData.emit(editor.parent())  # Emit signal of delegate, not of QSpinBox

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        # noinspection PyTypeChecker
        value: int = int(index.data(QtCore.Qt.DisplayRole))
        self._spin_box.setValue(value)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        self._spin_box.interpretText()
        value = int(self._spin_box.value())
        model.setData(index, value, QtCore.Qt.EditRole | QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)


class BooleanDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

        self._items: list[str] = ["False", "True"]

        self._combo_box: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self._combo_box.setFont(QtGui.QFont("Sans Serif", 10))
        self._combo_box.addItems(self._items)
        self._combo_box.currentIndexChanged.connect(self.commit_editor)

        self._combo_box.setStyleSheet("""
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

        item_list_view: QtWidgets.QAbstractItemView = self._combo_box.view()
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

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem,
              index: QtCore.QModelIndex) -> None:

        if (isinstance(self.parent(), QtWidgets.QAbstractItemView) and index.column() == 1 and
                type(index.data()) == bool):
            self.parent().openPersistentEditor(index)

        if index.isValid() and not index.column() == 1:
            super().paint(painter, option, index)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:

        editor: QtWidgets.QWidget = QtWidgets.QWidget(parent)
        editor.setStyleSheet("background-color: transparent")
        editor_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        editor_layout.setSpacing(0)
        editor_layout.setMargin(0)
        editor_layout.addWidget(self._combo_box)
        editor.setLayout(editor_layout)

        if index.isValid() and type(index.data()) == bool:
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()
        self.commitData.emit(editor.parent())

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        # noinspection PyTypeChecker
        value: str = str(index.data(QtCore.Qt.DisplayRole))
        num: int = self._items.index(value)
        self._combo_box.setCurrentIndex(num)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        value: bool = eval(self._combo_box.currentText())

        # noinspection PyTypeChecker
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)


class StringDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

        self._current_index: QtCore.QModelIndex = QtCore.QModelIndex()

        self._line_edit: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self._line_edit.setFont(QtGui.QFont("Sans Serif", 10))
        self._line_edit.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._line_edit.setStyleSheet("""
           QLineEdit {
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
            QLineEdit:focus {
                color: #E5E5E5;
                background-color: transparent;
            }
            QLineEdit:selected {
                color: #E5E5E5;
                background-color: transparent;
            }
        """)
        self._line_edit.textChanged.connect(self.commit_editor)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem,
              index: QtCore.QModelIndex) -> None:

        if isinstance(self.parent(), QtWidgets.QAbstractItemView) and index.column() == 1 and type(index.data()) == str:
            self.parent().openPersistentEditor(index)

        if index.isValid() and not index.column() == 1:
            super().paint(painter, option, index)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:

        self._current_index: QtCore.QModelIndex = index

        editor: QtWidgets.QWidget = QtWidgets.QWidget(parent)
        editor.setStyleSheet("background-color: transparent")
        editor_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        editor_layout.setSpacing(0)
        editor_layout.setMargin(0)
        editor_layout.addWidget(self._line_edit)
        editor.setLayout(editor_layout)
        editor.setFocusPolicy(QtCore.Qt.StrongFocus)

        if index.isValid() and type(index.data()) == str:
            return editor

    def commit_editor(self):
        editor: QtCore.QObject = self.sender()
        self.commitData.emit(editor.parent())

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        # noinspection PyTypeChecker
        value: str = index.data(QtCore.Qt.DisplayRole)
        self._line_edit.setText(value)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:

        value: str = self._line_edit.text()
        model.setData(index, value, QtCore.Qt.EditRole | QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem,
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def eventFilter(self, editor: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if type(event) == QtGui.QKeyEvent and event.key() == QtCore.Qt.Key_Tab:
            # current_prop_table: PropertyTable = self.parent()
            # current_row: int = self._current_index.row()
            # print(current_prop_table.currentIndex().row(), self._current_index.row())
            #
            # new_index: QtCore.QModelIndex = current_prop_table.model().index(current_row + 1, 1)
            # setCurrentIndex(new_index)
            # print("New row:", current_prop_table.currentIndex().row(), current_prop_table.currentIndex().column())
            self.commitData.emit(editor.parent())
            self.closeEditor.emit(self._line_edit)
            print("Tab")

            return False

        else:
            return super().eventFilter(editor, event)

from PySide2 import QtCore, QtGui, QtWidgets
import re


class Delegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, owner, choices):
        super().__init__(owner)
        self.items = choices

    def paint(self, painter, option, index):
        if isinstance(self.parent(), QtWidgets.QAbstractItemView):
            self.parent().openPersistentEditor(index)
        super(Delegate, self).paint(painter, option, index)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        editor.currentIndexChanged.connect(self.commit_editor)
        editor.addItems(self.items)
        return editor

    def commit_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)

    def setEditorData(self, editor, index):
        value = index.data(QtCore.Qt.DisplayRole)
        num = self.items.index(value)
        editor.setCurrentIndex(num)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class Model(QtCore.QAbstractTableModel):
    ActiveRole = QtCore.Qt.UserRole + 1
    def __init__(self, datain, headerdata, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        super().__init__()
        self.arraydata = datain
        self.headerdata = headerdata

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return QtCore.QVariant(self.headerdata[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid(): return 0
        return len(self.arraydata)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid(): return 0
        if len(self.arraydata) > 0:
            return len(self.arraydata[0])
        return 0

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(self.arraydata[index.row()][index.column()])

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        r = re.compile(r"^[0-9]\d*(\.\d+)?$")
        if role == QtCore.Qt.EditRole and value != "" and 0 < index.column() < self.columnCount():
            if index.column() in (0, 1):
                self.arraydata[index.row()][index.column()] = value
                self.dataChanged.emit(index, index, (QtCore.Qt.DisplayRole, ))
                return True
            else:
                if index.column() == 2:
                    if r.match(value) and (0 < float(value) <= 1):
                        self.arraydata[index.row()][index.column()] = value
                        self.dataChanged.emit(index, index, (QtCore.Qt.DisplayRole, ))
                        return True
                else:
                    if r.match(value):
                        self.arraydata[index.row()][index.column()] = value
                        self.dataChanged.emit(index, index, (QtCore.Qt.DisplayRole, ))
                        return True
        return False

    def print_arraydata(self):
        print(self.arraydata)

    def insert_row(self, data, position, rows=1):
        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)
        for i, e in enumerate(data):
            self.arraydata.insert(i+position, e[:])
        self.endInsertRows()
        return True

    def remove_row(self, position, rows=1):
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
        self.arraydata = self.arraydata[:position] + self.arraydata[position + rows:]
        self.endRemoveRows()
        return True

    def append_row(self, data):
        self.insert_row([data], self.rowCount())


class Main(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # create table view:
        self.get_choices_data()
        self.get_table_data()
        self.tableview = self.createTable()
        self.tableview.model().rowsInserted.connect(lambda: QtCore.QTimer.singleShot(0, self.tableview.scrollToBottom))

        # Set the maximum value of row to the selected row
        self.selectrow = self.tableview.model().rowCount()

        # create buttons:
        self.addbtn = QtWidgets.QPushButton('Add')
        self.addbtn.clicked.connect(self.insert_row)
        self.deletebtn = QtWidgets.QPushButton('Delete')
        self.deletebtn.clicked.connect(self.remove_row)
        self.exportbtn = QtWidgets.QPushButton('Export')
        self.exportbtn.clicked.connect(self.export_tv)
        self.computebtn = QtWidgets.QPushButton('Compute')
        self.enablechkbox = QtWidgets.QCheckBox('Completed')

        # create label:
        self.lbltitle = QtWidgets.QLabel('Table')
        self.lbltitle.setFont(QtGui.QFont('Arial', 20))

        # create gridlayout
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self.exportbtn, 2, 2, 1, 1)
        grid_layout.addWidget(self.computebtn, 2, 3, 1, 1)
        grid_layout.addWidget(self.addbtn, 2, 4, 1, 1)
        grid_layout.addWidget(self.deletebtn, 2, 5, 1, 1)
        grid_layout.addWidget(self.enablechkbox, 2, 6, 1, 1, QtCore.Qt.AlignCenter)
        grid_layout.addWidget(self.tableview, 1, 0, 1, 7)
        grid_layout.addWidget(self.lbltitle, 0, 3, 1, 1, QtCore.Qt.AlignCenter)

        # initializing sub_layout
        self.title = 'Data Visualization Tool'
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, 1024, 576)
        self.showMaximized()
        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setLayout(grid_layout)
        self.setCentralWidget(self.centralwidget)

    def get_table_data(self):
        # set initial table values:
        self.tabledata = [['Name', self.choices[0], 0.0, 0.0, 0.0]]

    def get_choices_data(self):
        # set combo box choices:
        self.choices = ['type_1', 'type_2', 'type_3', 'type_4', 'type_5']

    def createTable(self):
        tv = QtWidgets.QTableView()
        # set header for columns:
        header = ['Name', 'Type', 'var1', 'var2', 'var3']

        tablemodel = Model(self.tabledata, header, self)
        tv.setModel(tablemodel)
        hh = tv.horizontalHeader()
        tv.resizeRowsToContents()
        # ItemDelegate for combo boxes
        tv.setItemDelegateForColumn(1, Delegate(tv, self.choices))
        return tv

    def export_tv(self):
        self.tableview.model().print_arraydata()

    def remove_row(self):
        r = self.tableview.currentIndex().row()
        self.tableview.model().remove_row(r)

    def insert_row(self):
        self.tableview.model().append_row(['Name', self.choices[0], 0.0, 0.0, 0.0])


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
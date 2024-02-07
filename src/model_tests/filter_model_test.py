from PySide2 import QtCore, QtGui, QtWidgets


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.proxyModel = QtCore.QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)

        self.sourceGroupBox = QtWidgets.QGroupBox("Original Model")
        self.proxyGroupBox = QtWidgets.QGroupBox("Sorted/Filtered Model")

        self.sourceView = QtWidgets.QTreeView()
        self.sourceView.setRootIsDecorated(False)
        self.sourceView.setAlternatingRowColors(True)

        self.proxyView = QtWidgets.QTreeView()
        self.proxyView.setRootIsDecorated(False)
        self.proxyView.setAlternatingRowColors(True)
        self.proxyView.setModel(self.proxyModel)
        self.proxyView.setSortingEnabled(True)

        self.sortCaseSensitivityCheckBox = QtWidgets.QCheckBox("Case sensitive sorting")
        self.filterCaseSensitivityCheckBox = QtWidgets.QCheckBox("Case sensitive filter")

        self.filterPatternLineEdit = QtWidgets.QLineEdit()
        self.filterPatternLabel = QtWidgets.QLabel("&Filter pattern:")
        self.filterPatternLabel.setBuddy(self.filterPatternLineEdit)

        self.filterSyntaxComboBox = QtWidgets.QComboBox()
        self.filterSyntaxComboBox.addItem("Regular expression", QtCore.QRegExp.RegExp)
        self.filterSyntaxComboBox.addItem("Wildcard", QtCore.QRegExp.Wildcard)
        self.filterSyntaxComboBox.addItem("Fixed string", QtCore.QRegExp.FixedString)
        self.filterSyntaxLabel = QtWidgets.QLabel("Filter &syntax:")
        self.filterSyntaxLabel.setBuddy(self.filterSyntaxComboBox)

        self.filterColumnComboBox = QtWidgets.QComboBox()
        self.filterColumnComboBox.addItem("Subject")
        self.filterColumnComboBox.addItem("Sender")
        self.filterColumnComboBox.addItem("Date")
        self.filterColumnLabel = QtWidgets.QLabel("Filter &column:")
        self.filterColumnLabel.setBuddy(self.filterColumnComboBox)

        self.filterPatternLineEdit.textChanged.connect(self.filter_reg_exp_changed)
        self.filterSyntaxComboBox.currentIndexChanged.connect(self.filter_reg_exp_changed)
        self.filterColumnComboBox.currentIndexChanged.connect(self.filter_column_changed)
        self.filterCaseSensitivityCheckBox.toggled.connect(self.filter_reg_exp_changed)
        self.sortCaseSensitivityCheckBox.toggled.connect(self.sort_changed)

        source_layout = QtWidgets.QHBoxLayout()
        source_layout.addWidget(self.sourceView)
        self.sourceGroupBox.setLayout(source_layout)

        proxy_layout = QtWidgets.QGridLayout()
        proxy_layout.addWidget(self.proxyView, 0, 0, 1, 3)
        proxy_layout.addWidget(self.filterPatternLabel, 1, 0)
        proxy_layout.addWidget(self.filterPatternLineEdit, 1, 1, 1, 2)
        proxy_layout.addWidget(self.filterSyntaxLabel, 2, 0)
        proxy_layout.addWidget(self.filterSyntaxComboBox, 2, 1, 1, 2)
        proxy_layout.addWidget(self.filterColumnLabel, 3, 0)
        proxy_layout.addWidget(self.filterColumnComboBox, 3, 1, 1, 2)
        proxy_layout.addWidget(self.filterCaseSensitivityCheckBox, 4, 0, 1, 2)
        proxy_layout.addWidget(self.sortCaseSensitivityCheckBox, 4, 2)
        self.proxyGroupBox.setLayout(proxy_layout)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.sourceGroupBox)
        main_layout.addWidget(self.proxyGroupBox)
        self.setLayout(main_layout)

        self.setWindowTitle("Basic Sort/Filter Model")
        self.resize(500, 450)

        self.proxyView.sortByColumn(1, QtCore.Qt.AscendingOrder)
        self.filterColumnComboBox.setCurrentIndex(1)

        self.filterPatternLineEdit.setText("Andy|Grace")
        self.filterCaseSensitivityCheckBox.setChecked(True)
        self.sortCaseSensitivityCheckBox.setChecked(True)

    def set_source_model(self, model):
        self.proxyModel.setSourceModel(model)
        self.sourceView.setModel(model)

    def filter_reg_exp_changed(self):
        syntax_nr = self.filterSyntaxComboBox.itemData(self.filterSyntaxComboBox.currentIndex())
        syntax = QtCore.QRegExp.PatternSyntax(syntax_nr)

        if self.filterCaseSensitivityCheckBox.isChecked():
            case_sensitivity = QtCore.Qt.CaseSensitive
        else:
            case_sensitivity = QtCore.Qt.CaseInsensitive

        reg_exp = QtCore.QRegExp(self.filterPatternLineEdit.text(), case_sensitivity, syntax)
        self.proxyModel.setFilterRegExp(reg_exp)

    def filter_column_changed(self):
        self.proxyModel.setFilterKeyColumn(self.filterColumnComboBox.currentIndex())

    def sort_changed(self):
        if self.sortCaseSensitivityCheckBox.isChecked():
            case_sensitivity = QtCore.Qt.CaseSensitive
        else:
            case_sensitivity = QtCore.Qt.CaseInsensitive

        self.proxyModel.setSortCaseSensitivity(case_sensitivity)


def add_mail(model, subject, sender, date):
    model.insertRow(0)
    model.setData(model.index(0, 0), subject)
    model.setData(model.index(0, 1), sender)
    model.setData(model.index(0, 2), date)


def create_mail_model(parent):
    model = QtGui.QStandardItemModel(0, 3, parent)

    model.setHeaderData(0, QtCore.Qt.Horizontal, "Subject")
    model.setHeaderData(1, QtCore.Qt.Horizontal, "Sender")
    model.setHeaderData(2, QtCore.Qt.Horizontal, "Date")

    add_mail(model, "Happy New Year!", "Grace K. <grace@software-inc.com>",
             QtCore.QDateTime(QtCore.QDate(2006, 12, 31), QtCore.QTime(17, 3)))
    add_mail(model, "Radically new concept", "Grace K. <grace@software-inc.com>",
             QtCore.QDateTime(QtCore.QDate(2006, 12, 22), QtCore.QTime(9, 44)))
    add_mail(model, "Accounts", "pascale@nospam.com",
             QtCore.QDateTime(QtCore.QDate(2006, 12, 31), QtCore.QTime(12, 50)))
    add_mail(model, "Expenses", "Joe Blogs <joe@bloggs.com>",
             QtCore.QDateTime(QtCore.QDate(2006, 12, 25), QtCore.QTime(11, 39)))
    add_mail(model, "Re: Expenses", "Andy <andy@nospam.com>",
             QtCore.QDateTime(QtCore.QDate(2007, 1, 2), QtCore.QTime(16, 5)))
    add_mail(model, "Re: Accounts", "Joe Blogs <joe@bloggs.com>",
             QtCore.QDateTime(QtCore.QDate(2007, 1, 3), QtCore.QTime(14, 18)))
    add_mail(model, "Re: Accounts", "Andy <andy@nospam.com>",
             QtCore.QDateTime(QtCore.QDate(2007, 1, 3), QtCore.QTime(14, 26)))
    add_mail(model, "Sports", "Linda Smith <linda.smith@nospam.com>",
             QtCore.QDateTime(QtCore.QDate(2007, 1, 5), QtCore.QTime(11, 33)))
    add_mail(model, "AW: Sports", "Rolf Pig <rolfn@nospam.com>",
             QtCore.QDateTime(QtCore.QDate(2007, 1, 5), QtCore.QTime(12, 0)))
    add_mail(model, "RE: Sports", "Petra Schmidt <petras@nospam.com>",
             QtCore.QDateTime(QtCore.QDate(2007, 1, 5), QtCore.QTime(12, 1)))

    return model


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.set_source_model(create_mail_model(window))
    window.show()
    sys.exit(app.exec_())

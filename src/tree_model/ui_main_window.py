from typing import Optional

from PySide2 import QtCore, QtWidgets


class UiMainWindow:
    def __init__(self):
        self.central_widget: Optional[QtWidgets.QWidget] = None
        self.vbox_layout: Optional[QtWidgets.QVBoxLayout] = None
        self.view: Optional[QtWidgets.QTreeView] = None
        self.menubar: Optional[QtWidgets.QMenuBar] = None
        self.file_menu: Optional[QtWidgets.QMenu] = None
        self.actions_menu: Optional[QtWidgets.QMenu] = None
        self.statusbar: Optional[QtWidgets.QStatusBar] = None
        self.exit_action: Optional[QtWidgets.QAction] = None
        self.insert_row_action: Optional[QtWidgets.QAction] = None
        self.remove_row_action: Optional[QtWidgets.QAction] = None
        self.insert_column_action: Optional[QtWidgets.QAction] = None
        self.remove_column_action: Optional[QtWidgets.QAction] = None
        self.insert_child_action: Optional[QtWidgets.QAction] = None

    def setup_ui(self, main_window):
        main_window.setObjectName("MainWindow")
        main_window.resize(573, 468)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("centralwidget")
        self.vbox_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.vbox_layout.setContentsMargins(0, 0, 0, 0)
        self.vbox_layout.setSpacing(0)
        self.vbox_layout.setObjectName("vboxlayout")
        self.view = QtWidgets.QTreeView(self.central_widget)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.view.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.view.setAnimated(False)
        self.view.setAllColumnsShowFocus(True)
        self.view.setObjectName("view")
        self.vbox_layout.addWidget(self.view)
        main_window.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 573, 31))
        self.menubar.setObjectName("menubar")
        self.file_menu = QtWidgets.QMenu(self.menubar)
        self.file_menu.setObjectName("fileMenu")
        self.actions_menu = QtWidgets.QMenu(self.menubar)
        self.actions_menu.setObjectName("actionsMenu")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)
        self.exit_action = QtWidgets.QAction(main_window)
        self.exit_action.setObjectName("exitAction")
        self.insert_row_action = QtWidgets.QAction(main_window)
        self.insert_row_action.setObjectName("insertRowAction")
        self.remove_row_action = QtWidgets.QAction(main_window)
        self.remove_row_action.setObjectName("removeRowAction")
        self.insert_column_action = QtWidgets.QAction(main_window)
        self.insert_column_action.setObjectName("insertColumnAction")
        self.remove_column_action = QtWidgets.QAction(main_window)
        self.remove_column_action.setObjectName("removeColumnAction")
        self.insert_child_action = QtWidgets.QAction(main_window)
        self.insert_child_action.setObjectName("insertChildAction")
        self.file_menu.addAction(self.exit_action)
        self.actions_menu.addAction(self.insert_row_action)
        self.actions_menu.addAction(self.insert_column_action)
        self.actions_menu.addSeparator()
        self.actions_menu.addAction(self.remove_row_action)
        self.actions_menu.addAction(self.remove_column_action)
        self.actions_menu.addSeparator()
        self.actions_menu.addAction(self.insert_child_action)
        self.menubar.addAction(self.file_menu.menuAction())
        self.menubar.addAction(self.actions_menu.menuAction())

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        main_window.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Editable Tree Model", None))
        self.file_menu.setTitle(QtWidgets.QApplication.translate("MainWindow", "&File", None))
        self.actions_menu.setTitle(QtWidgets.QApplication.translate("MainWindow", "&Actions", None))
        self.exit_action.setText(QtWidgets.QApplication.translate("MainWindow", "E&xit", None))
        self.exit_action.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Q", None))
        self.insert_row_action.setText(QtWidgets.QApplication.translate("MainWindow", "Insert Row", None))
        self.insert_row_action.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+I, R", None))
        self.remove_row_action.setText(QtWidgets.QApplication.translate("MainWindow", "Remove Row", None))
        self.remove_row_action.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+R, R", None))
        self.insert_column_action.setText(QtWidgets.QApplication.translate("MainWindow", "Insert Column", None))
        self.insert_column_action.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+I, C", None))
        self.remove_column_action.setText(QtWidgets.QApplication.translate("MainWindow", "Remove Column", None))
        self.remove_column_action.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+R, C", None))
        self.insert_child_action.setText(QtWidgets.QApplication.translate("MainWindow", "Insert Child", None))
        self.insert_child_action.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+N", None))

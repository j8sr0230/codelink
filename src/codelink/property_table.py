from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class PropertyTable(QtWidgets.QTableView):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self._font: QtGui.QFont = QtGui.QFont("Sans Serif", 10)

        self.setFont(self._font)
        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setEditTriggers(QtWidgets.QTableView.AnyKeyPressed | QtWidgets.QTableView.DoubleClicked)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setFont(self._font)
        self.verticalHeader().hide()

        self.setStyleSheet("""
            QTableView {
                color: #E5E5E5;
                selection-color: #E5E5E5;
                background-color: #282828;
                alternate-background-color: #2B2B2B;
                gridline-color: black;
                padding: 0px;
                margin: 0px;
                border: none;
                border-radius: 0px;
                outline: none;
            }
            QHeaderView::section:horizontal {
                color: #E5E5E5;
                background-color: #3D3D3D;
                margin: 0px;
                padding: 0px;
                border-top: none;
                border-bottom: 1px solid black;
                border-left: none;
                border-right: 1px solid black;
            }
            QTableView::item {
                border: none;
                margin: 0px;
                padding: 0px;
            }
            QTableView::item:selected {
                background-color: #545454;
            }
            QTableView::item:hover {
                border: none;
            }
            QTableView::item:focus {
                border: none;
            }
        """)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Tab:
            new_row = self.currentIndex().row() + 1
            if new_row == self.model().rowCount():
                new_row = 0
            new_index = self.model().index(new_row, 1)
            self.setCurrentIndex(new_index)

        else:
            super().keyPressEvent(event)

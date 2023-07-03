from typing import Optional, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class PropertyTable(QtWidgets.QTableView):
    table_top_reached: QtCore.Signal = QtCore.Signal(QtWidgets.QTableView)
    table_bottom_reached: QtCore.Signal = QtCore.Signal(QtWidgets.QTableView)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # Widget setup
        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setEditTriggers(QtWidgets.QTableView.AnyKeyPressed | QtWidgets.QTableView.DoubleClicked)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().hide()

    # --------------- Overwrites ---------------

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Tab or event.key() == QtCore.Qt.Key_Down:
            new_row = self.currentIndex().row() + 1

            if new_row == self.model().rowCount():
                cast(QtCore.SignalInstance, self.table_bottom_reached).emit(self)
            else:
                new_index = self.model().index(new_row, 1)
                self.setCurrentIndex(new_index)

        elif event.key() == QtCore.Qt.Key_Up:
            new_row = self.currentIndex().row() - 1

            if new_row == -1:
                cast(QtCore.SignalInstance, self.table_top_reached).emit(self)
            else:
                new_index = self.model().index(new_row, 1)
                self.setCurrentIndex(new_index)

        else:
            super().keyPressEvent(event)

from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class PropertyTable(QtWidgets.QTableView):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        table_top_reached: QtCore.Signal = QtCore.Signal(QtWidgets.QTableView)
        table_bottom_reached: QtCore.Signal = QtCore.Signal(QtWidgets.QTableView)

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
        scroll_area: QtWidgets.QScrollArea = self.parent().parent().parent()

        if event.key() == QtCore.Qt.Key_Tab or event.key() == QtCore.Qt.Key_Down:
            new_row = self.currentIndex().row() + 1

            if new_row == self.model().rowCount():
                # Switch to next property table and select first row
                self.clearFocus()
                self.clearSelection()
                table_bottom_reached.emit(self)
                next_table_view: PropertyTable = self.parent().get_next_prop_table(self)
                next_table_view.setFocus()
                next_table_view.setCurrentIndex(next_table_view.model().index(0, 1))

            else:
                # Stay in current property table and increment row selection
                new_index = self.model().index(new_row, 1)
                self.setCurrentIndex(new_index)

            scroll_area.ensureWidgetVisible(self)

        elif event.key() == QtCore.Qt.Key_Up:
            new_row = self.currentIndex().row() - 1

            if new_row == -1:
                # Switch to next property table and select first row
                self.clearFocus()
                self.clearSelection()
                table_top_reached_reached.emit(self)
                next_table_view: PropertyTable = self.parent().get_prev_prop_table(self)
                next_table_view.setFocus()
                next_table_view.setCurrentIndex(next_table_view.model().index(
                    next_table_view.model().rowCount() - 1, 1)
                )

            else:
                # Stay in current property table and increment row selection
                new_index = self.model().index(new_row, 1)
                self.setCurrentIndex(new_index)

            scroll_area.ensureWidgetVisible(self)

        else:
            super().keyPressEvent(event)

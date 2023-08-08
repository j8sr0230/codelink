from typing import Optional

import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class NumberInputWidget(QtWidgets.QLineEdit):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.matches(QtGui.QKeySequence.Undo) or event.matches(QtGui.QKeySequence.Redo):
            event.ignore()
        else:
            super().keyPressEvent(event)


class OptionBoxWidget(QtWidgets.QComboBox):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self._last_index: int = 0

    @property
    def last_index(self) -> int:
        return self._last_index

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self._last_index: int = self.currentIndex()
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.matches(QtGui.QKeySequence.Undo) or event.matches(QtGui.QKeySequence.Redo):
            event.ignore()
        else:
            super().keyPressEvent(event)

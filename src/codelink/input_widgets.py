from typing import Optional

import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class NumberInputWidget(QtWidgets.QLineEdit):
    def __init__(self, parent: Optional[QtWidgets.QWidget]):
        super().__init__(parent)

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        super().focusOutEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.matches(QtGui.QKeySequence.Undo) or event.matches(QtGui.QKeySequence.Redo):
            event.ignore()
        else:
            super().keyPressEvent(event)

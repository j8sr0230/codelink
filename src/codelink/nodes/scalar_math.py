from __future__ import annotations
from typing import Optional

import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem


class ScalarMath(NodeItem):
    REG_NAME: str = "Scalar Math"

    def __init__(self, undo_stack: Optional[QtWidgets.QUndoStack] = None,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(undo_stack, parent)
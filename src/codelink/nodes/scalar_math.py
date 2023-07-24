from __future__ import annotations
from typing import Optional
import importlib

import PySide2.QtWidgets as QtWidgets


node_item_cls: type = getattr(importlib.import_module("node_item"), "NodeItem")


class ScalarMath(node_item_cls):
    def __init__(self, undo_stack: Optional[QtWidgets.QUndoStack] = None,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(undo_stack, parent)

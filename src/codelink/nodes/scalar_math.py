from __future__ import annotations
from typing import Optional

import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem
# from socket_widget import SocketWidget


class ScalarMath(NodeItem):
    REG_NAME: str = "Scalar Math"

    def __init__(self, undo_stack: Optional[QtWidgets.QUndoStack] = None,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(undo_stack, parent)

        # self.add_socket_widget(SocketWidget(label="Res", is_input=False, parent_node=self))
        # self.add_socket_widget(SocketWidget(label="B", is_input=True, parent_node=self))
        # self.add_socket_widget(SocketWidget(label="A", is_input=True, parent_node=self))

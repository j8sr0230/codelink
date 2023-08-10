from __future__ import annotations
from typing import Optional

import awkward as ak

import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem
from socket_widget import SocketWidget


class BroadCastArray(NodeItem):
    REG_NAME: str = "Broadcast Array"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, parent)

        # Node name
        self._prop_model.properties["Name"] = "Broadcast Array"

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            SocketWidget(undo_stack=self._undo_stack, label="A 1", is_input=True, parent_node=self),
            SocketWidget(undo_stack=self._undo_stack, label="A 2", is_input=True, parent_node=self),
            SocketWidget(undo_stack=self._undo_stack, label="BA 1", is_input=False, parent_node=self),
            SocketWidget(undo_stack=self._undo_stack, label="BA 2", is_input=False, parent_node=self)
        ]
        for widget in self._socket_widgets:
            self._content_widget.hide()
            self._content_layout.addWidget(widget)
            self._content_widget.show()

        self.update_all()

        # Socket-wise node methods
        self._evals: list[object] = [self.eval_socket_1, self.eval_socket_2]

    # --------------- Node eval methods ---------------

    def eval_socket_1(self, *args) -> ak.Array:
        try:
            result: ak.Array = ak.broadcast_arrays(args[0], args[1])[0]

            if result.ndim > 1:
                result: ak.Array = ak.flatten(result, axis=1)

            return result
        except ValueError as e:
            print(e)

    def eval_socket_2(self, *args) -> ak.Array:
        try:
            result: ak.Array = ak.broadcast_arrays(args[0], args[1])[1]

            if result.ndim > 1:
                result: ak.Array = ak.flatten(result, axis=1)

            return result
        except ValueError as e:
            print(e)

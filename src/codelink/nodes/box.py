from __future__ import annotations
from typing import Optional

import awkward as ak
import FreeCAD
import Part

import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem
from socket_widget import SocketWidget
from number_line import NumberLine
from shape import Shape


class Box(NodeItem):
    REG_NAME: str = "Box"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, parent)

        # Node name
        self._prop_model.properties["Name"] = "Box"

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            NumberLine(undo_stack=self._undo_stack, label="L", is_input=True, data=10., parent_node=self),
            NumberLine(undo_stack=self._undo_stack, label="W", is_input=True, data=10., parent_node=self),
            NumberLine(undo_stack=self._undo_stack, label="H", is_input=True, data=10., parent_node=self),
            Shape(undo_stack=self._undo_stack, label="Res", is_input=False, parent_node=self)
        ]
        for widget in self._socket_widgets:
            self._content_widget.hide()
            self._content_layout.addWidget(widget)
            self._content_widget.show()

        self.update_all()

        # Socket-wise node methods
        self._evals: list[object] = [self.eval_socket_1]

    # --------------- Node eval methods ---------------

    def eval_socket_1(self, *args) -> list[Part.Shape]:
        print("args", args)
        try:
            result: ak.Array = ak.Array(args[0]) + ak.Array(args[1])

            if result.ndim > 1:
                result: ak.Array = ak.flatten(result, axis=1)

            return result.to_list()
        except ValueError as e:
            print(e)

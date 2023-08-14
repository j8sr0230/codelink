from __future__ import annotations
from typing import Optional

import awkward as ak

import FreeCAD
import Part

import PySide2.QtWidgets as QtWidgets

from utils import map_objects, zip_nested
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
        self._evals: list[object] = [self.eval_socket_0]

    # --------------- Node eval methods ---------------

    @staticmethod
    def make_box(parameter_zip: tuple) -> Part.Shape:
        width: float = parameter_zip[0]
        length: float = parameter_zip[1]
        height: float = parameter_zip[2]
        return Part.makeBox(width, length, height)

    def eval_socket_0(self, *args) -> list:
        try:
            # Collect and pre-process input data
            length: list = args[0]
            width: list = args[1]
            height: list = args[2]

            #  Broadcast and calculate result
            broadcasted_input: list = ak.broadcast_arrays(length, width, height)
            zipped_input: list = zip_nested(
                broadcasted_input[0].to_list(),
                broadcasted_input[1].to_list(),
                broadcasted_input[2].to_list())
            result: list = list(map_objects(zipped_input, tuple, self.make_box))

            # Post-process result
            result: list = self.output_socket_widgets[0].perform_socket_operation(result)

            return result
        except ValueError as e:
            print(e)

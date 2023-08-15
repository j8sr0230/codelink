from __future__ import annotations
from typing import Optional
import warnings

import awkward as ak

# noinspection PyUnresolvedReferences
import FreeCAD
import Part

import PySide2.QtWidgets as QtWidgets

from utils import map_objects, zip_nested
from node_item import NodeItem
from socket_widget import SocketWidget
from number_line import NumberLine
from shape import Shape


class Sphere(NodeItem):
    REG_NAME: str = "Sphere"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, parent)

        # Node name
        self._prop_model.properties["Name"] = "Sphere"

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

        # Socket-wise node eval methods
        self._evals: list[object] = [self.eval_socket_0]

    # --------------- Node eval methods ---------------

    @staticmethod
    def make_box(parameter_zip: tuple) -> Part.Shape:
        width: float = parameter_zip[0]
        length: float = parameter_zip[1]
        height: float = parameter_zip[2]
        return Part.makeBox(width, length, height)

    def eval_socket_0(self, *args) -> list:
        result: list = [Part.Shape()]

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    length: list = self.input_data(0, args)
                    width: list = self.input_data(1, args)
                    height: list = self.input_data(2, args)

                    broadcasted_input: list = ak.broadcast_arrays(length, width, height)
                    zipped_input: list = zip_nested(
                        broadcasted_input[0].to_list(),
                        broadcasted_input[1].to_list(),
                        broadcasted_input[2].to_list())
                    result: list = list(map_objects(zipped_input, tuple, self.make_box))
                    self._is_dirty: bool = False

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

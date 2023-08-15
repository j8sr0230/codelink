from __future__ import annotations
from typing import Optional
import warnings

# noinspection PyUnresolvedReferences
import FreeCAD as App
import FreeCADGui as Gui
import Part

import PySide2.QtWidgets as QtWidgets

from utils import flatten
from node_item import NodeItem
from socket_widget import SocketWidget
from shape import Shape


class CompoundViewer(NodeItem):
    REG_NAME: str = "CViewer"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, parent)

        # Node name
        self._prop_model.properties["Name"] = "CViewer"

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            Shape(undo_stack=self._undo_stack, label="Shp", is_input=True, data=str(Part.Shape()), parent_node=self),
            Shape(undo_stack=self._undo_stack, label="Shp", is_input=False, parent_node=self)
        ]
        for widget in self._socket_widgets:
            self._content_widget.hide()
            self._content_layout.addWidget(widget)
            self._content_widget.show()

        self.update_all()

        # Socket-wise node eval methods
        self._evals: list[object] = [self.eval_socket_0]

        self._compound_obj: Optional[Part.Compound] = None

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
                    if hasattr(Gui, "ActiveDocument"):
                        shapes: list = self.input_data(0, args)
                        flat_shapes: list = list(flatten(shapes))
                        self._compound_obj = App.ActiveDocument.addObject("Part::Feature", "CViewer")
                        self._compound_obj.setPropertyStatus("Shape", ["Transient", "Output"])
                        self._is_dirty: bool = False
                    else:
                        self._is_dirty: bool = True

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

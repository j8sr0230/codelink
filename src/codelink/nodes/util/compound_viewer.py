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
            Shape(undo_stack=self._undo_stack, label="Shp", is_input=True,  data=str(Part.Shape()),
                  parent_node=self),
            Shape(undo_stack=self._undo_stack, label="Shp", is_input=False, parent_node=self)
        ]
        for widget in self._socket_widgets:
            self._content_widget.hide()
            self._content_layout.addWidget(widget)
            self._content_widget.show()

        self.update_all()

        # Socket-wise node eval methods
        self._evals: list[object] = [self.eval_socket_0]

        self._compound_name: str = ""

    @property
    def compound_name(self) -> str:
        return self._compound_name

    @compound_name.setter
    def compound_name(self, value: str) -> None:
        self._compound_name: str = value

    # --------------- Node eval methods ---------------

    def eval_socket_0(self, *args) -> list:
        result: list = [Part.Shape()]

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    shapes: list = self.input_data(0, args)
                    if hasattr(Gui, "ActiveDocument"):
                        flat_shapes: list = [shape for shape in flatten(shapes) if len(shape.Vertexes) > 0]
                        if len(flat_shapes) > 0:
                            if self._compound_name == "":
                                compound_obj = App.ActiveDocument.addObject("Part::Feature", "CViewer")
                                compound_obj.setPropertyStatus("Shape", ["Transient", "Output"])
                                self._compound_name: str = compound_obj.Name
                            else:
                                compound_obj = App.ActiveDocument.getObject(self._compound_name)

                            compound_obj.Shape = Part.makeCompound(flat_shapes)
                            App.activeDocument().recompute()
                        else:
                            self.on_remove()

                    self._is_dirty: bool = False
                    result: list = shapes

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

    def on_remove(self):
        if hasattr(Gui, "ActiveDocument") and self._compound_name != "":
            if App.ActiveDocument.getObject(self._compound_name) is not None:
                compound_object: App.DocumentObject = App.ActiveDocument.getObject(self._compound_name)
                for obj in App.ActiveDocument.Objects:
                    if "Base" in obj.PropertiesList and obj.getPropertyByName("Base") == compound_object:
                        App.ActiveDocument.removeObject(obj.Name)

                App.ActiveDocument.removeObject(self._compound_name)
            self._compound_name: str = ""

    def __getstate__(self) -> dict:
        data_dict: dict = super().__getstate__()
        data_dict["Compound Name"] = self._compound_name
        return data_dict

    def __setstate__(self, state: dict):
        super().__setstate__(state)
        self._compound_name: str = state["Compound Name"]
        self.update()

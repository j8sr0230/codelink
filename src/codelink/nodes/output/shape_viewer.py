# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2023 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import warnings
import inspect

# noinspection PyUnresolvedReferences
import FreeCAD as App
import FreeCADGui as Gui
import Part

import PySide2.QtWidgets as QtWidgets

from nested_data import NestedData
from node_item import NodeItem
from sockets.shape_none import ShapeNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class ShapeViewer(NodeItem):
    REG_NAME: str = "Shape Viewer"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Shp", content_value="<No Input>", is_input=True,
                      parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Shp", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]

        self._compound_name: str = ""

    @property
    def compound_name(self) -> str:
        return self._compound_name

    @compound_name.setter
    def compound_name(self, value: str) -> None:
        self._compound_name: str = value

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> NestedData:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        nested_data: NestedData = self.input_data(0, args)

                        if hasattr(Gui, "ActiveDocument"):
                            flat_shapes: list[Part.Shape] = nested_data.data

                            if len(flat_shapes) > 0 and len(flat_shapes[0].Vertexes) > 0:
                                if self._compound_name == "":
                                    compound_obj = App.ActiveDocument.addObject("Part::Feature", "CViewer")
                                    self._compound_name: str = compound_obj.Name
                                else:
                                    if App.ActiveDocument.getObject(self._compound_name) is not None:
                                        compound_obj = App.ActiveDocument.getObject(self._compound_name)
                                    else:
                                        compound_obj = App.ActiveDocument.addObject("Part::Feature", "CViewer")

                                compound_obj.Shape = Part.makeCompound(flat_shapes)
                                compound_obj.setPropertyStatus("Shape", ["Transient", "Output"])
                                App.activeDocument().recompute()
                            else:
                                self.on_remove()

                        result: NestedData = nested_data

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)
                        print("Shape viewer executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

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

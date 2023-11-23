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
from typing import TYPE_CHECKING, Optional, cast
import importlib
import warnings
import inspect

import numpy as np
import awkward as ak

# noinspection PyUnresolvedReferences
import FreeCAD
import Part

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from nested_data import NestedData
from utils import map_re
from node_item import NodeItem
from input_widgets import OptionBoxWidget
from sockets.shape_none import ShapeNone
from sockets.value_line import ValueLine
from sockets.vector_none import VectorNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class Voronoi(NodeItem):
    REG_NAME: str = "Voronoi"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget()
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Face", "Solid"])
        for option_idx in range(self._option_box.count()):
            self._option_box.model().setData(self._option_box.model().index(option_idx, 0), QtCore.QSize(160, 24),
                                             QtCore.Qt.SizeHintRole)

        item_list_view: QtWidgets.QListView = cast(QtWidgets.QListView, self._option_box.view())
        item_list_view.setSpacing(2)
        self._content_widget.hide()
        self._content_layout.addWidget(self._option_box)
        self._content_widget.show()

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Shape", content_value="<No Input>", is_input=True,
                      parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Position", content_value="<No Input>", is_input=True,
                       parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Mode", content_value=10., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Scale", content_value=1., is_input=True,
                      parent_node=self),
            ShapeNone(undo_stack=self._undo_stack, name="Voronoi", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    def update_socket_widgets(self) -> None:
        # Hack to prevent cyclic imports
        set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")
        execute_dag_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "EmitDagChangedCommand")

        last_option_index: int = self._option_box.last_index
        current_option_index: int = self._option_box.currentIndex()

        self._undo_stack.beginMacro("Changes option box")
        self._undo_stack.push(execute_dag_cmd_cls(self.scene(), self))
        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )
        self._undo_stack.push(execute_dag_cmd_cls(self.scene(), self, on_redo=True))
        self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> ak.Array:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        shape: NestedData = self.input_data(0, args)
                        position: ak.Array = self.input_data(1, args)
                        mode: ak.Array = self.input_data(2, args)
                        scale: ak.Array = self.input_data(3, args)

                        data_structure: ak.Array = ak.max(ak.ones_like(position.x), axis=-1)
                        data_structure.show()

                        nested_params: list[tuple[float, float, float]] = ak.to_list(
                            ak.zip([shape.structure, position.x, mode, scale], right_broadcast=True)
                        )

                        nested_params: list[tuple[float, float, float]] = map_re(
                            lambda t: (shape.data[t[0]], t[1], t[2], t[3]), nested_params
                        )
                        print(nested_params)

                        # if self._option_box.currentText() == "Face":
                        #     result: ak.Array = ak.Array(map_re(self.populate_positions_face, nested_params))
                        #
                        # elif self._option_box.currentText() == "Solid":
                        #     result: ak.Array = ak.Array(map_re(self.populate_positions_solid, nested_params))
                        #
                        # result: ak.Array = ak.flatten(result, axis=-1)

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        # self._cache[cache_idx] = self.output_data(0, result)
                        print("Voronoi executed")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

# --------------- Serialization ---------------

    def __getstate__(self) -> dict:
        data_dict: dict = super().__getstate__()
        data_dict["Option Idx"] = self._option_box.currentIndex()
        return data_dict

    def __setstate__(self, state: dict):
        super().__setstate__(state)
        self._option_box.blockSignals(True)
        self._option_box.setCurrentIndex(state["Option Idx"])
        self._option_box.blockSignals(False)
        self.update()

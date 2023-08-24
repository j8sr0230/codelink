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

import awkward as ak
import numpy as np

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from utils import map_objects
from node_item import NodeItem
from input_widgets import OptionBoxWidget
from value_line import ValueLine

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class ScalarTrigonometric(NodeItem):
    REG_NAME: str = "Scalar Trigonometric"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget()
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Sin", "Cos", "Tan", "ASin", "ACos", "ATan"])
        item_list_view: QtWidgets.QListView = cast(QtWidgets.QListView, self._option_box.view())
        item_list_view.setSpacing(2)
        self._content_widget.hide()
        self._content_layout.addWidget(self._option_box)
        self._content_widget.show()

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ValueLine(undo_stack=self._undo_stack, name="Value", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Res", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]
        for widget in self._socket_widgets:
            self._content_widget.hide()
            self._content_layout.addWidget(widget)
            self._content_widget.show()

        self.update_all()

        # Socket-wise node eval methods
        self._evals: list[object] = [self.eval_socket_0]

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    def update_socket_widgets(self):
        # Hack to prevent cyclic imports
        set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")

        last_option_index: int = self._option_box.last_index
        current_option_index: int = self._option_box.currentIndex()

        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )

    # --------------- Node eval methods ---------------

    def eval_socket_0(self, *args) -> list:
        result: ak.Array = ak.Array([0])

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    a: list = self.input_data(0, args)

                    if self._option_box.currentText() == "Sin":
                        result: list = list(map_objects(a, float, np.sin))

                    elif self._option_box.currentText() == "Cos":
                        result: list = list(map_objects(a, float, np.cos))

                    elif self._option_box.currentText() == "Tan":
                        result: list = list(map_objects(a, float, np.tan))

                    elif self._option_box.currentText() == "ASin":
                        result: list = list(map_objects(a, float, np.arcsin))

                    elif self._option_box.currentText() == "ACos":
                        result: list = list(map_objects(a, float, np.arccos))

                    elif self._option_box.currentText() == "ATan":
                        result: list = list(map_objects(a, float, np.arctan))

                    self._is_dirty: bool = False

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

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

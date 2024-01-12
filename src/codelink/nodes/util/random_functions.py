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
import time

import awkward as ak
import numpy as np

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from utils import unflatten_array_like, flatten_record, unflatten_record_like
from node_item import NodeItem
from input_widgets import OptionBoxWidget
from sockets.value_line import ValueLine
from sockets.bool_checkbox import BoolCheckBox
from sockets.vector_none import VectorNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = True


class RandomFunctions(NodeItem):
    REG_NAME: str = "Random Functions"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget(undo_stack)
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Value", "Boolean", "Vector"])
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
            ValueLine(undo_stack=self._undo_stack, name="Template", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Min", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Max", content_value=1., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Seed", content_value=.0, is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Random", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    def update_socket_widgets(self) -> None:
        # Hack to prevent cyclic imports
        add_socket_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "AddSocketCommand")
        remove_socket_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "RemoveSocketCommand")
        remove_edge_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "RemoveEdgeCommand")
        set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")
        emit_dag_changed_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "EmitDagChangedCommand")

        last_option_index: int = self._option_box.last_index
        current_option_name: str = self._option_box.currentText()
        current_option_index: int = self._option_box.currentIndex()

        self._undo_stack.beginMacro("Changes option box")
        self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self))

        if current_option_name in ("Boolean",):
            for idx in (4, 2, 1, 0):
                remove_socket: SocketWidget = self._socket_widgets[idx]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))
                self._undo_stack.push(remove_socket_cmd_cls(self, idx))

            new_template: BoolCheckBox = BoolCheckBox(
                undo_stack=self._undo_stack, name="Template", content_value=True, is_input=True, parent_node=self
            )
            insert_idx: int = 0
            self._undo_stack.push(add_socket_cmd_cls(self, new_template, insert_idx))

            new_result: BoolCheckBox = BoolCheckBox(
                undo_stack=self._undo_stack, name="Random", content_value="<No Input>", is_input=False,
                parent_node=self)
            insert_idx: int = 2
            self._undo_stack.push(add_socket_cmd_cls(self, new_result, insert_idx))

        else:
            if len(self.input_socket_widgets) < 4:
                new_min: ValueLine = ValueLine(
                    undo_stack=self._undo_stack, name="Min", content_value=.0, is_input=True, parent_node=self
                )
                insert_idx: int = 1
                self._undo_stack.push(add_socket_cmd_cls(self, new_min, insert_idx))

                new_max: ValueLine = ValueLine(
                    undo_stack=self._undo_stack, name="Max", content_value=1., is_input=True, parent_node=self
                )
                insert_idx: int = 2
                self._undo_stack.push(add_socket_cmd_cls(self, new_max, insert_idx))

            for idx in (0, 3):
                remove_socket: SocketWidget = self._socket_widgets[idx]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))

                self._undo_stack.push(remove_socket_cmd_cls(self, idx))

            if current_option_name in ("Value", ):
                new_template: ValueLine = ValueLine(
                    undo_stack=self._undo_stack, name="Template", content_value=.0, is_input=True, parent_node=self
                )
                insert_idx: int = 0
                self._undo_stack.push(add_socket_cmd_cls(self, new_template, insert_idx))

                new_result: ValueLine = ValueLine(
                    undo_stack=self._undo_stack, name="Random", content_value="<No Input>", is_input=False,
                    parent_node=self
                )
                insert_idx: int = 4
                self._undo_stack.push(add_socket_cmd_cls(self, new_result, insert_idx))

            if current_option_name in ("Vector",):
                new_template: VectorNone = VectorNone(
                    undo_stack=self._undo_stack, name="Template", content_value="<No Input>", is_input=True,
                    parent_node=self
                )
                insert_idx: int = 0
                self._undo_stack.push(add_socket_cmd_cls(self, new_template, insert_idx))

                new_result: VectorNone = VectorNone(
                    undo_stack=self._undo_stack, name="Random", content_value="<No Input>", is_input=False,
                    parent_node=self)
                insert_idx: int = 4
                self._undo_stack.push(add_socket_cmd_cls(self, new_result, insert_idx))

        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )
        self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self, on_redo=True))
        self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> ak.Array:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        template: ak.Array = self.input_data(0, args)

                        if DEBUG:
                            x: float = time.time()

                        if self._option_box.currentText() == "Value":
                            lower_limit: ak.Array = self.input_data(1, args)
                            upper_limit: ak.Array = self.input_data(2, args)
                            seed: ak.Array = self.input_data(3, args)

                            np.random.seed(int(ak.flatten(seed, axis=None)[0]))

                            broadcasted_params: ak.Array = ak.zip({"template": 0, "min": lower_limit,
                                                                   "max": upper_limit}, right_broadcast=True)
                            flat_params: ak.Array = flatten_record(nested_record=broadcasted_params, as_tuple=True)

                            template_len: int = ak.num(ak.flatten(template, axis=None), axis=0)
                            result_list: list[ak.Array] = []
                            for param_tuple in flat_params:
                                flat_rand: np.ndarray = np.random.randint(
                                    param_tuple["1"], param_tuple["2"] + 1,  template_len
                                )
                                result_list.append(unflatten_array_like(ak.from_numpy(flat_rand), template))

                            result: ak.Array = ak.concatenate(result_list, axis=0)

                        elif self._option_box.currentText() == "Boolean":
                            seed: ak.Array = self.input_data(1, args)

                            np.random.seed(int(ak.flatten(seed, axis=None)[0]))

                            template_len: int = ak.num(ak.flatten(template, axis=None), axis=0)
                            flat_rand: np.random = np.random.randint(0, 2,  template_len)
                            result: ak.Array = unflatten_array_like(
                                ak.from_numpy(flat_rand.astype(dtype=bool)), template
                            )
                            result: ak.Array = ak.Array(result)

                        else:
                            lower_limit: ak.Array = self.input_data(1, args)
                            upper_limit: ak.Array = self.input_data(2, args)
                            seed: ak.Array = self.input_data(3, args)

                            np.random.seed(int(ak.flatten(seed, axis=None)[0]))

                            broadcasted_params: ak.Array = ak.zip({"template": 0, "min": lower_limit,
                                                                   "max": upper_limit}, right_broadcast=True)
                            flat_params: ak.Array = flatten_record(nested_record=broadcasted_params, as_tuple=True)

                            template_len: int = ak.num(ak.flatten(template.x, axis=None), axis=0)
                            result_list: list[ak.Array] = []
                            for param_tuple in flat_params:
                                flat_rand: np.ndarray = np.random.randint(
                                    param_tuple["1"], param_tuple["2"] + 1, [template_len, 3]
                                )
                                flat_rand: ak.Array = ak.zip(
                                    {"x": flat_rand[:, 0], "y": flat_rand[:, 1], "z": flat_rand[:, 2]}
                                )
                                result_list.append(unflatten_record_like(flat_rand, template))

                            result: ak.Array = ak.concatenate(result_list, axis=0)

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            y: float = time.time()
                            print("Random Functions executed in", "{number:.{digits}f}".format(number=1000 * (y - x),
                                                                                               digits=2), "ms")

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

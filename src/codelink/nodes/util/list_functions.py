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
from typing import TYPE_CHECKING, Optional, Union, cast
import importlib
import warnings
import inspect
import time

import Part
import awkward as ak

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import numpy as np

from nested_data import NestedData
from utils import (global_index, unflatten_array_like, simplify_array, simplified_array_structure,
                   unflatten_record_like, flatten_record, simplify_record, simplified_rec_struct)
from node_item import NodeItem
from input_widgets import OptionBoxWidget
from sockets.any_none import AnyNone
from sockets.value_line import ValueLine

if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = True


class ListFunctions(NodeItem):
    REG_NAME: str = "List Functions"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget(undo_stack)
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Zip", "Shift"])
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
            AnyNone(undo_stack=self._undo_stack, name="List In", content_value="<No Input>", is_input=True,
                    parent_node=self),
            AnyNone(undo_stack=self._undo_stack, name="List Out", content_value="<No Input>", is_input=False,
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
        input_widget_count: int = len(self.input_socket_widgets)

        self._undo_stack.beginMacro("Changes option box")
        self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self))

        if current_option_name == "Zip":
            while input_widget_count > 1:
                remove_idx: int = len(self.input_socket_widgets) - 1
                remove_socket: SocketWidget = self._socket_widgets[remove_idx]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))

                self._undo_stack.push(remove_socket_cmd_cls(self, remove_idx))
                input_widget_count -= 1

        else:
            while input_widget_count < 2:
                new_socket_widget: ValueLine = ValueLine(
                    undo_stack=self._undo_stack, name="Offset", content_value=1.0, is_input=True, parent_node=self
                )
                insert_idx: int = len(self.input_socket_widgets)
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, insert_idx))
                input_widget_count += 1

        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )
        self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self, on_redo=True))
        self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> Union[ak.Array, NestedData, list]:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        list_in: Union[ak.Array, NestedData] = self.input_data(0, args)

                        if DEBUG:
                            a: float = time.time()

                        if self._option_box.currentText() == "Zip":
                            if isinstance(list_in, ak.Array):
                                if (len(list_in.fields) == 0 and type(simplified_array_structure(list_in)) == int or
                                        len(list_in.fields) != 0 and type(simplified_rec_struct(list_in)) == int):
                                    result: ak.Array = list_in
                                else:
                                    zipped_tuples: ak.Array = ak.zip(ak.to_list(list_in), right_broadcast=True)
                                    grafted_fields: list[ak.Array] = [
                                        ak.unflatten(zipped_tuples[field], counts=1, axis=-1)
                                        for field in zipped_tuples.fields
                                    ]
                                    result: ak.Array = ak.concatenate(grafted_fields, axis=-1)

                            elif isinstance(list_in, NestedData):
                                if type(simplified_array_structure(list_in.structure)) == int:
                                    result: NestedData = list_in
                                else:
                                    zipped_tuples: ak.Array = ak.zip(ak.to_list(list_in.structure),
                                                                     right_broadcast=True)
                                    grafted_fields: list[ak.Array] = [
                                        ak.unflatten(zipped_tuples[field], counts=1, axis=-1)
                                        for field in zipped_tuples.fields
                                    ]
                                    new_structure: ak.Array = ak.concatenate(grafted_fields, axis=-1)
                                    simple_structure: list = ak.to_list(simplify_array(new_structure))

                                    flat_data_in: np.ndarray = np.array(list_in.data, dtype="object")
                                    flat_data_out: [Part.Shape] = []
                                    for simple_ids in simple_structure:
                                        flat_data_out.extend(flat_data_in[simple_ids])

                                    result: NestedData = NestedData(
                                        flat_data_out, ak.transform(global_index, new_structure)
                                    )
                            else:
                                result: ak.Array = ak.Array([0])

                        else:
                            offset: ak.Array = self.input_data(1, args)

                            if isinstance(list_in, ak.Array):
                                if len(list_in.fields) == 0:
                                    flat_data: list = []
                                    target_structure: Optional[ak.Array] = None
                                    flat_offsets: ak.Array = ak.flatten(offset, axis=None)
                                    for flat_offset in flat_offsets:
                                        if target_structure is None:
                                            target_structure: ak.Array = list_in
                                        else:
                                            target_structure: ak.Array = ak.concatenate([target_structure, list_in])

                                        simple_list, struct_simple_list = (ak.to_list(simplify_array(list_in)),
                                                                           simplified_array_structure(list_in))
                                        if type(struct_simple_list) is int:
                                            flat_data.append(np.roll(simple_list, int(flat_offset)))
                                        else:
                                            for sub_list in simple_list:
                                                flat_data.append(np.roll(sub_list, int(flat_offset)))

                                    flat_result: ak.Array = ak.flatten(flat_data, axis=None)
                                    result: ak.Array = unflatten_array_like(flat_result, target_structure)

                                    offset_dept: int = offset.layout.minmax_depth[1]
                                    while offset_dept > 1:
                                        result: ak.Array = ak.unflatten(result, counts=ak.num(result, axis=0), axis=0)
                                        offset_dept -= 1
                                else:
                                    flat_data: list = []
                                    target_structure: Optional[ak.Array] = None
                                    flat_offsets: ak.Array = ak.flatten(offset, axis=None)
                                    for flat_offset in flat_offsets:
                                        if target_structure is None:
                                            target_structure: ak.Array = list_in
                                        else:
                                            target_structure: ak.Array = ak.concatenate([target_structure, list_in])

                                        simple_list, struct_simple_list = (simplify_record(list_in),
                                                                           simplified_rec_struct(list_in))

                                        if type(struct_simple_list) is int:
                                            flat_data.append(
                                                {"x": np.roll(ak.to_list(simple_list.x), int(flat_offset)),
                                                 "y": np.roll(ak.to_list(simple_list.y), int(flat_offset)),
                                                 "z": np.roll(ak.to_list(simple_list.z), int(flat_offset))}
                                            )
                                        else:
                                            for sub_list in simple_list:
                                                flat_data.append(
                                                    {"x": np.roll(ak.to_list(sub_list.x), int(flat_offset)),
                                                     "y": np.roll(ak.to_list(sub_list.y), int(flat_offset)),
                                                     "z": np.roll(ak.to_list(sub_list.z), int(flat_offset))}
                                                )

                                    flat_result: ak.Array = flatten_record(ak.Array(flat_data))
                                    result: ak.Array = unflatten_record_like(flat_result, target_structure)

                                    offset_dept: int = offset.layout.minmax_depth[1]
                                    while offset_dept > 1:
                                        result: ak.Array = ak.unflatten(result, counts=ak.num(result, axis=0), axis=0)
                                        offset_dept -= 1

                            elif isinstance(list_in, NestedData):
                                flat_data: list = []
                                target_structure: Optional[ak.Array] = None
                                flat_offsets: ak.Array = ak.flatten(offset, axis=None)
                                for flat_offset in flat_offsets:
                                    if target_structure is None:
                                        target_structure: ak.Array = list_in.structure
                                    else:
                                        target_structure: ak.Array = ak.concatenate([target_structure,
                                                                                     list_in.structure])

                                    simple_list, struct_simple_list = (ak.to_list(simplify_array(list_in.structure)),
                                                                       simplified_array_structure(list_in.structure))
                                    if type(struct_simple_list) is int:
                                        flat_data.append(np.roll(simple_list, int(flat_offset)))
                                    else:
                                        for sub_list in simple_list:
                                            flat_data.append(np.roll(sub_list, int(flat_offset)))

                                flat_structure: ak.Array = ak.flatten(flat_data, axis=None)
                                new_structure: ak.Array = unflatten_array_like(flat_structure, target_structure)

                                offset_dept: int = offset.layout.minmax_depth[1]
                                while offset_dept > 1:
                                    new_structure: ak.Array = ak.unflatten(
                                        new_structure, counts=ak.num(new_structure, axis=0), axis=0
                                    )
                                    offset_dept -= 1

                                simple_structure: list = ak.to_list(simplify_array(new_structure))

                                flat_data_in: np.ndarray = np.array(list_in.data, dtype="object")
                                flat_data_out: [Part.Shape] = []
                                for simple_ids in simple_structure:
                                    if type(simple_ids) == int:
                                        flat_data_out.append(flat_data_in[simple_ids])
                                    else:
                                        flat_data_out.extend(flat_data_in[simple_ids])

                                result: NestedData = NestedData(
                                    flat_data_out, ak.transform(global_index, new_structure)
                                )

                            else:
                                result: ak.Array = ak.Array([0])

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            b: float = time.time()
                            print("List Functions executed in", "{number:.{digits}f}".format(number=1000 * (b - a),
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

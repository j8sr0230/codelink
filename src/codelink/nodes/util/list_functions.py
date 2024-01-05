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
                   unflatten_record_like, flatten_record, simplify_record, simplified_rec_struct, mass_zip_to_array,
                   reorder_list)
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
        self._option_box.addItems(["Zip", "Mass Zip", "Flip", "Shift"])
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
            AnyNone(undo_stack=self._undo_stack, name="List A", content_value="<No Input>", is_input=True,
                    parent_node=self),
            AnyNone(undo_stack=self._undo_stack, name="List B", content_value="<No Input>", is_input=True,
                    parent_node=self),
            AnyNone(undo_stack=self._undo_stack, name="Out", content_value="<No Input>", is_input=False,
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

        if current_option_name in ("Mass Zip", "Flip"):
            while input_widget_count > 1:
                remove_idx: int = len(self.input_socket_widgets) - 1
                remove_socket: SocketWidget = self._socket_widgets[remove_idx]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))

                self._undo_stack.push(remove_socket_cmd_cls(self, remove_idx))
                input_widget_count -= 1
        else:
            while input_widget_count < 2:
                if current_option_name == "Shift":
                    new_socket_widget: ValueLine = ValueLine(
                        undo_stack=self._undo_stack, name="Offset", content_value=1.0, is_input=True, parent_node=self
                    )
                else:
                    new_socket_widget: AnyNone = AnyNone(
                        undo_stack=self._undo_stack, name="List B", content_value="<No Input>", is_input=True,
                        parent_node=self
                    )
                insert_idx: int = len(self.input_socket_widgets)
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, insert_idx))
                input_widget_count += 1

            if current_option_name == "Shift" and input_widget_count == 2 and type(self._socket_widgets[2]) == AnyNone:
                while input_widget_count > 1:
                    remove_idx: int = len(self.input_socket_widgets) - 1
                    remove_socket: SocketWidget = self._socket_widgets[remove_idx]
                    for edge in remove_socket.pin.edges:
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))

                    self._undo_stack.push(remove_socket_cmd_cls(self, remove_idx))
                    input_widget_count -= 1

                new_socket_widget: ValueLine = ValueLine(
                    undo_stack=self._undo_stack, name="Offset", content_value=1.0, is_input=True, parent_node=self
                )
                insert_idx: int = len(self.input_socket_widgets)
                self._undo_stack.push(add_socket_cmd_cls(self, new_socket_widget, insert_idx))
                input_widget_count += 1

            if current_option_name == "Zip" and input_widget_count == 2 and type(self._socket_widgets[2]) == ValueLine:
                while input_widget_count > 1:
                    remove_idx: int = len(self.input_socket_widgets) - 1
                    remove_socket: SocketWidget = self._socket_widgets[remove_idx]
                    for edge in remove_socket.pin.edges:
                        self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge, True))

                    self._undo_stack.push(remove_socket_cmd_cls(self, remove_idx))
                    input_widget_count -= 1

                new_socket_widget: AnyNone = AnyNone(
                    undo_stack=self._undo_stack, name="List B", content_value="<No Input>", is_input=True,
                    parent_node=self
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
                        list_a: Union[ak.Array, NestedData] = self.input_data(0, args)

                        if DEBUG:
                            a: float = time.time()

                        if self._option_box.currentText() == "Zip":
                            list_b: Union[ak.Array, NestedData] = self.input_data(1, args)

                            if isinstance(list_a, ak.Array) and isinstance(list_b, ak.Array):
                                zipped_tuples: ak.Array = ak.zip([list_a, list_b], right_broadcast=True)
                                grafted_tuples: ak.Array = ak.unflatten(zipped_tuples, counts=1, axis=-1)
                                result = ak.concatenate(ak.unzip(grafted_tuples), axis=-1)

                            elif isinstance(list_a, NestedData) and isinstance(list_b, NestedData):
                                zipped_tuples: ak.Array = ak.zip([list_a.structure, list_b.structure],
                                                                 right_broadcast=True)
                                grafted_tuples: ak.Array = ak.unflatten(zipped_tuples, counts=1, axis=-1)
                                new_structure: ak.Array = ak.concatenate(ak.unzip(grafted_tuples), axis=-1)

                                flat_data: list[Part.Shape] = []
                                simple_structure: list = ak.to_list(simplify_array(new_structure))

                                for simple_ids in simple_structure:
                                    flat_data.append(list_a.data[simple_ids[0]])
                                    flat_data.append(list_b.data[simple_ids[1]])

                                result: NestedData = NestedData(
                                    flat_data, ak.transform(global_index, new_structure)
                                )
                            else:
                                result: ak.Array = ak.Array([0])

                        elif self._option_box.currentText() == "Mass Zip":
                            if isinstance(list_a, ak.Array):
                                if (len(list_a.fields) == 0 and type(simplified_array_structure(list_a)) == int or
                                        len(list_a.fields) != 0 and type(simplified_rec_struct(list_a)) == int):
                                    result: ak.Array = list_a
                                else:
                                    result: ak.Array = mass_zip_to_array(list_a)

                            elif isinstance(list_a, NestedData):
                                if type(simplified_array_structure(list_a.structure)) == int:
                                    result: NestedData = list_a
                                else:
                                    new_structure: ak.Array = mass_zip_to_array(list_a.structure)
                                    flat_data_out: list[Part.Shape] = reorder_list(list_a.data, new_structure)

                                    result: NestedData = NestedData(
                                        flat_data_out, ak.transform(global_index, new_structure)
                                    )
                            else:
                                result: ak.Array = ak.Array([0])

                        elif self._option_box.currentText() == "Flip":
                            flat_data: list = []

                            if isinstance(list_a, ak.Array):
                                if len(list_a.fields) == 0:
                                    simple_list, struct_simple_list = (ak.to_list(simplify_array(list_a)),
                                                                       simplified_array_structure(list_a))
                                    if type(struct_simple_list) is int:
                                        flat_data.append(np.flip(simple_list))
                                    else:
                                        for sub_list in simple_list:
                                            flat_data.append(np.flip(sub_list))

                                    flat_result: ak.Array = ak.flatten(flat_data, axis=None)
                                    result: ak.Array = unflatten_array_like(flat_result, list_a)

                                else:
                                    simple_list, struct_simple_list = (simplify_record(list_a),
                                                                       simplified_rec_struct(list_a))
                                    if type(struct_simple_list) is int:
                                        flat_data.append(
                                            {"x": np.flip(ak.to_list(simple_list.x)),
                                             "y": np.flip(ak.to_list(simple_list.y)),
                                             "z": np.flip(ak.to_list(simple_list.z))}
                                        )
                                    else:
                                        for sub_list in simple_list:
                                            flat_data.append(
                                                {"x": np.flip(ak.to_list(sub_list.x)),
                                                 "y": np.flip(ak.to_list(sub_list.y)),
                                                 "z": np.flip(ak.to_list(sub_list.z))}
                                            )

                                    flat_result: ak.Array = flatten_record(ak.Array(flat_data))
                                    result: ak.Array = unflatten_record_like(flat_result, list_a)

                            elif isinstance(list_a, NestedData):
                                simple_list, struct_simple_list = (ak.to_list(simplify_array(list_a.structure)),
                                                                   simplified_array_structure(list_a.structure))
                                if type(struct_simple_list) is int:
                                    flat_data.append(np.flip(simple_list))
                                else:
                                    for sub_list in simple_list:
                                        flat_data.append(np.flip(sub_list))

                                flat_structure: ak.Array = ak.flatten(flat_data, axis=None)
                                new_structure: ak.Array = unflatten_array_like(flat_structure, list_a.structure)
                                flat_data_out: list[Part.Shape] = reorder_list(list_a.data, new_structure)

                                result: NestedData = NestedData(
                                    flat_data_out, ak.transform(global_index, new_structure)
                                )
                            else:
                                result: ak.Array = ak.Array([0])

                        else:
                            offset: ak.Array = self.input_data(1, args)

                            flat_data: list = []
                            target_structure: Optional[ak.Array] = None
                            flat_offsets: ak.Array = ak.flatten(offset, axis=None)

                            if isinstance(list_a, ak.Array):
                                if len(list_a.fields) == 0:
                                    for flat_offset in flat_offsets:
                                        if target_structure is None:
                                            target_structure: ak.Array = list_a
                                        else:
                                            target_structure: ak.Array = ak.concatenate([target_structure, list_a])

                                        simple_list, struct_simple_list = (ak.to_list(simplify_array(list_a)),
                                                                           simplified_array_structure(list_a))
                                        if type(struct_simple_list) is int:
                                            flat_data.append(np.roll(simple_list, int(flat_offset)))
                                        else:
                                            for sub_list in simple_list:
                                                flat_data.append(np.roll(sub_list, int(flat_offset)))

                                    flat_result: ak.Array = ak.flatten(flat_data, axis=None)
                                    result: ak.Array = unflatten_array_like(flat_result, target_structure)

                                else:
                                    for flat_offset in flat_offsets:
                                        if target_structure is None:
                                            target_structure: ak.Array = list_a
                                        else:
                                            target_structure: ak.Array = ak.concatenate([target_structure, list_a])

                                        simple_list, struct_simple_list = (simplify_record(list_a),
                                                                           simplified_rec_struct(list_a))
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

                            elif isinstance(list_a, NestedData):
                                for flat_offset in flat_offsets:
                                    if target_structure is None:
                                        target_structure: ak.Array = list_a.structure
                                    else:
                                        target_structure: ak.Array = ak.concatenate([target_structure,
                                                                                     list_a.structure])

                                    simple_list, struct_simple_list = (ak.to_list(simplify_array(list_a.structure)),
                                                                       simplified_array_structure(list_a.structure))
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

                                flat_data_out: list[Part.Shape] = reorder_list(list_a.data, new_structure)

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

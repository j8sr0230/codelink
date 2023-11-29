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
import warnings
import inspect

import awkward as ak

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from input_widgets import NumberInputWidget
from node_item import NodeItem
from sockets.value_line import ValueLine
from sockets.value_slider import ValueSlider

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class Slider(NodeItem):
    REG_NAME: str = "Slider"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name=REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Option combo box
        option_container: QtWidgets.QWidget = QtWidgets.QWidget()
        container_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        container_layout.setSpacing(0)
        container_layout.setMargin(0)
        option_container.setLayout(container_layout)

        self._slider_min: NumberInputWidget = NumberInputWidget(option_container)
        self._slider_min.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self._slider_min.setText("-100")
        self._slider_value: QtWidgets.QLabel = QtWidgets.QLabel(option_container)
        self._slider_value.setText("0")
        self._slider_max: NumberInputWidget = NumberInputWidget(option_container)
        self._slider_max.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self._slider_max.setText("100")

        container_layout.addWidget(self._slider_min)
        container_layout.addWidget(self._slider_value)
        container_layout.addWidget(self._slider_max)

        self._content_widget.hide()
        self._content_layout.addWidget(option_container)
        self._content_widget.show()

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ValueSlider(undo_stack=self._undo_stack, name="Value", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Value", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]

        # Listeners
        cast(QtCore.SignalInstance, self._slider_min.textChanged).connect(
            lambda txt: self.input_socket_widgets[0].input_widget.setMinimum(self._slider_min.input_data())
        )
        cast(QtCore.SignalInstance, self._slider_max.textChanged).connect(
            lambda txt: self.input_socket_widgets[0].input_widget.setMaximum(self._slider_max.input_data())
        )

        cast(QtCore.SignalInstance, self.input_socket_widgets[0].input_widget.valueChanged).connect(
            lambda txt: self._slider_value.setText(str(txt))
        )

    # def update_slider(self) -> None:
    #     # Hack to prevent cyclic imports
    #     set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")
    #     emit_dag_changed_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "EmitDagChangedCommand")
    #
    #     last_option_index: int = self._option_box.last_index
    #     current_option_index: int = self._option_box.currentIndex()
    #
    #     self._undo_stack.beginMacro("Changes option box")
    #     self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self))
    #     self._undo_stack.push(
    #         set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
    #     )
    #     self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self, on_redo=True))
    #     self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> list:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        result: ak.Array = self.input_data(0, args)

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)
                        print("Slider executed")

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
        data_dict["Slider Min"] = self._slider_min.text()
        data_dict["Slider Max"] = self._slider_max.text()
        data_dict["Slider Value"] = self._slider_value.text()
        return data_dict

    def __setstate__(self, state: dict):
        super().__setstate__(state)
        self.input_socket_widgets[0].input_widget.blockSignals(True)
        self._slider_min.setText(state["Slider Min"])
        self._slider_max.setText(state["Slider Max"])
        self._slider_value.setText(state["Slider Value"])

        self.input_socket_widgets[0].input_widget.setMinimum(int(state["Slider Min"]))
        self.input_socket_widgets[0].input_widget.setMaximum(int(state["Slider Max"]))
        self.input_socket_widgets[0].input_widget.setValue(int(state["Slider Value"]))
        self.input_socket_widgets[0].input_widget.blockSignals(False)

        cast(QtCore.SignalInstance, self.input_socket_widgets[0].input_widget.valueChanged).connect(
            lambda txt: self._slider_value.setText(str(txt))
        )

        self.update()

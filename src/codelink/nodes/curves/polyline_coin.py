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
import importlib

# noinspection PyUnresolvedReferences
import FreeCAD
# noinspection PyPackageRequirements
from pivy import coin

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from utils import map_last_level, map_objects, broadcast_data_tree, ListWrapper
from node_item import NodeItem
from input_widgets import OptionBoxWidget
from sockets.vector_none import VectorNone
from sockets.coin_none import CoinNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


class PolylineCoin(NodeItem):
    REG_NAME: str = "Polyline Coin"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget()
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Open", "Cyclic"])
        item_list_view: QtWidgets.QListView = cast(QtWidgets.QListView, self._option_box.view())
        item_list_view.setSpacing(2)
        self._content_widget.hide()
        self._content_layout.addWidget(self._option_box)
        self._content_widget.show()

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            VectorNone(undo_stack=self._undo_stack, name="Vector", content_value="<No Input>", is_input=True,
                       parent_node=self),
            CoinNone(undo_stack=self._undo_stack, name="Polyline Coin", content_value="<No Input>", is_input=False,
                     parent_node=self)
        ]

        self._polyline_sep: Optional[coin.SoSeparator] = None

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    def update_socket_widgets(self) -> None:
        # Hack to prevent cyclic imports
        set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")
        emit_dag_changed_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "EmitDagChangedCommand")

        last_option_index: int = self._option_box.last_index
        current_option_index: int = self._option_box.currentIndex()

        self._undo_stack.beginMacro("Changes option box")
        self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self))
        self._undo_stack.push(
            set_op_idx_cmd_cls(self, self._option_box, last_option_index, current_option_index)
        )
        self._undo_stack.push(emit_dag_changed_cmd_cls(self.scene(), self, on_redo=True))
        self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    @staticmethod
    def make_polyline_sep(parameter_zip: tuple) -> coin.SoSeparator:
        positions: list[FreeCAD.Vector] = parameter_zip[0].wrapped_data
        is_cyclic: bool = parameter_zip[1]

        if type(positions) == list and len(positions) > 1:
            if is_cyclic:
                positions.append(positions[0])

            polyline_sep: coin.SoSeparator = coin.SoSeparator()

            color: coin.SoBaseColor = coin.SoBaseColor()
            color.rgb = (0, 0, 0)
            polyline_sep.addChild(color)

            draw_style: coin.SoDrawStyle = coin.SoDrawStyle()
            draw_style.lineWidth = 1
            polyline_sep.addChild(draw_style)

            control_pts: coin.SoCoordinate3 = coin.SoCoordinate3()
            # noinspection PyTypeChecker
            pts: tuple = tuple([tuple(pos) for pos in positions])
            control_pts.point.setValues(0, len(pts), pts)
            polyline_sep.addChild(control_pts)

            polyline: coin.SoLineSet = coin.SoLineSet()
            polyline.numVertices = len(pts)
            polyline_sep.addChild(polyline)

            return polyline_sep

        else:
            return coin.SoSeparator()

    def eval_0(self, *args) -> list:
        result: list = [coin.SoSeparator()]

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    cyclic: list = [False]
                    if self._option_box.currentText() == "Cyclic":
                        cyclic: list = [True]

                    positions: list = self.input_data(0, args)
                    wrapped_positions: list = list(map_last_level([positions], FreeCAD.Vector, ListWrapper))

                    data_tree: list = list(broadcast_data_tree(wrapped_positions, cyclic))
                    result: list = list(map_objects(data_tree, tuple, self.make_polyline_sep))

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

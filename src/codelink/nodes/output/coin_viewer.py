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
import time

import FreeCADGui as Gui
# noinspection PyPackageRequirements
from pivy import coin

import PySide2.QtWidgets as QtWidgets

from nested_data import NestedData
from node_item import NodeItem
from sockets.coin_none import CoinNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget

DEBUG = True


class CoinViewer(NodeItem):
    REG_NAME: str = "Coin Viewer"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            CoinNone(undo_stack=self._undo_stack, name="Coin", content_value="<No Input>", is_input=True,
                     parent_node=self),
            CoinNone(undo_stack=self._undo_stack, name="Coin", content_value="<No Input>", is_input=False,
                     parent_node=self)
        ]

        self._coin_sep: Optional[coin.SoSeparator] = None

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> NestedData:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        nested_data: NestedData = self.input_data(0, args)

                        if DEBUG:
                            a: float = time.time()

                        if hasattr(Gui, "ActiveDocument"):
                            flat_coin_seps: list[coin.SoSeparator] = nested_data.data
                            sg = Gui.ActiveDocument.ActiveView.getSceneGraph()

                            if self._coin_sep is not None:
                                sg.removeChild(self._coin_sep)
                                # self._coin_sep: Optional[coin.SoSeparator] = None

                            self._coin_sep: coin.SoSeparator = coin.SoSeparator()
                            for child in flat_coin_seps:
                                self._coin_sep.addChild(child)

                            sg.addChild(self._coin_sep)
                        else:
                            self.on_remove()

                        result: NestedData = nested_data

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            b: float = time.time()
                            print("Coin Viewer executed in", "{number:.{digits}f}".format(number=1000 * (b - a),
                                                                                          digits=2), "ms")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

    def on_remove(self):
        if hasattr(Gui, "ActiveDocument") and self._coin_sep is not None:
            sg = Gui.ActiveDocument.ActiveView.getSceneGraph()
            sg.removeChild(self._coin_sep)
        self._coin_sep: Optional[coin.SoSeparator] = None

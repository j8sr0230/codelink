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

import awkward as ak
import numpy as np
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
# import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D  # noqa

import PySide2.QtWidgets as QtWidgets

from utils import record_structure, flatten_record, unflatten_array_like
from node_item import NodeItem
from sockets.vector_none import VectorNone
from sockets.value_line import ValueLine


if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = True


class KukaKr6(NodeItem):
    REG_NAME: str = "KUKA KR 6"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            VectorNone(undo_stack=self._undo_stack, name="Vector", content_value="<No Input>", is_input=True,
                       parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Rotation", content_value="<No Input>", is_input=False,
                      parent_node=self)
        ]

        self._kuka_kr_6_chain: Chain = Chain(name="kuka_kr_6", links=[
            OriginLink(),
            URDFLink(
                name="A1",
                origin_translation=np.array([0, 0, 0]),
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([0, 0, 1]),
            ),
            URDFLink(
                name="A2",
                origin_translation=np.array([260, 0, 675]),
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([0, 1, 0]),
            ),
            URDFLink(
                name="A3",
                origin_translation=np.array([0, 0, 680]),
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([0, 1, 0]),
            ),
            URDFLink(
                name="A4",
                origin_translation=np.array([670, 0, -35]),
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([1, 0, 0]),
            ),
            URDFLink(
                name="A5",
                origin_translation=np.array([0, 0, 0]),
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([0, 1, 0]),
            ),
            URDFLink(
                name="A6",
                origin_translation=np.array([115, 0, 0]),
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([1, 0, 0]),
            )
        ], active_links_mask=[False, True, True, True, True, True, True])

        # # Validating kinematic chain
        # a1: np.ndarray = np.radians(0)
        # a2: np.ndarray = np.radians(0)
        # a3: np.ndarray = np.radians(0)
        # a4: np.ndarray = np.radians(0)
        # a5: np.ndarray = np.radians(90)
        # a6: np.ndarray = np.radians(0)
        #
        # # Plotting forward and inverse result
        # ax = matplotlib.pyplot.figure().add_subplot(111, projection="3d")
        # self._kuka_kr_6_chain.plot([0, a1, a2, a3, a4, a5, a6], ax)
        # matplotlib.pyplot.show()

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> ak.Array:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        position:  ak.Array = self.input_data(0, args)

                        if DEBUG:
                            a: float = time.time()

                        flat_pos, struct_pos = (ak.to_list(flatten_record(position, True)), record_structure(position))

                        result: list[np.ndarray] = []
                        for param_tuple in flat_pos:
                            result.append(
                                np.round(
                                    np.degrees(self._kuka_kr_6_chain.inverse_kinematics(ak.to_numpy(param_tuple))[1:]),
                                    2
                                )
                            )

                        result: ak.Array = unflatten_array_like(result, struct_pos)

                        self._is_dirty: bool = False
                        self._is_invalid: bool = False
                        self._cache[cache_idx] = self.output_data(0, result)

                        if DEBUG:
                            b: float = time.time()
                            print("KUKA executed in", "{number:.{digits}f}".format(number=1000 * (b - a), digits=2),
                                  "ms")

                    except Exception as e:
                        self._is_dirty: bool = True
                        print(e)
                except Warning as e:
                    self._is_dirty: bool = True
                    print(e)

        return self._cache[cache_idx]

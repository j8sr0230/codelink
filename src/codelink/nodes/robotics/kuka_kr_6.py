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
from pathlib import Path
import warnings
import inspect
import time
import os

import awkward as ak
import numpy as np
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
# import matplotlib.pyplot
# from mpl_toolkits.mplot3d import Axes3D  # noqa

# import FreeCADGui as Gui
# noinspection PyPackageRequirements
from pivy import coin

import PySide2.QtWidgets as QtWidgets

from utils import populate_coin_scene, flatten_record
from nested_data import NestedData
from node_item import NodeItem
from sockets.vector_none import VectorNone
from sockets.value_line import ValueLine
from sockets.coin_none import CoinNone


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
            VectorNone(undo_stack=self._undo_stack, name="Origin", content_value="<No Input>", is_input=True,
                       parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Rotation", content_value=0., is_input=True, parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Target", content_value="<No Input>", is_input=True,
                       parent_node=self),
            CoinNone(undo_stack=self._undo_stack, name="KUKA KR 6", content_value="<No Input>", is_input=False,
                     parent_node=self)
        ]

        # Kinematic chain
        self._kuka_kr_6_chain: Chain = Chain(name="kuka_kr_6", links=[
            OriginLink(),
            URDFLink(name="A1", origin_translation=np.array([0, 0, 0]), origin_orientation=np.array([0, 0, 0]),
                     rotation=np.array([0, 0, 1])),
            URDFLink(name="A2", origin_translation=np.array([260, 0, 675]), origin_orientation=np.array([0, 0, 0]),
                     rotation=np.array([0, 1, 0])),
            URDFLink(name="A3", origin_translation=np.array([0, 0, 680]),  origin_orientation=np.array([0, 0, 0]),
                     rotation=np.array([0, 1, 0])),
            URDFLink(name="A4", origin_translation=np.array([670, 0, -35]), origin_orientation=np.array([0, 0, 0]),
                     rotation=np.array([1, 0, 0])),
            URDFLink(name="A5", origin_translation=np.array([0, 0, 0]), origin_orientation=np.array([0, 0, 0]),
                     rotation=np.array([0, 1, 0])),
            URDFLink(name="A6", origin_translation=np.array([115, 0, 0]), origin_orientation=np.array([0, 0, 0]),
                     rotation=np.array([1, 0, 0]))
        ], active_links_mask=[False, True, True, True, True, True, True])

        # SoVRMLGroup per axis
        so_vrml_groups: list[coin.SoVRMLGroup] = []
        vrml_paths: list[str] = [f for f in os.listdir(os.path.join(str(Path(__file__).parent), "vrml"))]
        vrml_paths.insert(0, vrml_paths.pop())
        so_input: coin.SoInput = coin.SoInput()
        for vrml_path in vrml_paths:
            so_input.openFile(os.path.join(str(Path(__file__).parent), "vrml", vrml_path))
            so_vrml_group: coin.SoVRMLGroup = coin.SoDB.readAllVRML(so_input)
            so_vrml_group.ref()
            so_vrml_groups.append(so_vrml_group)

        # SoSeparator with forward kinematic
        self._coin_sep: coin.SoSeparator = coin.SoSeparator()

        self._rotation: coin.SoRotationXYZ = coin.SoRotationXYZ()
        self._rotation.axis = coin.SoRotationXYZ.Z
        self._coin_sep.addChild(self._rotation)

        self._trans = coin.SoTranslation()
        self._coin_sep.addChild(self._trans)

        self._coin_sep.addChild(so_vrml_groups[0])
        self._a1_rot: coin.SoRotationXYZ = populate_coin_scene(so_vrml_groups[1], np.array([0, 0, 0]),
                                                               coin.SoRotationXYZ.Z, so_vrml_groups[0])
        self._a2_rot: coin.SoRotationXYZ = populate_coin_scene(so_vrml_groups[2], np.array([260, 0, 675]),
                                                               coin.SoRotationXYZ.Y, so_vrml_groups[1])
        self._a3_rot: coin.SoRotationXYZ = populate_coin_scene(so_vrml_groups[3], np.array([260, 0, 1355]),
                                                               coin.SoRotationXYZ.Y, so_vrml_groups[2])
        self._a4_rot: coin.SoRotationXYZ = populate_coin_scene(so_vrml_groups[4], np.array([260, 0, 1320]),
                                                               coin.SoRotationXYZ.X, so_vrml_groups[3])
        self._a5_rot: coin.SoRotationXYZ = populate_coin_scene(so_vrml_groups[5], np.array([930, 0, 1320]),
                                                               coin.SoRotationXYZ.Y, so_vrml_groups[4])
        self._a6_rot: coin.SoRotationXYZ = populate_coin_scene(so_vrml_groups[6], np.array([1045, 0, 1320]),
                                                               coin.SoRotationXYZ.X, so_vrml_groups[5])

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> ak.Array:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        origin:  ak.Array = self.input_data(0, args)
                        rotation: ak.Array = self.input_data(1, args)
                        target:  ak.Array = self.input_data(2, args)

                        if DEBUG:
                            a: float = time.time()

                        flat_targ: ak.Array = flatten_record(target, True)[0]
                        flat_targ: list[float, float, float] = (ak.to_list(flat_targ)
                                                                if not all(flat_targ[f] == 0 for f in flat_targ.fields)
                                                                else [930, 0, 1205])

                        axis_radians: list = self._kuka_kr_6_chain.inverse_kinematics(
                            target_position=ak.to_numpy(flat_targ),
                            target_orientation=np.degrees([1, 0, 0]),
                            orientation_mode="Z"
                        )[1:]

                        self._rotation.angle = np.radians(ak.flatten(rotation, axis=None)[0])
                        self._trans.translation.setValue(ak.to_list(flatten_record(origin, True)[0]))

                        self._a1_rot.angle = axis_radians[0]
                        self._a2_rot.angle = axis_radians[1]
                        self._a3_rot.angle = axis_radians[2]
                        self._a4_rot.angle = axis_radians[3]
                        self._a5_rot.angle = axis_radians[4]
                        self._a6_rot.angle = axis_radians[5]

                        result: NestedData = NestedData(
                            data=[self._coin_sep],
                            structure=ak.Array([0])
                        )

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

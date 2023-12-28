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
from mpl_toolkits.mplot3d import Axes3D  # noqa

import FreeCADGui as Gui
# noinspection PyPackageRequirements
from pivy import coin

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
            ValueLine(undo_stack=self._undo_stack, name="A1", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="A2", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="A3", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="A4", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="A5", content_value=0., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="A6", content_value=0., is_input=True, parent_node=self),
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

        kuka_kr6_base_path: str = os.path.join(str(Path(__file__).parent), "vrml", "kuka_kr6_base.wrl")
        kuka_kr6_a1_path: str = os.path.join(str(Path(__file__).parent), "vrml", "kuka_kr6_a1.wrl")
        kuka_kr6_a2_path: str = os.path.join(str(Path(__file__).parent), "vrml", "kuka_kr6_a2.wrl")
        kuka_kr6_a3_path: str = os.path.join(str(Path(__file__).parent), "vrml", "kuka_kr6_a3.wrl")
        kuka_kr6_a4_path: str = os.path.join(str(Path(__file__).parent), "vrml", "kuka_kr6_a4.wrl")
        kuka_kr6_a5_path: str = os.path.join(str(Path(__file__).parent), "vrml", "kuka_kr6_a5.wrl")
        kuka_kr6_a6_path: str = os.path.join(str(Path(__file__).parent), "vrml", "kuka_kr6_a6.wrl")

        inp_base: coin.SoInput = coin.SoInput()
        inp_base.openFile(kuka_kr6_base_path)
        so_base: coin.SoVRMLGroup = coin.SoDB.readAllVRML(inp_base)
        so_base.ref()

        inp_a1: coin.SoInput = coin.SoInput()
        inp_a1.openFile(kuka_kr6_a1_path)
        so_a1: coin.SoVRMLGroup = coin.SoDB.readAllVRML(inp_a1)
        so_a1.ref()

        inp_a2: coin.SoInput = coin.SoInput()
        inp_a2.openFile(kuka_kr6_a2_path)
        so_a2: coin.SoVRMLGroup = coin.SoDB.readAllVRML(inp_a2)
        so_a2.ref()

        inp_a3: coin.SoInput = coin.SoInput()
        inp_a3.openFile(kuka_kr6_a3_path)
        so_a3: coin.SoVRMLGroup = coin.SoDB.readAllVRML(inp_a3)
        so_a3.ref()

        inp_a4: coin.SoInput = coin.SoInput()
        inp_a4.openFile(kuka_kr6_a4_path)
        so_a4: coin.SoVRMLGroup = coin.SoDB.readAllVRML(inp_a4)
        so_a4.ref()

        inp_a5: coin.SoInput = coin.SoInput()
        inp_a5.openFile(kuka_kr6_a5_path)
        so_a5: coin.SoVRMLGroup = coin.SoDB.readAllVRML(inp_a5)
        so_a5.ref()

        inp_a6: coin.SoInput = coin.SoInput()
        inp_a6.openFile(kuka_kr6_a6_path)
        so_a6: coin.SoVRMLGroup = coin.SoDB.readAllVRML(inp_a6)
        so_a6.ref()

        if hasattr(Gui, "ActiveDocument"):
            sg = Gui.ActiveDocument.ActiveView.getSceneGraph()
            coin_sep: coin.SoSeparator = coin.SoSeparator()
            coin_sep.addChild(so_base)

            self._a1_rot: coin.SoRotationXYZ = coin.SoRotationXYZ()
            self._a1_rot.axis = coin.SoRotationXYZ.Z
            so_base.addChild(self._a1_rot)
            so_base.addChild(so_a1)

            a2_reverse_trans: coin.SoTranslation = coin.SoTranslation()
            a2_reverse_trans.translation.setValue([260, 0, 675])
            self._a2_rot: coin.SoRotationXYZ = coin.SoRotationXYZ()
            self._a2_rot.axis = coin.SoRotationXYZ.Y
            a2_forward_trans: coin.SoTranslation = coin.SoTranslation()
            a2_forward_trans.translation.setValue([-260, 0, -675])
            so_a1.addChild(a2_reverse_trans)
            so_a1.addChild(self._a2_rot)
            so_a1.addChild(a2_forward_trans)
            so_a1.addChild(so_a2)

            a3_reverse_trans: coin.SoTranslation = coin.SoTranslation()
            a3_reverse_trans.translation.setValue([260, 0, 1355])
            self._a3_rot: coin.SoRotationXYZ = coin.SoRotationXYZ()
            self._a3_rot.axis = coin.SoRotationXYZ.Y
            a3_forward_trans: coin.SoTranslation = coin.SoTranslation()
            a3_forward_trans.translation.setValue([-260, 0, -1355])
            so_a2.addChild(a3_reverse_trans)
            so_a2.addChild(self._a3_rot)
            so_a2.addChild(a3_forward_trans)
            so_a2.addChild(so_a3)

            so_a3.addChild(so_a4)
            so_a4.addChild(so_a5)
            so_a5.addChild(so_a6)
            sg.addChild(coin_sep)

    # --------------- Node eval methods ---------------

    def eval_0(self, *args) -> ak.Array:
        cache_idx: int = int(inspect.stack()[0][3].split("_")[-1])

        if self._is_invalid or self._cache[cache_idx] is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    try:
                        a1: ak.Array = self.input_data(0, args)
                        a2: ak.Array = self.input_data(1, args)
                        a3: ak.Array = self.input_data(2, args)
                        # a4: ak.Array = self.input_data(3, args)
                        # a5: ak.Array = self.input_data(4, args)
                        # a6: ak.Array = self.input_data(5, args)

                        position:  ak.Array = self.input_data(6, args)

                        if DEBUG:
                            a: float = time.time()

                        if hasattr(Gui, "ActiveDocument"):
                            self._a1_rot.angle = np.radians(ak.flatten(a1, axis=None))[0]
                            self._a2_rot.angle = np.radians(ak.flatten(a2, axis=None))[0]
                            self._a3_rot.angle = np.radians(ak.flatten(a3, axis=None))[0]

                        flat_pos, struct_pos = (ak.to_list(flatten_record(position, True)), record_structure(position))

                        result: list[np.ndarray] = []
                        for param_tuple in flat_pos:
                            result.append(
                                np.round(np.degrees(self._kuka_kr_6_chain.inverse_kinematics(
                                    target_position=ak.to_numpy(param_tuple),
                                    target_orientation=np.degrees([1, 0, 0]),
                                    orientation_mode="Z"
                                )[1:]), 2))

                        result: ak.Array = ak.Array(unflatten_array_like(result, struct_pos))

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

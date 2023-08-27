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

import numpy as np

import FreeCAD
import Part

import PySide2.QtWidgets as QtWidgets

from utils import flatten, map_objects
from node_item import NodeItem
from shape_none import ShapeNone
from value_line import ValueLine
from vector_none import VectorNone

if TYPE_CHECKING:
    from socket_widget import SocketWidget


DEBUG = False
BATCH_SIZE = 100
MAX_ITERATIONS = 1000


class DistributePointsSolid(NodeItem):
    REG_NAME: str = "Distribute Points in Solid"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack, name: str = REG_NAME,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, name, parent)

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            ShapeNone(undo_stack=self._undo_stack, name="Solid", content_value="<No Input>", is_input=True,
                      parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Count", content_value=10., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Distance", content_value=1., is_input=True, parent_node=self),
            ValueLine(undo_stack=self._undo_stack, name="Seed", content_value=0., is_input=True, parent_node=self),
            VectorNone(undo_stack=self._undo_stack, name="Points", content_value="<No Input>", is_input=False,
                       parent_node=self)
        ]
        self._content_widget.hide()
        for widget in self._socket_widgets:
            self._content_layout.addWidget(widget)
        self._content_widget.show()

        self.update_all()

        # Socket-wise node eval methods
        self._evals: list[object] = [self.eval_socket_0]

    # Based on https://github.com/nortikin/sverchok/blob/master/utils/field/probe.py
    @staticmethod
    def check_min_radius(new_position: list, old_positions: list, min_radius: float) -> bool:
        if not old_positions:
            return True

        new_position: np.array = np.array(new_position)
        old_positions: np.array = np.array(old_positions)
        distances: np.array = np.linalg.norm(old_positions - new_position, axis=1)
        ok: bool = (min_radius < distances).all()

        return ok

    def populate_positions(self, solid: Part.Solid, count: int = 10, distance: float = 10.) -> list:
        if isinstance(solid, Part.Solid):
            box = solid.BoundBox
            bbox = ((box.XMin, box.YMin, box.ZMin), (box.XMax, box.YMax, box.ZMax))
            b1, b2 = bbox
            x_min, y_min, z_min = b1
            x_max, y_max, z_max = b2

            done: int = 0
            iterations: int = 0
            generated_positions: list = []

            while done < count:
                iterations += 1

                if DEBUG:
                    print("Iteration no.:", iterations)

                if iterations > MAX_ITERATIONS:
                    raise ValueError("Maximum number of iterations reached.", MAX_ITERATIONS)

                left: int = count - done
                batch_size: int = min(BATCH_SIZE, left)

                batch_x: list = list(np.random.uniform(low=x_min, high=x_max, size=batch_size))
                batch_y: list = list(np.random.uniform(low=y_min, high=y_max, size=batch_size))
                batch_z: list = list(np.random.uniform(low=z_min, high=z_max, size=batch_size))
                batch: list = list(zip(batch_x, batch_y, batch_z))

                candidates: list = [
                    coordinate for coordinate in batch if solid.isInside(FreeCAD.Vector(coordinate), 0.1, True)
                ]

                if len(candidates) > 0:
                    if distance == 0:
                        good_positions: list = candidates
                    else:
                        good_positions: list = []
                        for candidate in candidates:
                            if self.check_min_radius(candidate, generated_positions + good_positions, distance):
                                good_positions.append(candidate)

                    generated_positions.extend(good_positions)
                    done += len(good_positions)

            return [FreeCAD.Vector(coordinates) for coordinates in generated_positions]

        else:
            return [FreeCAD.Vector(0, 0, 0)]

    # --------------- Node eval methods ---------------

    def eval_socket_0(self, *args) -> list:
        result: list = [FreeCAD.Vector(0, 0, 0,)]

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                try:
                    solid: list = self.input_data(0, args)
                    count: int = int(list(flatten(self.input_data(1, args)))[0])
                    distance: float = list(flatten(self.input_data(2, args)))[0]
                    seed: int = int(list(flatten(self.input_data(3, args)))[0])

                    np.random.seed(seed)

                    result: list = list(
                        map_objects(solid, Part.Shape, lambda target: self.populate_positions(target, count, distance))
                    )

                    self._is_dirty: bool = False

                except Exception as e:
                    self._is_dirty: bool = True
                    print(e)
            except Warning as e:
                self._is_dirty: bool = True
                print(e)

        return self.output_data(0, result)

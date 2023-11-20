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
from typing import TYPE_CHECKING, Any, Optional

import awkward as ak

import FreeCAD

import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from utils import simplify_ak
from socket_widget import SocketWidget

if TYPE_CHECKING:
	from node_item import NodeItem


class VectorNone(SocketWidget):
	def __init__(
			self, undo_stack: QtWidgets.QUndoStack, name: str = "Vector", content_value: Any = "<No Input>",
			is_flatten: bool = False, is_simplify: bool = False, is_graft: bool = False, is_input: bool = True,
			parent_node: Optional[NodeItem] = None, parent_widget: Optional[QtWidgets.QWidget] = None
	) -> None:

		super().__init__(
			undo_stack, name, content_value, is_flatten, is_simplify, is_graft, is_input, parent_node, parent_widget
		)

		# Pin setup
		self._pin_item.color = QtGui.QColor("#6363C7")
		self._pin_item.pin_type = FreeCAD.Vector

		self.update_stylesheets()

	# --------------- Socket data ---------------

	def input_data(self) -> list:
		result: list = []
		if self._pin_item.has_edges():
			for edge in self._pin_item.edges:
				pre_node: NodeItem = edge.start_pin.parent_node
				if len(pre_node.sub_scene.nodes) > 0:
					result.append(pre_node.linked_lowest_socket(edge.start_pin.socket_widget).pin)
				else:
					result.append(edge.start_pin)
		else:
			linked_highest: SocketWidget = self.parent_node.linked_highest_socket(self)
			if linked_highest != self:
				result.extend(linked_highest.input_data())

		if len(result) == 0:
			result.append(ak.Array([{"x": 0., "y": 0., "z": 0.}]))

		return result

	def perform_socket_operation(self, input_data: ak.Array) -> ak.Array:
		if self.socket_options_state()[0]:  # Flatten
			x: ak.Array = ak.flatten(input_data.x, axis=None)
			y: ak.Array = ak.flatten(input_data.y, axis=None)
			z: ak.Array = ak.flatten(input_data.z, axis=None)
			input_data: ak.Array = ak.zip({"x": x, "y": y, "z": z})

		if self.socket_options_state()[1]:  # Simplify
			x: ak.Array = simplify_ak(input_data.x)
			y: ak.Array = simplify_ak(input_data.y)
			z: ak.Array = simplify_ak(input_data.z)
			input_data: ak.Array = ak.zip({"x": x, "y": y, "z": z})

		if self.socket_options_state()[2]:  # Graft
			input_data: ak.Array = ak.unflatten(input_data, axis=-1, counts=1)

		return input_data

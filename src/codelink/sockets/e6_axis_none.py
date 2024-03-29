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

from utils import simplify_record, flatten_record
from socket_widget import SocketWidget

if TYPE_CHECKING:
	from node_item import NodeItem


class E6AxisNone(SocketWidget):
	def __init__(
			self, undo_stack: QtWidgets.QUndoStack, name: str = "E6Axis", content_value: Any = "<No Input>",
			is_flatten: bool = False, is_simplify: bool = False, is_graft: bool = False, is_input: bool = True,
			parent_node: Optional[NodeItem] = None, parent_widget: Optional[QtWidgets.QWidget] = None
	) -> None:

		super().__init__(
			undo_stack, name, content_value, is_flatten, is_simplify, is_graft, is_input, parent_node, parent_widget
		)

		# Pin setup
		self._pin_item.color = QtGui.QColor("olive")
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
			result.append(ak.Array([{"a1": 0., "a2": 0., "a3": 0., "a4": 0., "a5": 0., "a6": 0.}]))

		return result

	def perform_socket_operation(self, input_data: ak.Array) -> ak.Array:
		if self.socket_options_state()[0]:  # Flatten
			input_data: ak.Array = flatten_record(input_data, False)

		if self.socket_options_state()[1]:  # Simplify
			input_data: ak.Array = simplify_record(input_data, False)

		if self.socket_options_state()[2]:  # Graft
			input_data: ak.Array = ak.unflatten(input_data, axis=-1, counts=1)

		return input_data

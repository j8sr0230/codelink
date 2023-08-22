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

# noinspection PyUnresolvedReferences
import FreeCAD
import Part

import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from socket_widget import SocketWidget

if TYPE_CHECKING:
	from node_item import NodeItem


class Shape(SocketWidget):
	def __init__(
			self, undo_stack: QtWidgets.QUndoStack, name: str = "Shp", content_value: str = str(Part.Shape()),
			is_flatten: bool = False, is_simplify: bool = False, is_graft: bool = False,
			is_graft_topo: bool = False, is_unwrap: bool = False, is_wrap: bool = False, is_input: bool = True,
			parent_node: Optional[NodeItem] = None, parent_widget: Optional[QtWidgets.QWidget] = None
	) -> None:

		super().__init__(
			undo_stack, name, content_value, is_flatten, is_simplify, is_graft, is_graft_topo, is_unwrap, is_wrap,
			is_input, parent_node, parent_widget
		)

		# Pin setup
		self._pin_item.color = QtGui.QColor("blue")
		self._pin_item.pin_type = Part.Shape

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
			result.append(Part.Shape())

		return result

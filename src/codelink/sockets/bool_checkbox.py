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
from typing import TYPE_CHECKING, Any, Optional, cast

import awkward as ak

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from utils import simplify_array
from socket_widget import SocketWidget
from input_widgets import BoolInputWidget

if TYPE_CHECKING:
	from node_item import NodeItem


class BoolCheckBox(SocketWidget):
	def __init__(
			self, undo_stack: QtWidgets.QUndoStack, name: str = "A", content_value: Any = False,
			is_flatten: bool = False, is_simplify: bool = False, is_graft: bool = False, is_input: bool = True,
			parent_node: Optional[NodeItem] = None, parent_widget: Optional[QtWidgets.QWidget] = None
	) -> None:

		super().__init__(
			undo_stack, name, content_value, is_flatten, is_simplify, is_graft, is_input, parent_node, parent_widget
		)

		# Pin setup
		self._pin_item.color = QtGui.QColor("#CCA6D6")
		self._pin_item.pin_type = bool

		# Input widget setup
		self._input_widget: BoolInputWidget = BoolInputWidget(undo_stack)
		self._input_widget.setMinimumWidth(5)
		self._input_widget.setLayoutDirection(QtCore.Qt.RightToLeft)
		self._input_widget.setChecked(bool(self._prop_model.properties["Value"]))
		self._content_layout.addWidget(self._input_widget)
		self._input_widget.setFocusPolicy(QtCore.Qt.StrongFocus)
		self.setFocusProxy(self._input_widget)

		self.update_stylesheets()

		# Listeners
		cast(QtCore.SignalInstance, self._input_widget.stateChanged).connect(self.editing_finished)

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
			result.append(ak.Array([bool(self._input_widget.checkState())]))

		return result

	def perform_socket_operation(self, input_data: ak.Array) -> ak.Array:
		if self.socket_options_state()[0]:  # Flatten
			input_data: ak.Array = ak.flatten(input_data, axis=None)

		if self.socket_options_state()[1]:  # Simplify
			input_data: ak.Array = simplify_array(input_data)

		if self.socket_options_state()[2]:  # Graft
			input_data: ak.Array = ak.unflatten(input_data, axis=-1, counts=1)

		return input_data

	# --------------- Callbacks ---------------

	def update_stylesheets(self) -> None:
		super().update_stylesheets()

		if self._is_input:
			if self._pin_item.has_edges() or self.link != ("", -1):
				self._label_widget.setStyleSheet("background-color: transparent")
				self._input_widget.hide()
				self._input_widget.setFocusPolicy(QtCore.Qt.NoFocus)
			else:
				self._label_widget.setStyleSheet("background-color: #545454")
				self._input_widget.show()
				self._input_widget.setFocusPolicy(QtCore.Qt.StrongFocus)
		else:
			self._input_widget.hide()

	def update_all(self):
		super().update_all()
		self._input_widget.setChecked(bool(self._prop_model.properties["Value"]))

	def validate_input(self):
		input_state: bool = bool(self._input_widget.checkState())
		self._prop_model.setData(self._prop_model.index(1, 1, QtCore.QModelIndex()), input_state, 2)

	def editing_finished(self) -> None:
		self.validate_input()

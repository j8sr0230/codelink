#!/usr/bin/env python

# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2024 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
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

import networkx as nx

import PySide2.QtCore as QtCore

from codelink.backend.user_roles import UserRoles
from codelink.backend.tree_model import TreeModel


class EdgeValidator:
    def __init__(self, model: TreeModel) -> None:
        self._model: TreeModel = model

    def can_connect(self, source: QtCore.QModelIndex, destination: QtCore.QModelIndex) -> bool:
        di_graph: nx.DiGraph = self._model.to_nx()

        if self._model.is_input(source) and self._model.is_output(destination):
            temp: QtCore.QModelIndex = destination
            destination: QtCore.QModelIndex = source
            source: QtCore.QModelIndex = temp

        if source.parent().parent() == destination.parent().parent():
            return False

        if source == destination:
            return False

        if self._model.is_input(source) and self._model.is_input(destination):
            return False

        if self._model.is_output(source) and self._model.is_output(destination):
            return False

        di_graph.add_edge(
            source.parent().parent().data(UserRoles.UUID),
            destination.parent().parent().data(UserRoles.UUID)
        )

        try:
            nx.find_cycle(di_graph)
        except nx.exception.NetworkXNoCycle:
            return True
        else:
            return False

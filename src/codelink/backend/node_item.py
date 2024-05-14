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

from typing import Optional, Any

from tree_item import TreeItem
from base_item import BaseItem
from seperator_item import SeperatorItem


class NodeItem(BaseItem):
    def __init__(self, key: str, value: Any = None, uuid: Optional[str] = None,
                 parent: Optional[TreeItem] = None) -> None:
        super().__init__(key, value, uuid, parent)

        self._pos: tuple[float, float] = (0, 0)

    @property
    def pos(self) -> tuple[float, float]:
        return self._pos

    @pos.setter
    def pos(self, value: tuple[float, float]) -> None:
        self._pos: tuple[float, float] = value

    def setup_children(self) -> None:
        self.append_child(SeperatorItem("Base"))
        self.append_child(SeperatorItem("Inputs"))
        self.append_child(SeperatorItem("Outputs"))
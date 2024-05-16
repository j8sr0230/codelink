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

from codelink.backend.tree_item import TreeItem
from codelink.backend.base_item import BaseItem
from codelink.backend.seperator_item import SeperatorItem


class NodeItem(BaseItem):
    def __init__(self, key: str, value: Any = None, pos: Optional[list[int]] = None,
                 uuid: Optional[str] = None, parent: Optional[TreeItem] = None) -> None:
        super().__init__(key, value, uuid, parent)

        if pos is None:
            pos: list[int] = [0, 0]

        self._pos: list[int] = pos

    @property
    def pos(self) -> list[int]:
        return self._pos

    @pos.setter
    def pos(self, value: list[int]) -> None:
        self._pos: list[int] = value

    def setup_children(self) -> None:
        self.append_child(SeperatorItem("Base"))
        self.append_child(SeperatorItem("Inputs"))
        self.append_child(SeperatorItem("Outputs"))

    def __getstate__(self) -> dict[str, Any]:
        state: dict[str, Any] = super().__getstate__()
        state["pos"] = self._pos
        return state

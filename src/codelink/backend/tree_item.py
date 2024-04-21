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

from __future__ import annotations
from typing import Optional, Any


class TreeItem(object):
    def __init__(self, parent: Optional[TreeItem] = None) -> None:
        self._parent: Optional[TreeItem] = parent
        self._children: list[TreeItem] = []

    @property
    def parent(self) -> Optional[TreeItem]:
        return self._parent

    @parent.setter
    def parent(self, value: Optional[TreeItem]) -> None:
        self._parent: Optional[TreeItem] = value

    @property
    def children(self) -> list[TreeItem]:
        return self._children

    @children.setter
    def children(self, value: list[TreeItem]) -> None:
        self._children: list[TreeItem] = value

    def append_child(self, child: TreeItem) -> None:
        child.parent = self
        self._children.append(child)

    def child(self, row: int) -> Optional[TreeItem]:
        if 0 <= row < len(self._children):
            return self._children[row]
        return None

    def remove_child(self, row: int) -> None:
        if 0 <= row < len(self._children):
            child: TreeItem = self._children[row]
            child.parent = None
            self._children.remove(child)

    def row(self) -> int:
        if self._parent is not None:
            return self._parent.children.index(self)
        return 0

    def __getstate__(self) -> dict[str, Any]:
        state: dict = {}
        return state

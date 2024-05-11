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

import PySide2.QtCore as QtCore


class TreeItem(object):
    def __init__(self, uuid: Optional[str] = None, parent: Optional[TreeItem] = None) -> None:
        self._uuid: str = uuid if uuid else QtCore.QUuid.createUuid().toString()
        self._parent: Optional[TreeItem] = parent
        self._children: list[TreeItem] = []

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str) -> None:
        self._uuid: str = value

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

    def insert_child(self, row: int, child: TreeItem) -> bool:
        child.parent = self
        row: int = max(0, min(row, len(self._children)))
        self._children.insert(row, child)
        return True

    def append_child(self, child: TreeItem) -> bool:
        return self.insert_child(len(self._children), child)

    def child(self, row: int) -> Optional[TreeItem]:
        if 0 <= row < len(self._children):
            return self._children[row]
        return None

    def remove_child(self, row: int) -> bool:
        if 0 <= row < len(self._children):
            child: TreeItem = self._children[row]
            child.parent = None
            self._children.remove(child)
            return True

        return False

    def row(self) -> int:
        if self._parent is not None:
            return self._parent.children.index(self)
        return 0

    def __getstate__(self) -> dict[str, Any]:
        state: dict = {
            "type": self.__class__.__name__,
            "uuid": self._uuid
        }
        return state

    def __repr__(self) -> str:
        result: str = f"<{type(self).__module__}.{type(self).__name__} {self._uuid} at 0x{id(self):x}"
        result += f", {len(self._children)} children>"
        return result

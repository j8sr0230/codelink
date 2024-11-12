#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ************************************************************************
# * Copyright (c) 2024 Ronny Scharf-W. <ronny.scharf08@gmail.com>        *
# *                                                                      *
# * This program is free software; you can redistribute it and/or modify *
# * it under the terms of the GNU Lesser General Public License (LGPL)   *
# * as published by the Free Software Foundation; either version 2 of    *
# * the License, or (at your option) any later version.                  *
# * for detail see the LICENSE text file.                                *
# *                                                                      *
# * This program is distributed in the hope that it will be useful,      *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of       *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the         *
# * GNU Library General Public License for more details.                 *
# *                                                                      *
# * You should have received a copy of the GNU Library General Public    *
# * License along with this program; if not, write to the Free Software  *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  *
# * USA                                                                  *
# *                                                                      *
# ************************************************************************

from __future__ import annotations


class Item:
    def __init__(self, parent: Item | None = None) -> None:
        self._parent: Item | None = parent
        self._children: list[Item] = []

    @property
    def parent(self) -> Item | None:
        return self._parent

    @parent.setter
    def parent(self, value: Item | None) -> None:
        self._parent: Item | None = value

    @property
    def children(self) -> list[Item]:
        return self._children

    def insert_child(self, row: int, child: Item) -> bool:
        child.parent = self
        row: int = max(0, min(row, len(self._children)))
        self._children.insert(row, child)
        return True

    def append_child(self, child: Item) -> bool:
        return self.insert_child(len(self._children), child)

    def remove_child(self, row: int) -> bool:
        if 0 <= row < len(self._children):
            child: Item = self._children[row]
            child.parent = None
            self._children.remove(child)
            return True
        return False

    def child_count(self) -> int:
        return len(self._children)

    def child(self, row: int) -> Item | None:
        return self._children[row] if 0 <= row < self.child_count() else None

    def last_child(self) -> Item | None:
        return self._children[-1] if self._children else None

    def item_row(self) -> int:
        if self._parent is not None:
            return self._parent.children.index(self)
        return 0

    def __getstate__(self) -> dict:
        state: dict = {
            "class": self.__class__.__module__ + "." + self.__class__.__name__,
        }
        return state

    def __repr__(self) -> str:
        result: str = f"<{type(self).__module__}.{type(self).__name__} at 0x{id(self):x}"
        result += f", {len(self._children)} children>"
        return result

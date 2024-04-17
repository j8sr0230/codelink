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
from typing import Optional


class DataItem(object):
    def __init__(self, parent: Optional[DataItem] = None):
        self._parent: Optional[DataItem] = parent
        self._children: list[DataItem] = []

    @property
    def parent(self) -> Optional[DataItem]:
        return self._parent

    @parent.setter
    def parent(self, value: Optional[DataItem]) -> None:
        self._parent: Optional[DataItem] = value

    @property
    def children(self) -> list[DataItem]:
        return self._children

    @children.setter
    def children(self, value: list[DataItem]) -> None:
        self._children: list[DataItem] = value

    def append_child(self, child: DataItem) -> None:
        child.parent = self
        self._children.append(child)

    def remove_child(self, child: DataItem) -> None:
        child.parent = None
        if child in self._children:
            self._children.remove(child)

    def child_count(self) -> int:
        return len(self._children)

    def child(self, row: int) -> Optional[DataItem]:
        if 0 <= row < self.child_count():
            return self._children[row]
        return None

    def row(self) -> int:
        if self._parent is not None:
            return self._parent.children.index(self)
        return 0


if __name__ == "__main__":
    root_item: DataItem = DataItem(parent=None)
    data_item_1: DataItem = DataItem(parent=None)
    data_item_2: DataItem = DataItem(parent=None)

    print(data_item_1.row(), data_item_2.row())
    root_item.append_child(data_item_1)
    root_item.append_child(data_item_2)
    print(data_item_1.row(), data_item_2.row())

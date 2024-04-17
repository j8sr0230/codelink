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


class DataItem(object):
    def __init__(self, parent: Optional[DataItem] = None):
        self._parent: Optional[DataItem] = parent
        self._children: list[DataItem] = []

    @property
    def parent(self) -> Optional[DataItem]:
        return self._parent

    @property
    def children(self) -> list[DataItem]:
        return self._children

    def insert_child(self, child: DataItem, position: int) -> bool:
        if 0 <= position < len(self._children):
            self._children.insert(position, child)
            return True
        else:
            return False

    def child_row_number(self) -> int:
        if self._parent is not None and self in self._parent.children:
            return self._parent.children.index(self)

        return 0

    def child_count(self) -> int:
        return len(self._children)

    def child(self, row: int) -> Any:
        if 0 <= row < self.child_count():
            return self._children[row]

        return None

    def remove_children(self, position, count):
        if position < 0 or position + count > len(self._children):
            return False

        for row in range(count):
            self._children.pop(position)

        return True


if __name__ == "__main__":
    root_item: DataItem = DataItem(parent=None)
    root_item.insert_children(position=0, count=1)

    data_item: DataItem = root_item.child(0)
    print(data_item.child_row_number())

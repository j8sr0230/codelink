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

from typing import Any, Optional, cast

from data_item import DataItem


class DataProperty(DataItem):
    def __init__(self, key: str, value: Any, parent: Optional[DataItem] = None):
        super().__init__(parent)

        self._key: str = key
        self._value: Any = value

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, value: str) -> None:
        self._key: str = value

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value: Any = value


if __name__ == "__main__":
    root_item: DataItem = DataItem(parent=None)
    data_item: DataItem = DataItem(parent=None)
    prop_item: DataProperty = DataProperty(key="Number", value=10, parent=None)

    root_item.append_child(data_item)
    root_item.append_child(prop_item)

    child_item: DataItem = root_item.child(root_item.child_count() - 1)
    if type(child_item) is DataProperty:
        child_item: DataProperty = cast(DataProperty, child_item)
        print(child_item.key, child_item.value)

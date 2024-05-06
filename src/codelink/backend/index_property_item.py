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

import PySide2.QtCore as QtCore

from property_item import PropertyItem


class IndexPropertyItem(PropertyItem):
    def __init__(self, key: str, value: QtCore.QModelIndex, parent: Optional[PropertyItem] = None) -> None:
        super().__init__(key, value, parent)

    def __getstate__(self) -> dict[str, Any]:
        state: dict[str, Any] = super().__getstate__()
        state["key"] = self._key
        state["value"] = str(self._value)
        return state

    def __repr__(self) -> str:
        result: str = f"<index_property_item.IndexPropertyItem at 0x{id(self):x}"
        result += f", {len(self._children)} children>"
        return result

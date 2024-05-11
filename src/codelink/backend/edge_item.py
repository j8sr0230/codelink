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

from typing import Any, Optional

from tree_item import TreeItem


class EdgeItem(TreeItem):
    def __init__(self, source_uuid: str, destination_uuid: str, uuid: Optional[str] = None,
                 parent: Optional[TreeItem] = None) -> None:
        super().__init__(uuid, parent)

        self._source_uuid: str = source_uuid
        self._destination_uuid: str = destination_uuid

    @property
    def source_uuid(self) -> str:
        return self._source_uuid

    @source_uuid.setter
    def source_uuid(self, value: str) -> None:
        self._source_uuid: str = value

    @property
    def destination_uuid(self) -> str:
        return self._destination_uuid

    @destination_uuid.setter
    def destination_uuid(self, value: str) -> None:
        self._destination_uuid: str = value

    def __getstate__(self) -> dict[str, Any]:
        state: dict[str, Any] = super().__getstate__()
        state["source"] = self._source_uuid
        state["destination"] = self._destination_uuid
        return state

    def __repr__(self) -> str:
        result: str = f"<connection_item.EdgeItem {self._uuid} at 0x{id(self):x}"
        result += f", {len(self._children)} children>"
        return result

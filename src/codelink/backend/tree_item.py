#!/usr/bin/env python

############################################################################
#
# Copyright (C) 2005-2005 Trolltech AS. All rights reserved.
# Modified 2024 by Ronny Scharf-W. (ronny.scharf08@gmail.com).
#
# This file is part of the example classes of the Qt Toolkit.
#
# This file may be used under the terms of the GNU General Public
# License version 2.0 as published by the Free Software Foundation
# and appearing in the file LICENSE.GPL included in the packaging of
# this file.  Please review the following information to ensure GNU
# General Public Licensing requirements will be met:
# http://www.trolltech.com/products/qt/opensource.html
#
# If you are unsure which license is appropriate for your use, please
# review the following information:
# http://www.trolltech.com/products/qt/licensing.html or contact the
# sales department at sales@trolltech.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
############################################################################

from __future__ import annotations
from typing import Optional, Any


class TreeItem:
    def __init__(self, data: list[Any], parent: Optional[TreeItem] = None):
        self._parent_item: Optional[TreeItem] = parent
        self._item_data: list[Any] = data
        self._child_items: list[TreeItem] = []

    def parent(self) -> TreeItem:
        return self._parent_item

    def data(self, column: int) -> Any:
        if column < self.column_count():
            return self._item_data[column]
        return None

    def set_data(self, column: int, value: Any) -> bool:
        if column < 0 or column >= len(self._item_data):
            return False

        self._item_data[column] = value
        return True

    def column_count(self) -> int:
        return len(self._item_data)

    def insert_columns(self, position: int, columns: int) -> bool:
        if position < 0 or position > len(self._item_data):
            return False

        for column in range(columns):
            self._item_data.insert(position, None)

        for child in self._child_items:
            child.insert_columns(position, columns)

        return True

    def remove_columns(self, position: int, columns: int) -> bool:
        if position < 0 or position + columns > len(self._item_data):
            return False

        for column in range(columns):
            self._item_data.pop(position)

        for child in self._child_items:
            child.remove_columns(position, columns)

        return True

    def child_number(self) -> int:
        if self._parent_item is not None:
            return self._parent_item._child_items.index(self)
        return 0

    def child_count(self) -> int:
        return len(self._child_items)

    def child(self, row: int) -> Any:
        if self.child_count() > 0:
            return self._child_items[row]
        return None

    def insert_children(self, position: int, count: int, columns: int) -> bool:
        if position < 0 or position > len(self._child_items):
            return False

        for row in range(count):
            data: list[Any] = [None] * columns
            item: TreeItem = TreeItem(data, self)
            self._child_items.insert(position, item)

        return True

    def remove_children(self, position, count):
        if position < 0 or position + count > len(self._child_items):
            return False

        for row in range(count):
            self._child_items.pop(position)

        return True


if __name__ == "__main__":
    root_item: TreeItem = TreeItem(data=["Key", "Value"], parent=None)
    root_item.insert_children(0, 1, 2)

    data_item: TreeItem = root_item.child(0)
    data_item.set_data(0, "Color")
    data_item.set_data(1, "#1D1D1D")

    root_item.insert_columns(root_item.column_count(), 2)
    print(data_item.child_number(), data_item.data(0), data_item.data(1))

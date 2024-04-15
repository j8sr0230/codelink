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


class TreeItem(object):
    def __init__(self, data: list[str, Any], parent: Optional[TreeItem] = None):
        self._data: list[str, Any] = data
        self._parent: Optional[TreeItem] = parent
        self._children: list[TreeItem] = []

    @property
    def parent(self) -> Optional[TreeItem]:
        return self._parent

    @property
    def children(self) -> list[TreeItem]:
        return self._children

    def data(self, column: int) -> Any:
        if 0 <= column < 2:
            return self._data[column]

        return None

    def set_data(self, column: int, value: Any) -> bool:
        if column < 0 or column >= 2:
            return False

        self._data[column] = value
        return True

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

    def insert_children(self, position: int, count: int) -> bool:
        if position < 0 or position > len(self._children):
            return False

        for row in range(count):
            item: TreeItem = TreeItem(["", None], self)
            self._children.insert(position, item)

        return True

    def remove_children(self, position, count):
        if position < 0 or position + count > len(self._children):
            return False

        for row in range(count):
            self._children.pop(position)

        return True


if __name__ == "__main__":
    import PySide2.QtGui as QtGui

    root_item: TreeItem = TreeItem(data=["Key", "Value"], parent=None)
    root_item.insert_children(position=0, count=1)

    data_item: TreeItem = root_item.child(0)
    data_item.set_data(column=0, value="Color")
    data_item.set_data(column=1, value=QtGui.QColor("#1D1D1D"))

    print(root_item.data(0), root_item.data(1))
    print(data_item.child_row_number(), data_item.data(0), data_item.data(1))

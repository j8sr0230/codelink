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
from typing import Any, Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from codelink.backend.tree_model import TreeModel


class DocumentModel(TreeModel):
    def __init__(self, data: Optional[dict[str, Any]] = None, undo_stack: Optional[QtWidgets.QUndoStack] = None,
                 parent: QtCore.QObject = None) -> None:
        super().__init__(data, undo_stack, parent)

        self._file_name: Optional[str] = None
        self._is_modified: bool = False

    @property
    def file_name(self) -> Optional[str]:
        return self._file_name

    @file_name.setter
    def file_name(self, value: Optional[str]) -> None:
        self._file_name: Optional[str] = value

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @is_modified.setter
    def is_modified(self, value: bool) -> None:
        self._is_modified: bool = value

    def get_title(self) -> str:
        title: str = self._file_name if self._file_name else "untitled"
        title: str = title + "*" if self._is_modified else title
        return title

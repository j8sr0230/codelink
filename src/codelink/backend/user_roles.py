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

from enum import IntEnum

import PySide2.QtCore as QtCore


class UserRoles(IntEnum):
    TYPE: int = QtCore.Qt.UserRole + 1
    UUID: int = QtCore.Qt.UserRole + 2
    KEY: int = QtCore.Qt.UserRole + 3
    VALUE: int = QtCore.Qt.UserRole + 4
    COLOR: int = QtCore.Qt.UserRole + 5
    POS: int = QtCore.Qt.UserRole + 6
    SRC: int = QtCore.Qt.UserRole + 7
    DEST: int = QtCore.Qt.UserRole + 8
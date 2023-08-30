# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2023 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
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
import FreeCAD
import awkward as ak
import numpy as np

from utils import map_last_level, flatten


a = ak.Array([
    [[1, 0, 0], [2, 0, 0]], [1, 2, 3], [1, 2, 3], [6, 7, 8], [8, 8, 8]
])

b = ak.Array([
    [1, 0, 0], [2, 0, 0], [1, 2, 3], [1, 2, 3], [6, 7, 8], [8, 8, 8]
])

ak.local_index(a).show()
min_depth: int = a.layout.minmax_depth[0]
ak.flatten(a, axis=min_depth-2).show()

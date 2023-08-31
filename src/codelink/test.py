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

import awkward as ak


v1 = ak.Array(
    [[[{"x": 1, "y": 0, "z": 0}, {"x": 1.1, "y": 0.1, "z": 0}]], [],
     [[{"x": 0.2, "y": 1, "z": 0}], [{"x": 3.1, "y": 0.9, "z": 0}]]
     ], with_name="Vector3D"
)
v2 = ak.Array(
    [[{"x": 0, "y": 1, "z": 0}], [],
     [{"x": -2.2, "y": 0.0, "z": 0}, {"x": 1.1, "y": 0.9, "z": 0}]
     ], with_name="Vector3D"
)

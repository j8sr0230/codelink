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
import numpy as np


one = ak.Array([[[{"x": 0, "y": 2, "z": 0}, {"x": 2, "y": 2.2, "z": 0}], {"x": 3, "y": 0, "z": 0}],
                [],
                [{"x": 4, "y": 4.4, "z": 0}, {"x": 5, "y": 5.5, "z": 0}],
                [{"x": 6, "y": 6.6, "z": 0}],
                [[{"x": 7, "y": 7.7, "z": 0}], [{"x": 8, "y": 8.8, "z": 0}], [{"x": 9, "y": 9.9, "z": 0}]]],
               with_name="vector3D")

two = ak.Array([[{"x": 1, "y": 0, "z": 0}, {"x": 0, "y": 0, "z": 0}],
                [],
                [{"x": 3.9, "y": 4, "z": 0}, {"x": 5, "y": 5.5, "z": 0}],
                [{"x": 5.9, "y": 6, "z": 0}],
                [{"x": 6.9, "y": 7, "z": 0}, {"x": 8, "y": 8.8, "z": 0}, {"x": 8.9, "y": 9, "z": 0}]],
               with_name="vector3D")

# (one * two)

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

v3 = ak.Array([[[{"x": 0, "y": 2, "z": 0}, {"x": 2, "y": 2.2, "z": 0}], {"x": 3, "y": 0, "z": 0}],
               [],
               [{"x": 4, "y": 4.4, "z": 0}, {"x": 5, "y": 5.5, "z": 0}],
               [{"x": 6, "y": 6.6, "z": 0}],
               [[{"x": 7, "y": 7.7, "z": 0}], [{"x": 8, "y": 8.8, "z": 0}], [{"x": 9, "y": 9.9, "z": 0}]]],
              with_name="Vector3D")

v4 = ak.Array([[{"x": 1, "y": 0, "z": 0}, {"x": 0, "y": 0, "z": 0}],
               [],
               [{"x": 3.9, "y": 4, "z": 0}, {"x": 5, "y": 5.5, "z": 0}],
               [{"x": 5.9, "y": 6, "z": 0}],
               [{"x": 6.9, "y": 7, "z": 0}, {"x": 8, "y": 8.8, "z": 0}, {"x": 8.9, "y": 9, "z": 0}]],
              with_name="Vector3D")

np.multiply(v3, v4).show()

ak.behavior[np.multiply, np.ndarray, np.ndarray] = np.multiply


# def test(left, right):
#     print("l", left)
#     return ak.Array(
#         [
#             1, # left[1] * right[2] - left[2] * right[1],
#             2, # left[2] * right[0] - left[0] * right[2],
#             3, # left[0] * right[1] - left[1] * right[0]
#         ]
#     )
#
#
# ak.behavior[np.multiply, "v3", "v3"] = test
#
# l1 = ak.with_parameter([[1, 0, 0], [4, 8, 0], [2, 4, 0]], "__list__", "v3")
# l2 = ak.with_parameter([[0, 1, 0], [4, 0, 7], [5, 6, 7]], "__list__", "v3")
#
#
# (l1 * l2).show()

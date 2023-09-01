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

import time

import awkward as ak
import numpy as np


# v1 = ak.Array(
#     [[[{"x": 1, "y": 0, "z": 0}, {"x": 1.1, "y": 0.1, "z": 0}]], [],
#      [[{"x": 0.2, "y": 1, "z": 0}], [{"x": 3.1, "y": 0.9, "z": 0}]]
#      ], with_name="Vector3D"
# )
# v2 = ak.Array(
#     [[{"x": 0, "y": 1, "z": 0}], [],
#      [{"x": -2.2, "y": 0.0, "z": 0}, {"x": 1.1, "y": 0.9, "z": 0}]
#      ], with_name="Vector3D"
# )
#
#
# from_columns = ak.Array(
#     {
#         "x": [1, 2, 3, 4, 5],
#         "y": [1.1, 2.2, 3.3, 4.4, 5.5],
#         "z": ["one", "two", "three", "four", "five"],
#     }
# )
# from_columns.show()


def vector_add(a, b):
    return ak.contents.RecordArray(
        [
            ak.to_layout(a.x + b.x),
            ak.to_layout(a.y + b.y),
            ak.to_layout(a.z + b.z),
        ],
        ["x", "y", "z"],
        parameters={"__record__": "Vector3D"},
    )


def vector_sub(a, b):
    return ak.contents.RecordArray(
        [
            ak.to_layout(a.x - b.x),
            ak.to_layout(a.y - b.y),
            ak.to_layout(a.z - b.z),
        ],
        ["x", "y", "z"],
        parameters={"__record__": "Vector3D"},
    )


ak.behavior[np.add, "Vector3D", "Vector3D"] = vector_add
ak.behavior[np.subtract, "Vector3D", "Vector3D"] = vector_sub

start = time.perf_counter()

x = [np.arange(0, 1000000).tolist()]
y = [0]
z = [0]

a = ak.zip({"x": x, "y": y, "z": z})
b = ak.Array([{"x": 1, "y": 0, "z": 0}])
res = ak.Array(a, with_name="Vector3D") + ak.Array(b, with_name="Vector3D")

end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")

# print(res.to_list())

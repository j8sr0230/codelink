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


# def vector_add(a, b):
#     return ak.contents.RecordArray(
#         [
#             ak.to_layout(a.x + b.x),
#             ak.to_layout(a.y + b.y),
#             ak.to_layout(a.z + b.z),
#         ],
#         ["x", "y", "z"],
#         parameters={"__record__": "Vector3D"},
#     )
#
#
# def vector_sub(a, b):
#     return ak.contents.RecordArray(
#         [
#             ak.to_layout(a.x - b.x),
#             ak.to_layout(a.y - b.y),
#             ak.to_layout(a.z - b.z),
#         ],
#         ["x", "y", "z"],
#         parameters={"__record__": "Vector3D"},
#     )
#
#
# ak.behavior[np.add, "Vector3D", "Vector3D"] = vector_add
# ak.behavior[np.subtract, "Vector3D", "Vector3D"] = vector_sub

start = time.perf_counter()

x = np.arange(0, 1000000)  # [:, np.newaxis]
y = [0]
z = [0]

v1 = ak.Array([{"x": 1, "y": 1, "z": 1}], with_name="Vector3D")
v2 = ak.Array([{"x": 2, "y": 2, "z": 2}], with_name="Vector3D")

v3 = ak.concatenate([v1, v2])
v3 = v3[None, :]  # Wrapping generates max recursion exception
# v3 = ak.Array([v3])  # Works but maybe slow
v3 = ak.flatten(ak.flatten(ak.broadcast_arrays(v3[None, :])))  # Works

v4 = ak.concatenate([v1, v3])

res = ak.zip({"x": v1.x + v4.x, "y": v1.y + v4.y, "z": v1.z + v4.z})

end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")

res.show()

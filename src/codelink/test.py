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

x = np.arange(0, 1)  # [:, np.newaxis]
y = [0]
z = [0]

v1 = ak.zip({"x": x, "y": y, "z": z})
v1 = ak.concatenate([v1, v1])
v2 = ak.Array([{"x": 1, "y": 0, "z": 0}])
res = ak.Array(v1, with_name="Vector3D") + ak.Array(v2, with_name="Vector3D")

end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")

# res.show()
# ak.unflatten(res, axis=-1, counts=1).show()

v1 = ak.Array([{"x": 1, "y": 2, "z": 3}, {"x": 1, "y": 2, "z": 3}, {"x": 1, "y": 2, "z": 3}])
v1.show()
print(ak.num(v1, axis=0))
ak.unflatten(v1, axis=1, counts=3).show()

# v1 = ak.Array([{"x": 1, "y": 2, "z": 3}])
# v1.show()
# v1[:, np.newaxis].show()

x1: ak.Array = ak.Array([1, [1, 2], 2])
x2: ak.Array = ak.Array([5])

x1.show()
x2.show()

(x1 + x2).show()

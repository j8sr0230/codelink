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
from numba import jit


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

x = np.arange(0, 10)
y = [0]
z = [0]

v1 = ak.zip({"x": x, "y": y, "z": z})
v1 = ak.Array(v1, with_name="Vector3D")

v2 = ak.Array([{"x": 2, "y": 2, "z": 2}], with_name="Vector3D")
v3 = ak.concatenate([v1, v2])

start = time.perf_counter()

# v3_1 = v3[None, :]  # Works not, raises max recursion exception
v3_1 = ak.contents.ListOffsetArray(content=ak.to_layout(v3), offsets=ak.index.Index64([0, 2]))  # Fastest solution
# v3_1 = ak.Array([v3], with_name="Vector3D")  # Works but slower

end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")

v4 = ak.concatenate([v1, v3_1])
res = v2 + v4
res.show()

print()
k: ak.Array = ak.Array([[99], [[[3, 4, 87]]], np.arange(0, 5)])
# print(simplify(k.to_list()))

x = np.arange(100).reshape(10, 10)
print(x)


@jit(nopython=True)
def go_fast(a):  # Function is compiled and runs in machine code
    trace = 0.0
    for i in range(a.shape[0]):
        trace += np.tanh(a[i, i])
    return a + trace


# DO NOT REPORT THIS... COMPILATION TIME IS INCLUDED IN THE EXECUTION TIME!
start = time.time()
go_fast(x)
end = time.time()
print("Elapsed (with compilation) = %s" % (end - start))

# NOW THE FUNCTION IS COMPILED, RE-TIME IT EXECUTING FROM CACHE
start = time.time()
go_fast(x)
end = time.time()
print("Elapsed (after compilation) = %s" % (end - start))


@jit(nopython=True)
def simplify(nested_list: list) -> list:
    result: list = []

    copy: list = nested_list[:]
    while copy:
        entry: list = copy[1]

        if isinstance(entry, list):
            contains_lists: bool = True
            for i in entry:
                if not isinstance(i, list):
                    contains_lists: bool = False

            if len(list(entry)) > 0 and not contains_lists:
                result.append(entry)
            else:
                copy = entry
                # copy.extend(entry)
        else:
            result.append(entry)

    # result.reverse()
    return result


print(simplify(k.to_list()))
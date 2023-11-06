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

from typing import Any
import time
from collections.abc import Iterable

# import awkward as ak
import numpy as np

# noinspection PyUnresolvedReferences
import FreeCAD
import Part

from utils import flatten, flatten_nested_list, simplify, simplify_nested_list, graft, graft_nested_list, \
    map_nested_list, map_objects, map_last_nesting_level, map_last_level


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
#
# x = np.arange(0, 10)
# y = [0]
# z = [0]
#
# v1 = ak.zip({"x": x, "y": y, "z": z})
# v1 = ak.Array(v1, with_name="Vector3D")
#
# v2 = ak.Array([{"x": 2, "y": 2, "z": 2}], with_name="Vector3D")
# v3 = ak.concatenate([v1, v2])
#
# start = time.perf_counter()
#
# # v3_1 = v3[None, :]  # Works not, raises max recursion exception
# v3_1 = ak.contents.ListOffsetArray(content=ak.to_layout(v3), offsets=ak.index.Index64([0, 2]))  # Fastest solution
# # v3_1 = ak.Array([v3], with_name="Vector3D")  # Works but slower
#
# end = time.perf_counter()
# ms = (end - start) * 10 ** 3
# print(f"Elapsed: {ms:.03f} milliseconds.")
#
# v4 = ak.concatenate([v1, v3_1])
# res = v2 + v4
# res.show()
#
# print()
# u = ak.flatten(ak.Array([[1], [[[1, 1]]], [1]]), axis=1)
# v = ak.flatten(ak.Array([[2], [[[2, 2]]], [2]]), axis=1)
# w = ak.flatten(ak.Array([[3], [[[3, 3]]], [3]]), axis=1)
# u.show()
# res = ak.zip({"x": u, "y": v, "z": w})
# res.show()
#
# t: ak.Array = ak.Array([[[0], [1], [2], [3], [4]]])
# p: ak.Array = ak.Array([0])
# (t + p).show()

print("Original")
o: list = [0, [[[100, 200, 300]]], 300, [[[200]]], [17, [[np.arange(0, 1e1, 1).tolist()]]], 99, []]
# print(o)
print()

print("Flatten")
start = time.perf_counter()
res_0: list[Any] = flatten_nested_list(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
# print(res_0)

start = time.perf_counter()
res_1: Iterable = flatten(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
# print(res_1)
print()

print("Simplify")
start = time.perf_counter()
res: list[Any] = simplify_nested_list(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
# print(res)

start = time.perf_counter()
res: Iterable = simplify(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
# print(res)
print()

print("Graft")
start = time.perf_counter()
res: list[Any] = graft_nested_list(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
#print(res)

start = time.perf_counter()
res: Iterable = graft(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
# print(res)
print()

def square(x):
    return x * x


print("Map")
start = time.perf_counter()
res: list[Any] = map_nested_list(square, o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
print(res)

start = time.perf_counter()
res: list[Any] = map_objects(o, int | float, square)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
print(res)
print()

print("Map last")
start = time.perf_counter()
res: list[Any] = map_last_nesting_level(np.sum, o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
print(res)

start = time.perf_counter()
res: list[Any] = map_last_level(o, int | float, np.sum)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
print(res)

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

# noinspection PyUnresolvedReferences
import FreeCAD
import Part

from utils import flatten, flatten_it, simplify, simplify_it, graft, graft_re, \
    map_re, map_objects, map_last_re, map_last_level, ListWrapper
from nested_data import NestedData


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
u = ak.flatten(ak.Array([[1], [[[1, 1]]], [1]]), axis=1)
v = ak.flatten(ak.Array([[2], [[[2, 2]]], [2]]), axis=1)
w = ak.flatten(ak.Array([[3], [[[3, 3]]], [3]]), axis=1)
u.show()
res = ak.zip({"x": u, "y": v, "z": w})
res.show()

t: ak.Array = ak.Array([[[0], [1], [2], [3], [4]]])
p: ak.Array = ak.Array([0])
(t + p).show()

print("Original")
o: list = [0, [[[100., 200., 300.]]], 300., [[[200.]]], [17., [[np.arange(0., 1e1, 1.).tolist()]]], 99., []]
# print(o)
print()

print("Flatten")
start = time.perf_counter()
flatten_it(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")

start = time.perf_counter()
flatten(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
print()

print("Simplify")
start = time.perf_counter()
simplify_it(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")

start = time.perf_counter()
simplify(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
print()

print("Graft")
start = time.perf_counter()
graft_re(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")

start = time.perf_counter()
graft(o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
print()


def square(x_in: float) -> float:
    return x_in * x_in


print("Map")
start = time.perf_counter()
map_re(square, o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")

start = time.perf_counter()
map_objects(o, float, square)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
print()

print("Map last")
start = time.perf_counter()
map_last_re(np.sum, o)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")

start = time.perf_counter()
map_last_level(o, float, np.sum)
end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
print()

print("Map last level")
# t: ak.Array = ak.Array(
#     [
#         [
#             [
#                 [[
#                     [{"x": 0., "y": 0., "z": 0.}, {"x": 1., "y": 0., "z": 0.}]
#                 ]]
#             ],
#             [
#                 {"x": 0., "y": 1., "z": 0.}, {"x": 1., "y": 1., "z": 0.}, {"x": 2., "y": 1., "z": 0.},
#
#             ]
#         ]
#     ]
# )

x: np.ndarray = np.arange(0, 1e2)
y: list = [np.arange(0, 1e3)]
z: list = [0]

t = ak.zip({"x": x, "y": y, "z": z})
# t.show()

start = time.perf_counter()

ones: ak.Array = ak.ones_like(t.x)
indices: ak.Array = ak.local_index(ones)
flat_indices: ak.Array = ak.flatten(indices, axis=None)
splitter: np.ndarray = np.where(np.append(flat_indices, 0) == 0)[0]
last_level_length: np.ndarray = np.diff(splitter)

x_data: ak.Array = ak.unflatten(ak.flatten(t.x, axis=None), counts=last_level_length)
y_data: ak.Array = ak.unflatten(ak.flatten(t.y, axis=None), counts=last_level_length)
z_data: ak.Array = ak.unflatten(ak.flatten(t.z, axis=None), counts=last_level_length)

last_level_zip: list[list[tuple[float, float, float]]] = ak.to_list(ak.zip([x_data, y_data, z_data]))
last_level_vectors: list[list[FreeCAD.Vector]] = [
    [FreeCAD.Vector(vec) for vec in last_level] for last_level in last_level_zip
]
polylines: list[Part.Shape] = [Part.makePolygon(last_level, False) for last_level in last_level_vectors]
new_nested: NestedData = NestedData(polylines, ak.firsts(ones))

end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")

print("Data length:", len(new_nested.data))
print(new_nested.structure)
Part.show(Part.makeCompound(new_nested.data))
print()


def make_polyline(data: ListWrapper) -> Part.Shape:
    pos: list[FreeCAD.Vector] = data.wrapped_data
    return Part.makePolygon(pos, False)


positions: list = ak.zip([t.x, t.y, t.z]).to_list()

positions: list = list(map_objects(positions, tuple, FreeCAD.Vector))
# print(positions)

start = time.perf_counter()

wrapped_positions: list = list(map_last_level(positions, FreeCAD.Vector, ListWrapper))
result: list = list(map_objects(wrapped_positions, ListWrapper, make_polyline))

end = time.perf_counter()
ms = (end - start) * 10 ** 3
print(f"Elapsed: {ms:.03f} milliseconds.")
print("Data length:", len(result))

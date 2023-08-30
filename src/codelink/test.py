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

from utils import zip_nested


class Vector3DArray(ak.Array):
    def dot_prod(self, other):
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def cross_prod(self, other):
        return ak.Array({
           "x": self.y * other.z - self.z * other.y,
           "y": self.z * other.x - self.x * other.z,
           "z": self.x * other.y - self.y * other.x,
        })


ak.behavior["*", "vector3D"] = Vector3DArray

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

# print(one.layout)
# one[0].show()
# one[0][0].show()
# one["x"].show()

# one.dot_prod(two).show()

cross = one.cross_prod(two)
zip = ak.zip([cross["x"], cross["y"], cross["z"]])
cross.show()
zip.show()




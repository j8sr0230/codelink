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

from utils import zip_nested


a: ak.Array = ak.Array([[[10], [20]], [30], [40]])
b: ak.Array = ak.Array([5])
c: ak.Array = ak.Array([7])

print("a", a.to_list())
print("b", b.to_list())
print("c", c.to_list())

a_cast: ak.Array = ak.broadcast_arrays(a, b, c)[0]
b_cast: ak.Array = ak.broadcast_arrays(a, b, c)[1]
c_cast: ak.Array = ak.broadcast_arrays(a, b, c)[2]

print("a_casted", a_cast.to_list())
print("b_casted", b_cast.to_list())
print("c_casted", c_cast.to_list())

print("zip", zip_nested(a_cast.to_list(), b_cast.to_list(), c_cast.to_list()))

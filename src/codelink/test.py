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

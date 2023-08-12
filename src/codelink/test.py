import awkward as ak

from utils import simplify

a: ak.Array = ak.Array(simplify([[[[50.0]]], [[50.0]], [50.0]]))
b: ak.Array = ak.Array(simplify([0]))
c: ak.Array = ak.Array(simplify([0]))

print("a", a.to_list())
print("b", b.to_list())
print("c", c.to_list())

a_cast: ak.Array = ak.broadcast_arrays(a, b, c)[0]
b_cast: ak.Array = ak.broadcast_arrays(a, b, c)[1]
c_cast: ak.Array = ak.broadcast_arrays(a, b, c)[2]

print("a_cast", a_cast.to_list())
print("b_cast", b_cast.to_list())
print("c_cast", c_cast.to_list())

print("zip", ak.zip([a_cast, b_cast, c_cast]))

import awkward as ak

a: ak.Array = ak.Array([[[[50.0]]], [[50.0]], [50.0]])
b: ak.Array = ak.Array([0])
c: ak.Array = ak.Array([0])

a_cast: ak.Array = ak.broadcast_arrays(a, b, c)[0]
b_cast: ak.Array = ak.broadcast_arrays(a, b, c)[1]
c_cast: ak.Array = ak.broadcast_arrays(a, b, c)[2]

print(a_cast.to_list())
print(b_cast.to_list())
print(c_cast.to_list())

print(ak.zip([a_cast, b_cast, c_cast]))

import awkward as ak

from utils import flatten_array, unflatten_array_like

print("a")
a: ak.Array = ak.Array([[[1, 2, 9, 100]], [[3, 4]], [[5]]])
a.show()
print()

print("flat a")
flat_a: ak.Array = flatten_array(a)
flat_a.show()
print()

print("deep a")
deep_a: ak.Array = unflatten_array_like(flat_array=flat_a, template_array=a)
deep_a.show()

from typing import Any, Optional

import awkward as ak


class NestedData:
	def __init__(self, data: Optional[list[Any]] = None, structure: ak.Array = ak.Array([])):
		if data is None:
			data: list[Any] = []

		self._data: list[Any] = data
		self._structure: ak.Array = structure

	@property
	def data(self) -> list[Any]:
		return self._data

	@data.setter
	def data(self, value: list[Any]) -> None:
		self._data: list[Any] = value

	@property
	def structure(self) -> ak.Array:
		return self._structure

	@structure.setter
	def structure(self, value: ak.Array) -> None:
		self._structure: ak.Array = value

	def __str__(self) -> str:
		return "Data: " + str(self._data) + " / Structure: " + str(self._structure)


def nd_zip(*args):
	structure_dict: dict[Any] = {str(idx): item.structure for idx, item in enumerate(args)}
	structure_zip: ak.Array = ak.zip(structure_dict)
	structure_zip.show()

	flat_structure_lists: list[ak.Array] = [ak.flatten(structure_zip[key], axis=None) for key in structure_dict]
	flat_structure_tuples: list[tuple[int, int]] = ak.to_list(ak.zip(flat_structure_lists))

	for structure_tuple in flat_structure_tuples:
		print(
			[structure_zip[str(key)][index] for key, index in enumerate(structure_tuple)]
		)

	# (structure_zip[key][idx] for key, idx in enumerate(structure_tuple))


def main() -> None:
	a: NestedData = NestedData(
		data=[100, "Apple", {"x": 1, "y": 2, "z": 3}],
		structure=ak.Array([0, [1, 2]])
	)

	b: NestedData = NestedData(
		data=[200, "Test"],
		structure=ak.Array([0, 1])
	)

	print(a)
	print(b)
	print()

	res_structure: ak.Array = ak.zip({"a": a.structure, "b": b.structure})
	res_structure.show()
	print()

	a_flat: ak.Array = ak.flatten(res_structure.a, axis=None)
	b_flat: ak.Array = ak.flatten(res_structure.b, axis=None)

	res_flat: ak.Array = ak.zip([a_flat, b_flat])
	res_flat.show()
	print()

	params: list[tuple[Any, Any]] = [(a.data[ak.to_list(item)[0]], b.data[ak.to_list(item)[1]]) for item in res_flat]
	print(params)
	print()

	nd_zip(a, b)


if __name__ == "__main__":
	main()

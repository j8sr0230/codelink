from typing import Any, Union, Optional, cast

import awkward as ak
import numpy as np


# noinspection PyUnusedLocal
def global_index(layout: ak.contents.Content, **kwargs) -> ak.contents.Content:
	if layout.is_numpy:
		layout: np.ndarray = cast(np.ndarray, layout)
		# noinspection PyTypeChecker
		return ak.contents.NumpyArray(
			np.arange(0, layout.data.size)
		)


class NestedData:
	def __init__(self, data: Optional[list[Any]] = None, structure: Union[int, ak.Array] = ak.Array([])):
		if data is None:
			data: list[Any] = []

		self._data: list[Any] = data
		self._structure: Union[int, ak.Array] = structure

	@property
	def data(self) -> list[Any]:
		return self._data

	@data.setter
	def data(self, value: list[Any]) -> None:
		self._data: list[Any] = value

	@property
	def structure(self) -> Union[int, ak.Array]:
		return self._structure

	@structure.setter
	def structure(self, value: Union[int, ak.Array]) -> None:
		self._structure: Union[int, ak.Array] = value

	def __str__(self) -> str:
		return "Data: " + str(self._data) + " / Structure: " + str(self._structure)


class NestedVector:
	def __init__(self, vector: ak.Array = ak.Array([{"x": 0., "y": 0., "z": 0.}])):
		self._vector: ak.Array = vector
		self._structure: ak.Array = ak.transform(global_index, vector.x)

	@property
	def vector(self) -> ak.Array:
		return self._vector

	@vector.setter
	def vector(self, value: ak.Array) -> None:
		self._vector: ak.Array = value
		self._structure: ak.Array = ak.transform(global_index, self._vector.x)

	@property
	def structure(self) -> ak.Array:
		return self._structure

	def simplified(self, as_tuple: bool = False) -> tuple[Union[list[list[tuple]], ak.Array], Union[int, ak.Array]]:
		depth: int = self._vector.layout.minmax_depth[0]

		simplified_vector: ak.Array = ak.copy(self._vector)
		nesting_axes: np.ndarray = np.arange(1, depth - 1)
		for nesting_axis in nesting_axes[::-1]:
			simplified_vector: ak.Array = ak.flatten(simplified_vector, axis=nesting_axis)

		if as_tuple:
			simplified_vector: ak.Array = ak.zip([simplified_vector.x, simplified_vector.y, simplified_vector.z])
			simplified_vector: list[list[tuple]] = ak.to_list(simplified_vector)

		if depth > 1:
			simplified_structure: ak.Array = ak.transform(global_index, ak.max(self._structure, axis=-1))
		else:
			simplified_structure: int = 0

		return simplified_vector, simplified_structure

	def flat(self, as_tuple: bool = False) -> tuple[Union[list[tuple], ak.Array], Union[float, ak.Array]]:
		if not as_tuple:
			flat_vector: ak.Array = ak.zip({
				"x": ak.flatten(self._vector.x, axis=None),
				"y": ak.flatten(self._vector.y, axis=None),
				"z": ak.flatten(self._vector.z, axis=None)
			})
		else:
			flat_vector: ak.Array = ak.zip([
				ak.flatten(self._vector.x, axis=None),
				ak.flatten(self._vector.y, axis=None),
				ak.flatten(self._vector.z, axis=None)
			])

		return flat_vector, self._structure


def nd_zip(*args) -> tuple[list[list[Any, ...]], ak.Array]:
	structure_dict: dict[str, Any] = {str(idx): item.structure for idx, item in enumerate(args)}
	structure_zip: ak.Array = ak.zip(structure_dict)

	new_structure: ak.Array = structure_zip[structure_zip.fields[0]]

	flat_structure_lists: list[ak.Array] = [ak.flatten(structure_zip[key], axis=None) for key in structure_zip.fields]
	flat_structure_zip: ak.Array = ak.zip(flat_structure_lists)

	flat_param_list: list[list[Any, ...]] = [
		[args[key].data[index] for key, index in enumerate(structure_tuple)]
		for structure_tuple in flat_structure_zip.to_list()
	]

	return flat_param_list, new_structure


def main() -> None:

	a: ak.Array = ak.Array([
		[
			[{"x": 1, "y": 0, "z": 0}, {"x": 99, "y": 0, "z": 0}],
			[{"x": 0, "y": 1, "z": 0}],
			[{"x": 0, "y": 0, "z": 1}]
		]
	])

	# b: ak.Array = ak.Array([{"x": 1, "y": 0, "z": 0}, {"x": 2, "y": 0, "z": 0}])

	nv: NestedVector = NestedVector(a)

	print("Original")
	nv.vector.show()
	print()

	print("Simplified")
	print(nv.simplified()[0])
	print(ak.without_field(nv.simplified()[0]))
	print(nv.simplified()[1])
	print()

	print("Flat")
	print(nv.flat()[0])
	print(nv.flat()[1])
	print()


if __name__ == "__main__":
	main()

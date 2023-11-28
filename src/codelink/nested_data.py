from typing import Any, Optional, cast

import awkward as ak
import numpy as np


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


# noinspection PyUnusedLocal
def global_index(layout: ak.contents.Content, **kwargs) -> ak.contents.Content:
	if layout.is_numpy:
		layout: np.ndarray = cast(np.ndarray, layout)
		# noinspection PyTypeChecker
		return ak.contents.NumpyArray(
			np.arange(0, layout.data.size)
		)


class NestedVector:
	def __init__(self, vector: ak.Array = ak.Array([{"x": 0., "y": 0., "z": 0.}])):
		# Original nested vector
		self._original_vector: ak.Array = vector
		self._original_structure: ak.Array = ak.transform(global_index, vector.x)

		# Vector with preserved last nesting level
		self._simplified_vector: ak.Array = ak.copy(vector)
		depth: int = vector.layout.minmax_depth[0]
		reversed_nesting_axes: np.ndarray = np.arange(1, depth - 1)[::-1]
		for nesting_axis in reversed_nesting_axes:
			self._simplified_vector = ak.flatten(self._simplified_vector, axis=nesting_axis)
		self._simplified_structure: ak.Array = ak.firsts(self._original_structure, axis=-1)
		self._simplified_structure: ak.Array = ak.transform(global_index, self._simplified_structure.to_list())

		# Complete flat vector
		flat_x: ak.Array = ak.flatten(vector.x, axis=None)
		flat_y: ak.Array = ak.flatten(vector.y, axis=None)
		flat_z: ak.Array = ak.flatten(vector.z, axis=None)
		self.flat_vector: ak.Array = ak.zip({"x": flat_x, "y": flat_y, "z": flat_z})

		print("Original")
		self._original_vector.show()
		print()

		print("Simplified")
		self._simplified_vector.show()
		self._simplified_structure.show()
		print()

		print("Flat")
		self.flat_vector.show()
		self._original_structure.show()
		print()


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
	# start: NestedData = NestedData(
	# 	data=[0, 1, 2],
	# 	structure=ak.Array([0, [1, 2]])
	# )
	#
	# stop: NestedData = NestedData(
	# 	data=[5, 10],
	# 	structure=ak.Array([0, 1])
	# )
	#
	# step: NestedData = NestedData(
	# 	data=[1, 2],
	# 	structure=ak.Array([0, 1])
	# )
	#
	# flat_params, new_struct = nd_zip(start, stop, step)
	# new_data: list[np.ndarray] = list(map(lambda param: np.arange(param[0], param[1], param[2]), flat_params))
	# res: NestedData = NestedData(data=new_data, structure=new_struct)
	#
	# print(res)
	# res.structure.show()

	a: ak.Array = ak.Array([
		[
			[{"x": 1, "y": 0, "z": 0}, {"x": 99, "y": 0, "z": 0}],
			[{"x": 0, "y": 1, "z": 0}],
			[{"x": 0, "y": 0, "z": 1}]
		]
	])
	ne: NestedVector = NestedVector(a)


if __name__ == "__main__":
	main()

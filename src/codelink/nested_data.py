from typing import Union, cast

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
	def __init__(self, data: Union[ak.Array, list] = ak.Array([0]), structure: ak.Array = ak.Array([0])):
		self._original_data: Union[ak.Array, list] = data

		if type(data) is ak.Array and data.layout.minmax_depth[0] != 1:
			self._flat_data: ak.Array = ak.zip({
				"x": ak.flatten(data.x, axis=None),
				"y": ak.flatten(data.y, axis=None),
				"z": ak.flatten(data.z, axis=None)
			})
			self._data_structure: ak.Array = ak.transform(global_index, data.x)
		else:
			self._flat_data: Union[ak.Array, list] = data
			self._data_structure: Union[ak.Array, float] = structure

	@property
	def data(self) -> Union[ak.Array, list]:
		return self._flat_data

	@data.setter
	def data(self, value: Union[ak.Array, list]) -> None:
		self._flat_data: Union[ak.Array, list] = value

	@property
	def structure(self) -> ak.Array:
		return self._data_structure

	@structure.setter
	def structure(self, value: ak.Array) -> None:
		self._data_structure: ak.Array = value

	def data_keep_last(self) -> Union[ak.Array, list]:
		if type(self._flat_data) is ak.Array:
			# This works
			original_data: ak.Array = ak.zip({"x": self._data_structure, "y": self._data_structure, "z": self._data_structure})

			# This not
			original_data["x"] = self._flat_data.x
			original_data["y"] = self._flat_data.y
			original_data["z"] = self._flat_data.z

			if original_data.layout.minmax_depth[0] > 2:
				while original_data.layout.minmax_depth[0] > 2:
					original_data: ak.Array = ak.flatten(original_data, axis=1)

			return original_data

	def structure_keep_last(self) -> ak.Array:
		struct: Union[float, ak.Array] = ak.sum(self._data_structure)
		if type(struct) == ak.Array:
			struct: ak.Array = ak.transform(global_index, struct)
		return struct

	def __str__(self) -> str:
		return "Data: " + str(self._flat_data) + " / Structure: " + str(self._data_structure)

# def nd_zip(*args) -> tuple[list[list[Any, ...]], ak.Array]:
# 	structure_dict: dict[str, Any] = {str(idx): item.structure for idx, item in enumerate(args)}
# 	structure_zip: ak.Array = ak.zip(structure_dict)
#
# 	new_structure: ak.Array = structure_zip[structure_zip.fields[0]]
#
# 	flat_structure_lists: list[ak.Array] = [ak.flatten(structure_zip[key], axis=None) for key in structure_zip.fields]
# 	flat_structure_zip: ak.Array = ak.zip(flat_structure_lists)
#
# 	flat_param_list: list[list[Any, ...]] = [
# 		[args[key].data[index] for key, index in enumerate(structure_tuple)]
# 		for structure_tuple in flat_structure_zip.to_list()
# 	]
#
# 	return flat_param_list, new_structure
#
#
# def main() -> None:
# 	start: NestedData = NestedData(
# 		data=[0, 1, 2],
# 		structure=ak.Array([0, [1, 2]])
# 	)
#
# 	stop: NestedData = NestedData(
# 		data=[5, 10],
# 		structure=ak.Array([0, 1])
# 	)
#
# 	step: NestedData = NestedData(
# 		data=[1, 2],
# 		structure=ak.Array([0, 1])
# 	)
#
# 	flat_params, new_struct = nd_zip(start, stop, step)
# 	new_data: list[np.ndarray] = list(map(lambda param: np.arange(param[0], param[1], param[2]), flat_params))
# 	res: NestedData = NestedData(data=new_data, structure=new_struct)
#
# 	print(res)
# 	res.structure.show()
#
#
# if __name__ == "__main__":
# 	main()

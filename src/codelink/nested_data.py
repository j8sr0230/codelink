from typing import Any  # , Optional

import awkward as ak
# import numpy as np


class NestedData:
	def __init__(self, data: Any = None, structure: ak.Array = ak.Array([])):
		if data is None:
			data: list[Any] = []

		self._data: Any = data
		self._structure: ak.Array = structure

	# TODO: Maybe a keep_last_level view here?

	@property
	def data(self) -> Any:
		return self._data

	@data.setter
	def data(self, value: Any) -> None:
		self._data: Any = value

	@property
	def structure(self) -> ak.Array:
		return self._structure

	@structure.setter
	def structure(self, value: ak.Array) -> None:
		self._structure: ak.Array = value

	def __str__(self) -> str:
		return "Data: " + str(self._data) + " / Structure: " + str(self._structure)


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

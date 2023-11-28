from typing import Union

import awkward as ak
# import numpy as np


class NestedData:
	def __init__(self, data: Union[ak.Array, list] = None, structure: ak.Array = ak.Array([0])):
		if data is None:
			data: Union[ak.Array, list] = []

		self._data: Union[ak.Array, list] = data
		self._structure: Union[ak.Array, float] = structure

	@property
	def data(self) -> Union[ak.Array, list]:
		return self._data

	@data.setter
	def data(self, value: Union[ak.Array, list]) -> None:
		self._data: Union[ak.Array, list] = value

	@property
	def structure(self) -> ak.Array:
		return self._structure

	@structure.setter
	def structure(self, value: ak.Array) -> None:
		self._structure: ak.Array = value

	def data_keep_last(self) -> ak.Array:
		# TODO: Gets view with last level preserved
		pass

	def structure_keep_last(self) -> ak.Array:
		# TODO: Gets view with last level preserved
		pass

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

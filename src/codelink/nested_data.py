from typing import Any, Optional, Union

import awkward as ak
import numpy as np

from utils import global_index


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
			flat_vector: ak.Array = ak.to_list(ak.zip([
				ak.flatten(self._vector.x, axis=None),
				ak.flatten(self._vector.y, axis=None),
				ak.flatten(self._vector.z, axis=None)
			]))

		return flat_vector, self._structure

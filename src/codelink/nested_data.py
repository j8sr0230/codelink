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


def main() -> None:
	a: NestedData = NestedData(data=[100, "Apple", {"x": 1, "y": 2, "z": 3}], structure=ak.Array([1, [2, 3]]))
	print(a)


if __name__ == "__main__":
	main()

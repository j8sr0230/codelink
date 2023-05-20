from typing import Any, Optional

import PySide2.QtCore as QtCore


class PropertyModel(QtCore.QAbstractTableModel):
    def __init__(self, properties: Optional[dict] = None, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)

        if properties is None:
            properties: dict = {}

        self._properties = properties

    @property
    def properties(self) -> dict:
        return self._properties

    @properties.setter
    def properties(self, value: dict) -> None:
        self._properties: dict = value

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self._properties.keys())

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 2

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self._properties.keys()):
            return None

        if role == QtCore.Qt.DisplayRole:
            key: str = list(self._properties.keys())[index.row()]

            if index.column() == 0:
                return key
            else:
                return self._properties[key]

        return None

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole) -> Any:
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return "Property"
            elif section == 1:
                return "Value"

        return None

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.DisplayRole) -> bool:
        if role == QtCore.Qt.EditRole:
            key: str = list(self._properties.keys())[index.row()]
            data_type = type(self._properties[key])
            self._properties[key] = data_type(value)
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEnabled

        # if index.row() == 0:
        #     return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEnabled
        #
        # if index.column() == 0:
        #     return None
        if index.column() == 1 and index.row() > 0:
            return QtCore.Qt.ItemFlags(
                QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable
            )

    def __getstate__(self) -> dict:
        return self._properties

    def __setstate__(self, state: dict):
        self._properties: dict = state

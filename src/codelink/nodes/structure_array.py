from __future__ import annotations
from typing import Optional, cast

import awkward as ak

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem
from input_widgets import OptionBoxWidget
from socket_widget import SocketWidget


class StructureArray(NodeItem):
    REG_NAME: str = "Structure Array"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, parent)

        # Node name
        self._prop_model.properties["Name"] = "Structure Array"

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget()
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Flatten", "Graft"])
        item_list_view: QtWidgets.QListView = cast(QtWidgets.QListView, self._option_box.view())
        item_list_view.setSpacing(2)
        self._content_widget.hide()
        self._content_layout.addWidget(self._option_box)
        self._content_widget.show()

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            SocketWidget(undo_stack=self._undo_stack, label="A", is_input=True, parent_node=self),
            SocketWidget(undo_stack=self._undo_stack, label="A'", is_input=False, parent_node=self)
        ]
        for widget in self._socket_widgets:
            self._content_widget.hide()
            self._content_layout.addWidget(widget)
            self._content_widget.show()

        self.update_all()

        # Socket-wise node methods
        self._evals: list[object] = [self.eval_socket_1]

    # --------------- Node eval methods ---------------

    def eval_socket_1(self, *args) -> ak.Array:
        try:
            if self._option_box.currentText() == "Flatten":
                if ak.Array(args[0]).ndim > 1:
                    result: ak.Array = ak.flatten(args[0], axis=1)
                else:
                    result: ak.Array = ak.Array(args[0])
            else:
                result: ak.Array = ak.Array([[item] for item in args[0]])

            if result.ndim > 1:
                result: ak.Array = ak.flatten(result, axis=1)

            return result
        except ValueError as e:
            print(e)

# --------------- Serialization ---------------

    def __getstate__(self) -> dict:
        data_dict: dict = super().__getstate__()
        data_dict["Option Idx"] = self._option_box.currentIndex()
        return data_dict

    def __setstate__(self, state: dict):
        super().__setstate__(state)
        self._option_box.setCurrentIndex(state["Option Idx"])
        self.update()

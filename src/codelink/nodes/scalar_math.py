from __future__ import annotations
from typing import TYPE_CHECKING, Union, Optional, cast
import importlib

import awkward as ak

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from node_item import NodeItem
from input_widgets import OptionBoxWidget
from number_line import NumberLine
from socket_widget import SocketWidget

if TYPE_CHECKING:
    from pin_item import PinItem


class ScalarMath(NodeItem):
    REG_NAME: str = "Scalar Math"

    def __init__(self, pos: tuple, undo_stack: QtWidgets.QUndoStack,
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(pos, undo_stack, parent)

        # Node name
        self._prop_model.properties["Name"] = "Scalar Math"

        # Option combo box
        self._option_box: OptionBoxWidget = OptionBoxWidget()
        self._option_box.setFocusPolicy(QtCore.Qt.NoFocus)
        self._option_box.setMinimumWidth(5)
        self._option_box.addItems(["Add", "Sub", "Mul", "Div", "Sqrt"])
        item_list_view: QtWidgets.QListView = cast(QtWidgets.QListView, self._option_box.view())
        item_list_view.setSpacing(2)
        self._content_widget.hide()
        self._content_layout.addWidget(self._option_box)
        self._content_widget.show()

        # Socket widgets
        self._socket_widgets: list[SocketWidget] = [
            NumberLine(undo_stack=self._undo_stack, label="A", is_input=True, parent_node=self),
            SocketWidget(undo_stack=self._undo_stack, label="B", is_input=True, parent_node=self),
            SocketWidget(undo_stack=self._undo_stack, label="Res", is_input=False, parent_node=self)
        ]
        for widget in self._socket_widgets:
            self._content_widget.hide()
            self._content_layout.addWidget(widget)
            self._content_widget.show()

        self.update_all()

        # Socket-wise node methods
        self._evals: list[object] = [self.eval_socket_1]

        # Listeners
        cast(QtCore.SignalInstance, self._option_box.currentIndexChanged).connect(self.update_socket_widgets)

    def update_socket_widgets(self):
        # Hack to prevent cyclic imports
        add_socket_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "AddSocketCommand")
        remove_socket_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "RemoveSocketCommand")
        remove_edge_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "RemoveEdgeCommand")
        set_op_idx_cmd_cls: type = getattr(importlib.import_module("undo_commands"), "SetOptionIndexCommand")

        last_option_index: int = self._option_box.last_index
        current_option_name: str = self._option_box.currentText()
        current_option_index: int = self._option_box.currentIndex()
        input_widget_count: int = len(self.input_socket_widgets)

        if current_option_name == "Sqrt":
            self._undo_stack.beginMacro("Changes option box")
            self._undo_stack.push(
                set_op_idx_cmd_cls(self._option_box, last_option_index, current_option_index)
            )

            while input_widget_count > 1:
                remove_idx: int = len(self.input_socket_widgets) - 1
                remove_socket: SocketWidget = self._socket_widgets[remove_idx]
                for edge in remove_socket.pin.edges:
                    self._undo_stack.push(remove_edge_cmd_cls(self.scene(), edge))

                self._undo_stack.push(
                    remove_socket_cmd_cls(self, remove_idx)
                )
                # self.remove_socket_widget(remove_idx)
                input_widget_count -= 1

            self._undo_stack.endMacro()

        else:
            self._undo_stack.beginMacro("Changes option box")
            self._undo_stack.push(
                set_op_idx_cmd_cls(self._option_box, last_option_index, current_option_index)
            )

            while input_widget_count < 2:
                new_socket_widget: SocketWidget = SocketWidget(undo_stack=self._undo_stack, label="B", is_input=True,
                                                               parent_node=self)
                insert_idx: int = len(self.input_socket_widgets)
                self._undo_stack.push(
                    add_socket_cmd_cls(self, new_socket_widget, insert_idx)
                )
                # self.insert_socket_widget(new_socket_widget, insert_idx)
                input_widget_count += 1

            self._undo_stack.endMacro()

    # --------------- Node eval methods ---------------

    def eval_socket_1(self, *args) -> ak.Array:
        try:
            if self._option_box.currentText() == "Add" and len(args) == 2:
                return ak.Array(args[0]) + ak.Array(args[1])
            elif self._option_box.currentText() == "Sub" and len(args) == 2:
                return ak.Array(args[0]) - ak.Array(args[1])
            elif self._option_box.currentText() == "Mul" and len(args) == 2:
                return ak.Array(args[0]) * ak.Array(args[1])
            elif self._option_box.currentText() == "Div" and len(args) == 2:
                try:
                    return ak.Array(args[0]) / ak.Array(args[1])
                except ZeroDivisionError:
                    print("Division by zero")
                    return ak.Array([0])
            elif self._option_box.currentText() == "Sqrt" and len(args) == 1:
                return ak.Array(args[0]) ** 0.5
            else:
                return ak.Array([0])
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

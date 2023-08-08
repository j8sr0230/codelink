from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_model import PropertyModel
from input_widgets import NumberInputWidget
from pin_item import PinItem

if TYPE_CHECKING:
    from node_item import NodeItem


class SocketWidget(QtWidgets.QWidget):
    def __init__(self, undo_stack: QtWidgets.QUndoStack,
                 label: str = "In", is_input: bool = True, data: float = 0.0,
                 parent_node: Optional[NodeItem] = None,
                 parent_widget: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent_widget)

        # Persistent data model
        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "Name": label,
                        "Is Input": is_input,
                        "Data": data
                        },
            header_left="Socket Property",
            header_right="Value",
            undo_stack=undo_stack
        )
        self._link: tuple[str, int] = ("", -1)

        # Non persistent data model
        self._parent_node: Optional[NodeItem] = parent_node

        self._pin_item: PinItem = PinItem(
            pin_type=float,
            color=QtGui.QColor("#00D6A3"),
            socket_widget=self,
            parent_node=parent_node
        )

        # UI
        # Layout
        self._layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self._layout.setMargin(0)
        self._layout.setSpacing(0)
        self.setFixedHeight(24)
        self.setLayout(self._layout)

        # Label
        self._label_widget: QtWidgets.QLabel = QtWidgets.QLabel(self._prop_model.properties["Name"], self)
        self._layout.addWidget(self._label_widget)

        # Input widget
        self._input_widget: NumberInputWidget = NumberInputWidget(self)
        self._input_widget.setMinimumWidth(5)
        self._input_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self._input_widget.setText(str(self._prop_model.properties["Data"]))
        self._layout.addWidget(self._input_widget)
        self.setFocusProxy(self._input_widget)

        self.update_stylesheets()

        # Listeners
        cast(QtCore.SignalInstance,  self._prop_model.dataChanged).connect(lambda: self.update_all())
        cast(QtCore.SignalInstance, self._input_widget.editingFinished).connect(self.editing_finished)
        # cast(QtCore.SignalInstance, self._input_widget.returnPressed).connect(self.return_pressed)

    @property
    def prop_model(self) -> QtCore.QAbstractTableModel:
        return self._prop_model

    @property
    def link(self) -> tuple[str, int]:
        return self._link

    @link.setter
    def link(self, value: tuple[str, int]) -> None:
        self._link: tuple[str, int] = value

    @property
    def is_input(self) -> bool:
        return self._prop_model.properties["Is Input"]

    @property
    def parent_node(self) -> NodeItem:
        return self._parent_node

    @parent_node.setter
    def parent_node(self, value: NodeItem) -> None:
        self._parent_node: 'NodeItem' = value

    @property
    def pin(self) -> PinItem:
        return self._pin_item

    @property
    def input_widget(self) -> QtWidgets.QWidget:
        return self._input_widget

    # --------------- Socket data ---------------

    def input_data(self) -> Optional[Union[PinItem, int]]:
        result: Optional[Union[PinItem, int]] = None
        if self._pin_item.has_edges():
            pre_node: NodeItem = self._pin_item.edges[0].start_pin.parent_node
            if len(pre_node.sub_scene.nodes) > 0:
                result: PinItem = pre_node.linked_lowest_socket(self._pin_item.edges[0].start_pin.socket_widget).pin
            else:
                result: PinItem = self._pin_item.edges[0].start_pin

        else:
            linked_highest: SocketWidget = self.parent_node.linked_highest_socket(self)
            if linked_highest != self:
                result = linked_highest.input_data()

        if result is None:
            if self._input_widget.text() != "":
                result: float = float(self._input_widget.text())
            else:
                result: float = 0

        return result

    # --------------- Callbacks ---------------

    def update_stylesheets(self):
        if self._prop_model.properties["Is Input"]:
            self._label_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

            if self._pin_item.has_edges():
                self._label_widget.setStyleSheet("background-color: transparent")
                self._input_widget.hide()
            else:
                self._label_widget.setStyleSheet("background-color: #545454")
                self._input_widget.show()
        else:
            self._label_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self._label_widget.setStyleSheet("background-color: transparent")
            self._input_widget.hide()

    def update_pin_position(self) -> None:
        if not self._parent_node.is_collapsed:
            y_pos: float = (self._parent_node.content_y + self.y() + (self.height() - self._pin_item.size) / 2)

            if self._prop_model.properties["Is Input"]:
                self._pin_item.setPos(-self._pin_item.size / 2, y_pos)
            else:
                self._pin_item.setPos(self._parent_node.boundingRect().width() - self._pin_item.size / 2, y_pos)
            self._pin_item.show()

        else:
            y_pos: float = (self._parent_node.header_height - self._pin_item.size) / 2
            if self._prop_model.properties["Is Input"]:
                self._pin_item.setPos(-self._pin_item.size / 2, y_pos)
            else:
                self._pin_item.setPos(self._parent_node.boundingRect().width() - self._pin_item.size / 2, y_pos)
            self._pin_item.hide()

    def update_all(self):
        self._label_widget.setText(self._prop_model.properties["Name"])
        self._input_widget.setText(str(self._prop_model.properties["Data"]))
        self._input_widget.clearFocus()
        self.update_stylesheets()
        self.update_pin_position()

    def evaluate_input(self):
        last_value: float = self.prop_model.properties["Data"]
        input_txt: str = self._input_widget.text()

        try:
            input_number: float = float(input_txt)
            self._prop_model.setData(self._prop_model.index(2, 1, QtCore.QModelIndex()), input_number, 2)
        except ValueError:
            self._input_widget.setText(str(last_value))
            print("Wrong input format")

    def editing_finished(self) -> None:
        self.evaluate_input()
        self.clearFocus()

    def return_pressed(self) -> None:
        self.return_pressed()

    # --------------- Overwrites ---------------

    def focusNextPrevChild(self, forward: bool) -> bool:
        input_widget: QtWidgets.QLineEdit = cast(QtWidgets.QLineEdit, self.focusWidget())

        if input_widget == QtWidgets.QApplication.focusWidget():
            return False

        socket_idx: int = self.parent_node.input_socket_widgets.index(self)
        if forward:
            next_idx = socket_idx + 1
            if next_idx >= len(self.parent_node.input_socket_widgets):
                next_idx = 0
        else:
            next_idx = socket_idx - 1
            if next_idx < 0:
                next_idx = len(self.parent_node.input_socket_widgets) - 1

        self.parent_node.input_socket_widgets[next_idx].input_widget.setFocus(QtCore.Qt.TabFocusReason)

        return True

    # --------------- Serialization ---------------

    def __getstate__(self) -> dict:
        data_dict: dict = {
            "Class": self.__class__.__name__,
            "Properties": self._prop_model.__getstate__(),
            "Link": self._link
        }
        return data_dict

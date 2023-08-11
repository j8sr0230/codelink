from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_model import PropertyModel
from pin_item import PinItem

if TYPE_CHECKING:
    from node_item import NodeItem


class SocketWidget(QtWidgets.QWidget):
    def __init__(self, undo_stack: QtWidgets.QUndoStack,
                 label: str = "In", is_input: bool = True, data: Any = 0.0, parent_node: Optional[NodeItem] = None,
                 parent_widget: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent_widget)

        # Persistent data model
        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "Name": label,
                        "Is Input": is_input,
                        "Data": data,
                        "Flatten": False,
                        "Simplify": False,
                        "Graft": False,
                        "Graft Topo": False,
                        "Unwrap": False,
                        "Wrap": False
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
        self._label_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self._layout.addWidget(self._label_widget)

        # Input widget placeholder
        self._input_widget: QtWidgets.QLabel = QtWidgets.QLabel("", self)
        self._input_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self._layout.addWidget(self._input_widget)
        self._input_widget.hide()

        self.update_stylesheets()

        # QActions
        self._flatten_action: QtWidgets.QAction = QtWidgets.QAction("Flatten", self)
        self._flatten_action.setCheckable(True)
        self._flatten_action.setChecked(False)
        cast(QtCore.SignalInstance, self._flatten_action.triggered).connect(self.on_socket_action)

        self._simplify_action: QtWidgets.QAction = QtWidgets.QAction("Simplify", self)
        self._simplify_action.setCheckable(True)
        self._simplify_action.setChecked(False)
        cast(QtCore.SignalInstance, self._simplify_action.triggered).connect(self.on_socket_action)

        self._graft_action: QtWidgets.QAction = QtWidgets.QAction("Graft", self)
        self._graft_action.setCheckable(True)
        self._graft_action.setChecked(False)
        cast(QtCore.SignalInstance, self._graft_action.triggered).connect(self.on_socket_action)

        self._graft_topo_action: QtWidgets.QAction = QtWidgets.QAction("Graft Topo", self)
        self._graft_topo_action.setCheckable(True)
        self._graft_topo_action.setChecked(False)
        cast(QtCore.SignalInstance, self._graft_topo_action.triggered).connect(self.on_socket_action)

        self._unwrap_action: QtWidgets.QAction = QtWidgets.QAction("Unwrap", self)
        self._unwrap_action.setCheckable(True)
        self._unwrap_action.setChecked(False)
        cast(QtCore.SignalInstance, self._unwrap_action.triggered).connect(self.on_socket_action)

        self._wrap_action: QtWidgets.QAction = QtWidgets.QAction("Wrap", self)
        self._wrap_action.setCheckable(True)
        self._wrap_action.setChecked(False)
        cast(QtCore.SignalInstance, self._wrap_action.triggered).connect(self.on_socket_action)

        # Listeners
        cast(QtCore.SignalInstance, self._prop_model.dataChanged).connect(lambda: self.update_all())

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

    def input_data(self) -> list:
        result: list = []
        if self._pin_item.has_edges():
            for edge in self._pin_item.edges:
                pre_node: NodeItem = edge.start_pin.parent_node
                if len(pre_node.sub_scene.nodes) > 0:
                    result.append(pre_node.linked_lowest_socket(edge.start_pin.socket_widget).pin)
                else:
                    result.append(edge.start_pin)
        else:
            linked_highest: SocketWidget = self.parent_node.linked_highest_socket(self)
            if linked_highest != self:
                result.extend(linked_highest.input_data())

        if len(result) == 0:
            result.append(0.)

        return result

    def socket_actions(self) -> list[QtWidgets.QAction]:
        return [self._flatten_action, self._simplify_action, self._graft_action, self._graft_topo_action,
                self._unwrap_action,  self._wrap_action]

    # --------------- Callbacks ---------------

    def on_socket_action(self) -> None:
        sender: QtWidgets.QAction = self.sender()
        row: int = list(self._prop_model.properties.keys()).index(sender.text())
        self._prop_model.setData(
            self._prop_model.index(row, 1, QtCore.QModelIndex()), sender.isChecked(), 2
        )

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

    def update_stylesheets(self) -> None:
        if self._prop_model.properties["Is Input"]:
            self._label_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self._label_widget.setStyleSheet("background-color: transparent")
        else:
            self._label_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self._label_widget.setStyleSheet("background-color: transparent")

    def update_socket_actions(self) -> None:
        self._flatten_action.setChecked(bool(self._prop_model.properties["Flatten"]))
        self._simplify_action.setChecked(bool(self._prop_model.properties["Simplify"]))
        self._graft_action.setChecked(bool(self._prop_model.properties["Graft"]))
        self._graft_topo_action.setChecked(bool(self._prop_model.properties["Graft Topo"]))
        self._unwrap_action.setChecked(bool(self._prop_model.properties["Unwrap"]))
        self._wrap_action.setChecked(bool(self._prop_model.properties["Wrap"]))

    def update_all(self):
        self._label_widget.setText(self._prop_model.properties["Name"])
        self.update_pin_position()
        self.update_stylesheets()
        self.update_socket_actions()
        self.parent_node.update_details(self._parent_node.zoom_level)

    # --------------- Overwrites ---------------

    def focusNextPrevChild(self, forward: bool) -> bool:
        input_widget: QtWidgets.QWidget = self.focusWidget()

        if input_widget == QtWidgets.QApplication.focusWidget():
            return False

        socket_idx: int = self.parent_node.input_socket_widgets.index(input_widget.parent())
        next_idx: int = 0
        for idx in range(socket_idx + 1, len(self.parent_node.input_socket_widgets)):
            if self.parent_node.input_socket_widgets[idx].input_widget.focusPolicy() == QtCore.Qt.StrongFocus:
                next_idx: int = idx
                break

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

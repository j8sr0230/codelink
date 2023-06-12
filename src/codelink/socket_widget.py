from typing import Optional, Union

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_model import PropertyModel
from pin_item import PinItem


class SocketWidget(QtWidgets.QWidget):
    def __init__(self, label: str = "In", is_input: bool = True, data: object = 0,
                 parent_node: Optional['NodeItem'] = None, parent_widget: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent_widget)

        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "Class": self.__class__.__name__,
                        "Name": label,
                        "Is Input": is_input,
                        "Data": data
                        },
            header_left="Socket Property",
            header_right="Value"
        )

        self._parent_node: Optional['NodeItem'] = parent_node

        self._pin_item: PinItem = PinItem(
            pin_type=int,
            color=QtGui.QColor("#00D6A3"),
            socket_widget=self,
            parent_node=parent_node
        )

        self._layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self._layout.setMargin(0)
        self._layout.setSpacing(0)
        self.setFixedHeight(24)

        self.setLayout(self._layout)

        self._label_widget: QtWidgets.QLabel = QtWidgets.QLabel(self._prop_model.properties["Name"], self)
        self._layout.addWidget(self._label_widget)

        self._input_widget: QtWidgets.QWidget = QtWidgets.QLineEdit(self)
        self._input_widget.setMinimumWidth(5)
        # self._input_widget.setPlaceholderText("Enter value")
        self._input_widget.setText(str(self._prop_model.properties["Data"]))

        # noinspection PyTypeChecker
        self._input_widget.textChanged.connect(lambda: self._prop_model.setData(
            self._prop_model.index(3, 1, QtCore.QModelIndex()),
            int(self.input_widget.text()), QtCore.Qt.EditRole
        ))

        self._layout.addWidget(self._input_widget)

        self.update_stylesheets()

        # Listeners
        self._prop_model.dataChanged.connect(lambda: self.update_all())

    @property
    def prop_model(self) -> QtCore.QAbstractTableModel:
        return self._prop_model

    @property
    def is_input(self) -> bool:
        return self._prop_model.properties["Is Input"]

    @property
    def parent_node(self) -> 'NodeItem':
        return self._parent_node

    @parent_node.setter
    def parent_node(self, value: 'NodeItem') -> None:
        self._parent_node: 'NodeItem' = value

    @property
    def pin(self) -> PinItem:
        return self._pin_item

    @property
    def input_widget(self) -> QtWidgets.QWidget:
        return self._input_widget

    def input_data(self) -> Union['NodeItem', int]:
        if self._pin_item.has_edges():
            return self._pin_item.edges[0].start_pin  # .socket_widget
        else:
            if self._input_widget.text() != "":
                return int(self._input_widget.text())
            else:
                return 0

    # def input_data(self) -> Union['NodeItem', int]:
    #     result: list = []
    #
    #     # Process all connected edges
    #     for edge in self._pin_item.edges:
    #         if len(edge.start_pin.socket_widget.parent_node.sub_scene.nodes) == 0:
    #             # If edge end IS NOT a custom node socket, go along edge
    #             result.append(edge.start_pin.socket_widget.prop_model.properties["Name"])  # .socket_widget
    #         else:
    #             # If edge end IS a custom node socket, step into custom node
    #             custom_node: 'NodeItem' = edge.start_pin.socket_widget.parent_node
    #             custom_socket_key: str = str(custom_node.socket_widgets.index(edge.start_pin.socket_widget))
    #             inner_pin_map: dict = custom_node.pin_map
    #             inner_socket_idx: list[int] = inner_pin_map[custom_socket_key]
    #             inner_node: 'NodeItem' = custom_node.sub_scene.nodes[inner_socket_idx[0]]
    #             inner_socket: 'SocketWidget' = inner_node.socket_widgets[inner_socket_idx[1]]
    #             result.append(inner_socket.prop_model.properties["Name"])
    #
    #     # In addition to connected edges, check for inputs from upper level
    #     socket_idx: list[int] = [
    #         self.parent_node.scene().nodes.index(self.parent_node),
    #         self.parent_node.socket_widgets.index(self)
    #     ]
    #
    #     parent_custom: Optiona['NodeItem'] = self.parent_node.scene().parent_custom_node
    #     if parent_custom and socket_idx in list(parent_custom.pin_map.values()):
    #         # If node is in custom node (inner node), step out from inner node to custom node input
    #         parent_socket_idx: int = list(parent_custom.pin_map.values()).index(socket_idx)
    #         upper_level_socket_widget: 'SocketWidget' = parent_custom.socket_widgets[parent_socket_idx]
    #
    #         # TODO: Issues with compound in compound
    #         for edge in upper_level_socket_widget.pin.edges:
    #             result.append(edge.start_pin.socket_widget.prop_model.properties["Name"])
    #
    #     # If result still empty, grab data from input widget
    #     if len(result) == 0:
    #         if self._input_widget.text() != "":
    #             result.append(int(self._input_widget.text()))
    #         else:
    #             result.append(0)
    #
    #     return result

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
        self.update_stylesheets()
        self.update_pin_position()

    def __copy__(self) -> 'SocketWidget':
        copy: 'SocketWidget' = type(self)(
            label=self._prop_model.properties["Name"],
            is_input=self._prop_model.properties["Is Input"],
            data=self._prop_model.properties["Data"],
            parent_node=self._parent_node,
            parent_widget=self.parentWidget()
        )
        return copy

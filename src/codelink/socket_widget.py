from typing import Optional, Union

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_model import PropertyModel
from socket_item import SocketItem


class SocketWidget(QtWidgets.QWidget):
    def __init__(self, label: str = "In", socket_type: object = int, is_input: bool = True,
                 parent_node: Optional['NodeItem'] = None,
                 parent_widget: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent_widget)

        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "Class": self.__class__.__name__,
                        "Name": label,
                        "Is Input": is_input,
                        "Input": 0
                        },
            header_left="Socket Property",
            header_right="Value"
        )

        self._socket_type: object = socket_type
        self._parent_node: Optional['NodeItem'] = parent_node

        self._socket: SocketItem = SocketItem(
            color=QtGui.QColor("#00D6A3"),
            parent_node=parent_node, socket_widget=self
        )

        self._layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self._layout.setMargin(0)
        self._layout.setSpacing(0)
        self.setFixedHeight(24)

        self.setLayout(self._layout)

        self._label_widget: QtWidgets.QLabel = QtWidgets.QLabel(self._prop_model.properties["Name"], self)
        self._label_widget.setFont(self._parent_node.font)
        self._layout.addWidget(self._label_widget)

        self._input_widget: QtWidgets.QWidget = QtWidgets.QLineEdit(self)
        self._input_widget.setFont(self._parent_node.font)
        self._input_widget.setMinimumWidth(5)
        # self._input_widget.setPlaceholderText("Enter value")
        self._input_widget.setText(str(self._prop_model.properties["Input"]))

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
    def socket_type(self) -> object:
        return self._socket_type

    @property
    def is_input(self) -> bool:
        return self._prop_model.properties["Is Input"]

    @property
    def socket(self) -> SocketItem:
        return self._socket

    @property
    def input_widget(self) -> QtWidgets.QWidget:
        return self._input_widget

    def has_edges(self) -> bool:
        return self._socket.has_edges()

    def input_data(self) -> Union['NodeItem', int]:
        if self.has_edges():
            return self._socket.edges[0].start_socket.socket_widget
        else:
            if self._input_widget.text() != "":
                return int(self._input_widget.text())
            else:
                return 0

    def update_stylesheets(self):
        if self._prop_model.properties["Is Input"]:
            self._label_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

            if self._socket.has_edges():
                self._label_widget.setStyleSheet(
                    "color: #E5E5E5;"
                    "background-color: transparent;"
                    "min-height: 24px;"
                    "max-height: 24px;"
                    "margin: 0px;"
                    "padding-left: 10px;"
                    "padding-right: 0px;"
                    "padding-top: 0px;"
                    "padding-bottom: 0px;"
                    "border-radius: 0px;"
                    "border: 0px;"
                )
                self._input_widget.hide()
            else:
                self._label_widget.setStyleSheet(
                    "color: #E5E5E5;"
                    "background-color: #545454;"
                    "min-height: 24px;"
                    "max-height: 24px;"
                    "margin-left: 0px;"
                    "margin-right: 1px;"
                    "margin-top: 0px;"
                    "margin-bottom: 0px;"
                    "padding-left: 10px;"
                    "padding-right: 10px;"
                    "padding-top: 0px;"
                    "padding-bottom: 0px;"
                    "border-top-left-radius: 5px;"
                    "border-bottom-left-radius: 5px;"
                    "border-top-right-radius: 0px;"
                    "border-bottom-right-radius: 0px;"
                    "border: 0px;"
                )

                self._input_widget.setStyleSheet(
                    "color: #E5E5E5;"
                    "background-color: #545454;"
                    "selection-background-color: black;"
                    "min-width: 5px;"
                    "min-height: 24px;"
                    "max-height: 24px;"
                    "margin-left: 1px;"
                    "margin-right: 0px;"
                    "margin-top: 0px;"
                    "margin-bottom: 0px;"
                    "padding-left: 10px;"
                    "padding-right: 10px;"
                    "padding-top: 0px;"
                    "padding-bottom: 0px;"
                    "border-top-left-radius: 0px;"
                    "border-bottom-left-radius: 0px;"
                    "border-top-right-radius: 5px;"
                    "border-bottom-right-radius: 5px;"
                    "border: 0px;"
                )
                self._input_widget.show()
        else:
            self._label_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self._label_widget.setStyleSheet(
                "color: #E5E5E5;"
                "background-color: transparent;"
                "min-height: 24px;"
                "max-height: 24px;"
                "margin: 0px;"
                "padding-left: 0px;"
                "padding-right: 10px;"
                "padding-top: 0px;"
                "padding-bottom: 0px;"
                "border-radius: 0px;"
                "border: 0px;"
            )
            self._input_widget.hide()

    def update_socket_position(self) -> None:
        if not self._parent_node.is_collapsed:
            y_pos: float = (self._parent_node.content_y + self.y() + (self.height() - self._socket.size) / 2)

            if self._prop_model.properties["Is Input"]:
                self._socket.setPos(-self._socket.size / 2, y_pos)
            else:
                self._socket.setPos(self._parent_node.boundingRect().width() - self._socket.size / 2, y_pos)
            self._socket.show()

        else:
            y_pos: float = (self._parent_node.header_height - self._socket.size) / 2
            if self._prop_model.properties["Is Input"]:
                self._socket.setPos(-self._socket.size / 2, y_pos)
            else:
                self._socket.setPos(self._parent_node.boundingRect().width() - self._socket.size / 2, y_pos)
            self._socket.hide()

    def update_all(self):
        self._label_widget.setText(self._prop_model.properties["Name"])
        self._input_widget.setText(str(self._prop_model.properties["Input"]))
        self.update_stylesheets()
        self.update_socket_position()


class OutputSocketWidget(QtWidgets.QWidget):
    def __init__(self, label: str = "In", socket_type: object = int, parent_node: Optional['NodeItem'] = None,
                 parent_widget: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent_widget)

        self.is_input = False

        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "Class": self.__class__.__name__,
                        "Name": label,
                        },
            header_left="Output Property",
            header_right="Value"
        )

        self._socket_type: object = socket_type
        self._parent_node: Optional['NodeItem'] = parent_node

        self._socket: SocketItem = SocketItem(
            color=QtGui.QColor("#00D6A3"),
            parent_node=parent_node, socket_widget=self
        )

        self._layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self._layout.setMargin(0)
        self._layout.setSpacing(0)
        self.setFixedHeight(24)

        self.setLayout(self._layout)

        self._label_widget: QtWidgets.QLabel = QtWidgets.QLabel(self._prop_model.properties["Name"], self)
        self._label_widget.setFont(self._parent_node.font)
        self._label_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self._label_widget.setStyleSheet(
            "color: #E5E5E5;"
            "background-color: transparent;"
            "min-height: 24px;"
            "max-height: 24px;"
            "margin: 0px;"
            "padding-left: 0px;"
            "padding-right: 10px;"
            "padding-top: 0px;"
            "padding-bottom: 0px;"
            "border-radius: 0px;"
            "border: 0px;"
        )
        self._layout.addWidget(self._label_widget)

        # Listeners
        self._prop_model.dataChanged.connect(lambda: self.update_all())

    @property
    def prop_model(self) -> QtCore.QAbstractTableModel:
        return self._prop_model

    @property
    def socket_type(self) -> object:
        return self._socket_type

    @property
    def socket(self) -> SocketItem:
        return self._socket

    def has_edges(self) -> bool:
        return self._socket.has_edges()

    def update_stylesheets(self):
        pass

    def update_socket_position(self) -> None:
        if not self._parent_node.is_collapsed:
            y_pos: float = (self._parent_node.content_y + self.y() + (self.height() - self._socket.size) / 2)

            self._socket.setPos(self._parent_node.boundingRect().width() - self._socket.size / 2, y_pos)
            self._socket.show()

        else:
            y_pos: float = (self._parent_node.header_height - self._socket.size) / 2

            self._socket.setPos(self._parent_node.boundingRect().width() - self._socket.size / 2, y_pos)
            self._socket.hide()

    def update_all(self):
        self._label_widget.setText(self._prop_model.properties["Name"])
        self.update_socket_position()

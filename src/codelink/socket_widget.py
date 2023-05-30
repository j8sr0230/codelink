from typing import Optional, Union

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_model import PropertyModel
from pin_item import PinItem


class SocketWidget(QtWidgets.QWidget):
    def __init__(self, label: str = "In", is_input: bool = True, parent_node: Optional['NodeItem'] = None,
                 parent_widget: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent_widget)

        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "Class": self.__class__.__name__,
                        "Name": label,
                        "Is Input": is_input,
                        "Data": 0
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
    def pin(self) -> PinItem:
        return self._pin_item

    @property
    def input_widget(self) -> QtWidgets.QWidget:
        return self._input_widget

    def has_edges(self) -> bool:
        return self._pin_item.has_edges()

    def input_data(self) -> Union['NodeItem', int]:
        if self.has_edges():
            return self._pin_item.edges[0].start_pin.socket_widget
        else:
            if self._input_widget.text() != "":
                return int(self._input_widget.text())
            else:
                return 0

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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_model import PropertyModel

if TYPE_CHECKING:
    from node_item import NodeItem


class FrameItem(QtWidgets.QGraphicsItem):
    def __init__(self, framed_nodes: list[NodeItem], parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        # Persistent data model
        self._uuid: str = ""
        self._prop_model: PropertyModel = PropertyModel(
            properties={
                        "Name": "Frame Label",
                        "Color": "green"
                        }
        )

        # Reference to framed nodes
        self._framed_nodes: list[NodeItem] = framed_nodes
        for node in framed_nodes:
            node.parent_frame = self

        # Geometry
        self._offset: int = 10

        # Assets
        self._font_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._default_border_color: QtGui.QColor = QtGui.QColor("black")
        self._default_border_pen: QtGui.QPen = QtGui.QPen(self._default_border_color)
        self._selected_border_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._selected_border_pen: QtGui.QPen = QtGui.QPen(self._selected_border_color)
        self._selected_border_pen.setWidthF(1.5)

        # Hack for setting frame font to qss font defined in app_style.py -> NODE_STYLE -> QWidget
        self.framed_nodes[0].content_widget.style().unpolish(self.framed_nodes[0].content_widget)  # Unload qss
        self.framed_nodes[0].content_widget.style().polish(self.framed_nodes[0].content_widget)  # Reload qss
        self.framed_nodes[0].content_widget.update()
        self._font: QtGui.QFont = self.framed_nodes[0].content_widget.font()
        self._font.setPixelSize(self._font.pixelSize() + 4)

        # Widget setup
        self.setZValue(0)
        self.setAcceptHoverEvents(True)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsSelectable)

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str) -> None:
        self._uuid: str = value

    @property
    def prop_model(self) -> PropertyModel:
        return self._prop_model

    @property
    def framed_nodes(self) -> list[NodeItem]:
        return self._framed_nodes

    @framed_nodes.setter
    def framed_nodes(self, value: list[NodeItem]) -> None:
        self._framed_nodes: list[NodeItem] = value

    # --------------- Overwrites ---------------

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverEnterEvent(event)
        print("Frame UUID:", self._uuid)

    # --------------- Shape and painting ---------------

    def boundingRect(self) -> QtCore.QRectF:
        x_min: float = min([node.x() for node in self._framed_nodes]) - self._offset
        x_max: float = max([node.x() + node.boundingRect().width() for node in self._framed_nodes]) + self._offset
        y_min: float = min([node.y() for node in self._framed_nodes]) - self._offset
        y_max: float = max([node.y() + node.boundingRect().height() for node in self._framed_nodes]) + self._offset
        return QtCore.QRectF(x_min, y_min, x_max - x_min, y_max - y_min)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        if self.isSelected():
            painter.setPen(self._selected_border_pen)
        else:
            painter.setPen(self._default_border_pen)
        background_color: QtGui.QColor = QtGui.QColor(self._prop_model.properties["Color"])
        background_color.setAlpha(50)
        painter.setBrush(background_color)
        painter.drawRoundedRect(self.boundingRect(), 5, 5)

        painter.setPen(self._font_color)
        painter.setFont(self._font)
        painter.drawText(
            QtCore.QPointF(self.boundingRect().x() + 5, self.boundingRect().y() - 5),
            self._prop_model.properties["Name"]
        )

    # --------------- Serialization ---------------

    def __getstate__(self) -> dict:
        data_dict: dict = {
            "UUID": self._uuid,
            "Properties": self._prop_model.__getstate__(),
            "Framed Nodes UUID's": [node.uuid for node in self._framed_nodes],
        }
        return data_dict

    def __setstate__(self, state: dict):
        self._uuid = state["UUID"]
        self._prop_model.__setstate__(state["Properties"])
        self.update()

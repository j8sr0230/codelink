from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from property_model import PropertyModel


class FrameItem(QtWidgets.QGraphicsItem):
    def __init__(self, framed_nodes: list['NodeItem'], parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._prop_model: PropertyModel = PropertyModel(
            properties={"Class": self.__class__.__name__,
                        "Name": "Frame Label",
                        "Color": "green"
                        }
        )

        self._framed_nodes: list['NodeItem'] = framed_nodes

        self._offset: int = 10

        # Assets
        self._default_border_color: QtGui.QColor = QtGui.QColor("black")
        self._default_border_pen: QtGui.QPen = QtGui.QPen(self._default_border_color)

        self._selected_border_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._selected_border_pen: QtGui.QPen = QtGui.QPen(self._selected_border_color)
        self._selected_border_pen.setWidthF(1.5)

        self._font_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._font: QtGui.QFont = QtGui.QFont("Helvetica", 12)

        self.setZValue(0)

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsSelectable)

    @property
    def prop_model(self) -> QtCore.QAbstractTableModel:
        return self._prop_model

    @property
    def framed_nodes(self) -> list['NodeItem']:
        return self._framed_nodes

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

    def __getstate__(self) -> dict:
        data_dict: dict = {
            "Properties": self.prop_model.__getstate__(),
            "Framed Nodes": [self.scene().nodes.index(node) for node in self._framed_nodes]
        }
        return data_dict

    def __setstate__(self, state: dict):
        self.prop_model.__setstate__(state["Properties"])
        self.update()

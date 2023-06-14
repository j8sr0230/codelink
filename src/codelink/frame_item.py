from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from app_style import NODE_STYLE
from property_model import PropertyModel
from node_item import NodeItem


class FrameItem(QtWidgets.QGraphicsItem):
    def __init__(self, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._prop_model: PropertyModel = PropertyModel(
            properties={"Class": self.__class__.__name__,
                        "Name": "Frame Label",
                        "Color": "green"
                        }
        )

        # Assets
        self._default_border_color: QtGui.QColor = QtGui.QColor("black")
        self._font_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._default_border_pen: QtGui.QPen = QtGui.QPen(self._default_border_color)
        self._header_font: QtGui.QFont = QtGui.QFont()

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable)

    @property
    def prop_model(self) -> QtCore.QAbstractTableModel:
        return self._prop_model

    def boundingRect(self) -> QtCore.QRectF:
        return self.childrenBoundingRect()

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(self._default_border_pen)

        background_color: QtGui.QColor = QtGui.QColor(self._prop_model.properties["Color"])
        background_color.setAlpha(20)
        painter.setBrush(background_color)

        painter.drawRoundedRect(self.boundingRect(), 5, 5)

        painter.setPen(self._font_color)
        painter.setFont(QtGui.QFont("Helvetica", 12))
        painter.drawText(
            QtCore.QPointF(self.boundingRect().x() + 5, self.boundingRect().y() - 5),
            self._prop_model.properties["Name"]
        )

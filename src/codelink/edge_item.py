from typing import Any, Optional, Union, cast

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

from pin_item import PinItem


class EdgeItem(QtWidgets.QGraphicsPathItem):
    def __init__(self, color: QtGui.QColor = QtGui.QColor("#E5E5E5"),
                 parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        # Non persistent data model
        self._start_pin: Optional[Union[QtWidgets.QGraphicsItem, PinItem]] = None
        self._end_pin: Optional[Union[QtWidgets.QGraphicsItem, PinItem]] = None
        self._mode: str = ""

        # Assets
        self._default_color: QtGui.QColor = color
        self._selected_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._pen: QtGui.QPen = QtGui.QPen(self._default_color)
        self._pen.setWidthF(3.0)

        # Widget setup
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

    @property
    def color(self) -> QtGui.QColor:
        return self._default_color

    @color.setter
    def color(self, value: QtGui.QColor) -> None:
        self._default_color: QtGui.QColor = value

    @property
    def start_pin(self) -> QtWidgets.QGraphicsItem:
        return self._start_pin

    @start_pin.setter
    def start_pin(self, value: QtWidgets.QGraphicsItem) -> None:
        self._start_pin: QtWidgets.QGraphicsItem = value

    @property
    def end_pin(self) -> QtWidgets.QGraphicsItem:
        return self._end_pin

    @end_pin.setter
    def end_pin(self, value: QtWidgets.QGraphicsItem) -> None:
        self._end_pin: QtWidgets.QGraphicsItem = value

    def sort_pins(self) -> None:
        old_start_socket: PinItem = cast(PinItem, self._start_pin)

        if old_start_socket.socket_widget.is_input:
            self._start_pin: QtWidgets.QGraphicsItem = self._end_pin
            self._end_pin: QtWidgets.QGraphicsItem = old_start_socket

    # --------------- Edge validation ---------------

    def is_valid(self, eval_target: QtWidgets.QGraphicsItem) -> bool:
        result: bool = True

        if type(eval_target) == PinItem and type(self._start_pin) == PinItem and (eval_target != self._start_pin):
            self._start_pin: PinItem = cast(PinItem, self._start_pin)
            self._end_pin: PinItem = cast(PinItem, eval_target)
            self._end_pin.add_edge(self)

            socket_type_start: type = self._start_pin.pin_type
            socket_type_end: type = self._end_pin.pin_type

            if socket_type_start == socket_type_end:
                if self._start_pin.parentItem() is self._end_pin.parentItem():
                    # Sockets of the same node
                    result: bool = False

                elif self._start_pin.socket_widget.is_input and self._end_pin.socket_widget.is_input:
                    # Input with input pin
                    result: bool = False

                elif not self._start_pin.socket_widget.is_input and not self._end_pin.socket_widget.is_input:
                    # Output with output pin
                    result: bool = False

                elif self.scene().is_cyclic():
                    # Cyclic graph
                    result: bool = False

                # In any case, reset target to QtWidgets.QGraphicsEllipseItem
                self._end_pin.remove_edge(self)
                temp_target: QtWidgets.QGraphicsEllipseItem = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
                temp_target.setPos(self._end_pin.parent_node.mapToScene(self._end_pin.center()))
                self._end_pin = temp_target

            else:
                result: bool = False
        else:
            result: bool = False

        return result

    # --------------- Overwrites ---------------

    def scene(self) -> Any:
        return super().scene()

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverEnterEvent(event)
        self._mode: str = "HOVER"

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverLeaveEvent(event)
        self._mode: str = ""

    # --------------- Shape and painting ---------------

    def path(self) -> QtGui.QPainterPath:
        start_pin: PinItem = cast(PinItem, self._start_pin)
        start_point: QtCore.QPointF = self._start_pin.parentItem().mapToScene(start_pin.center())

        if type(self._end_pin) == PinItem:
            end_pin: PinItem = cast(PinItem, self._end_pin)
            end_point: QtCore.QPointF = self._end_pin.parentItem().mapToScene(end_pin.center())
        else:
            end_point: QtCore.QPointF = self._end_pin.pos()

        ctr_pt_offset: float = abs(end_point.x() - start_point.x()) / 2.5

        if not start_pin.socket_widget.is_input:
            ctr_pt_1: QtCore.QPointF = QtCore.QPointF(start_point.x() + ctr_pt_offset, start_point.y())
            ctr_pt_2: QtCore.QPointF = QtCore.QPointF(end_point.x() - ctr_pt_offset, end_point.y())
        else:
            ctr_pt_1: QtCore.QPointF = QtCore.QPointF(start_point.x() - ctr_pt_offset, start_point.y())
            ctr_pt_2: QtCore.QPointF = QtCore.QPointF(end_point.x() + ctr_pt_offset, end_point.y())

        path: QtGui.QPainterPath = QtGui.QPainterPath(start_point)
        path.cubicTo(ctr_pt_1, ctr_pt_2, end_point)

        return path

    def shape(self) -> QtGui.QPainterPath:
        return self.path()

    def boundingRect(self) -> QtCore.QRectF:
        return self.path().boundingRect()

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        if self.isSelected() or self._mode == "HOVER":
            self._pen.setColor(self._selected_color)
        else:
            self._pen.setColor(self._default_color)

        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(self._pen)
        painter.drawPath(self.path())

    # --------------- Serialization ---------------

    def __getstate__(self) -> dict:
        data_dict: dict = {
            "Start Node Idx": self.scene().nodes.index(self._start_pin.parentItem()),
            "Start Socket Idx": self._start_pin.parentItem().socket_widgets.index(
                cast(PinItem, self._start_pin).socket_widget
            ),
            "End Node Idx": self.scene().nodes.index(self._end_pin.parentItem()),
            "End Socket Idx": self._end_pin.parentItem().socket_widgets.index(

                cast(PinItem, self._end_pin).socket_widget
            )
        }
        return data_dict

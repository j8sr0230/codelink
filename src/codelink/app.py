import sys
import math
from typing import Optional

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class CLGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, scene: QtWidgets.QGraphicsScene = None, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(scene, parent)

        self._middle_mouse_pressed: bool = False
        self._last_view_pos: QtCore.QPoint = QtCore.QPoint()

        self._zoom: int = 10
        self._zoom_step: int = 1
        self._zoom_step_range: list = [1, 10]
        self._zoom_in_factor: float = 1.25

        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing |
                            QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)

        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MiddleButton:
            event.accept()

            self._middle_mouse_pressed: bool = True
            self._last_view_pos: QtCore.QPoint = event.pos()
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

            # Faking events for enabling dragging the scene with middle button
            left_btn_event = QtGui.QMouseEvent(event.type(), event.localPos(), QtCore.Qt.LeftButton,
                                               event.buttons() | QtCore.Qt.LeftButton, event.modifiers())
            super().mousePressEvent(left_btn_event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MiddleButton:
            event.accept()

            self._middle_mouse_pressed: bool = False
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

            # Faking events for disabling dragging the scene with middle button
            left_btn_event = QtGui.QMouseEvent(event.type(), event.localPos(), QtCore.Qt.LeftButton,
                                               event.buttons() | QtCore.Qt.LeftButton, event.modifiers())
            super().mouseReleaseEvent(left_btn_event)
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        event.accept()

        zoom_out_factor = 1 / self._zoom_in_factor
        if event.angleDelta().y() > 0:
            zoom_factor: float = self._zoom_in_factor
            self._zoom += self._zoom_step
        else:
            zoom_factor: float = zoom_out_factor
            self._zoom -= self._zoom_step

        _zoom_clamped: bool = False
        if self._zoom < self._zoom_step_range[0]:
            self._zoom = self._zoom_step_range[0]
            _zoom_clamped: bool = True
        if self._zoom > self._zoom_step_range[1]:
            self._zoom = self._zoom_step_range[1]
            _zoom_clamped: bool = True

        if not _zoom_clamped:
            self.scale(zoom_factor, zoom_factor)


class CLGraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent: Optional[QtCore.QObject] = None):
        super().__init__(QtCore.QRectF(0, 0, 64000, 64000), parent)

        self._major_grid_spacing = 20
        self._minor_grid_spacing = 5

        self._background_color_dark: QtGui.QColor = QtGui.QColor("#393939")
        self._background_color_medium: QtGui.QColor = QtGui.QColor("#292929")
        self._background_color_light: QtGui.QColor = QtGui.QColor("#2f2f2f")

        self._pen_light: QtGui.QPen = QtGui.QPen(self._background_color_light)
        self._pen_light.setWidth(1)
        self._pen_dark: QtGui.QPen = QtGui.QPen(self._background_color_medium)
        self._pen_dark.setWidth(2)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)

        self.setBackgroundBrush(self._background_color_dark)

        bound_box_left: int = int(math.floor(rect.left()))
        bound_box_right: int = int(math.ceil(rect.right()))
        bound_box_top: int = int(math.floor(rect.top()))
        bound_box_bottom: int = int(math.ceil(rect.bottom()))

        first_left: int = bound_box_left - (bound_box_left % self._major_grid_spacing)
        first_top: int = bound_box_top - (bound_box_top % self._major_grid_spacing)

        light_lines: list = []
        dark_lines: list = []
        for x in range(first_left, bound_box_right, self._major_grid_spacing):
            if x % (self._major_grid_spacing * self._minor_grid_spacing) != 0:
                light_lines.append(QtCore.QLine(x, bound_box_top, x, bound_box_bottom))
            else:
                dark_lines.append(QtCore.QLine(x, bound_box_top, x, bound_box_bottom))

        for y in range(first_top, bound_box_bottom, self._major_grid_spacing):
            if y % (self._major_grid_spacing * self._minor_grid_spacing) != 0:
                light_lines.append(QtCore.QLine(bound_box_left, y, bound_box_right, y))
            else:
                dark_lines.append(QtCore.QLine(bound_box_left, y, bound_box_right, y))

        painter.setPen(self._pen_light)
        painter.drawLines(light_lines)
        painter.setPen(self._pen_dark)
        painter.drawLines(dark_lines)


class MyGraphicsItem(QtWidgets.QGraphicsItem):
    def __init__(self, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:
        painter.setPen(QtCore.QColor("#000"))
        painter.drawEllipse(0, 0, 200, 100)


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # app.setStyle(QtWidgets.QStyleFactory().create("Fusion"))

    cl_graphics_scene: CLGraphicsScene = CLGraphicsScene()
    cl_graphics_view: CLGraphicsView = CLGraphicsView()

    cl_graphics_view.setScene(cl_graphics_scene)
    cl_graphics_view.resize(1200, 600)
    cl_graphics_view.show()

    item = QtWidgets.QGraphicsEllipseItem(0, 0, 200, 100)  # MyGraphicsItem()
    item.setPen(QtGui.QPen(QtGui.QColor("white")))
    print(item)
    cl_graphics_scene.addItem(item)
    item.show()

    sys.exit(app.exec_())

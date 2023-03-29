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
        self._last_scene_pos: QtCore.QPoint = QtCore.QPoint()

        self._zoom_level: int = 10
        self._zoom_level_range: list = [5, 10]

        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing |
                            QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)

        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)

        self._last_scene_pos: QtCore.QPoint = self.mapToScene(event.pos())

        if event.button() == QtCore.Qt.MiddleButton:
            self._middle_mouse_pressed: bool = True
            self.setCursor(QtCore.Qt.SizeAllCursor)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)

        if self._middle_mouse_pressed:
            current_pos: QtCore.QPoint = self.mapToScene(event.pos())
            pos_delta: QtCore.QPoint = current_pos - self._last_scene_pos
            self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
            self.translate(pos_delta.x(), pos_delta.y())
            self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
            self._last_scene_pos = self.mapToScene(event.pos())

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        if event.button() == QtCore.Qt.MiddleButton:
            self._middle_mouse_pressed: bool = False
            self.setCursor(QtCore.Qt.ArrowCursor)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        event.accept()

        self._last_scene_pos = self.mapToScene(event.pos())

        if event.angleDelta().y() > 0:
            if self._zoom_level < self._zoom_level_range[1]:
                self._zoom_level += 1
                self.scale(1.25, 1.25)
        else:
            if self._zoom_level > self._zoom_level_range[0]:
                self._zoom_level -= 1
                self.scale(1 / 1.25, 1 / 1.25)

        # Hack: Fixes the scene drifting while zooming
        drifted_pos: QtCore.QPoint = self.mapToScene(event.pos())
        pos_delta: QtCore.QPoint = drifted_pos - self._last_scene_pos
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.translate(pos_delta.x(), pos_delta.y())
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)


class CLGraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent: Optional[QtCore.QObject] = None):
        super().__init__(QtCore.QRectF(0, 0, 64000, 64000), parent)

        self._major_grid_spacing: int = 20
        self._minor_grid_spacing: int = 5

        self._background_color_dark: QtGui.QColor = QtGui.QColor("#393939")
        self._background_color_medium: QtGui.QColor = QtGui.QColor("#292929")
        self._background_color_light: QtGui.QColor = QtGui.QColor("#2f2f2f")

        self._pen_light: QtGui.QPen = QtGui.QPen(self._background_color_light)
        self._pen_light.setWidth(1)
        self._pen_dark: QtGui.QPen = QtGui.QPen(self._background_color_medium)
        self._pen_dark.setWidth(2)

        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)

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

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, 200, 100)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:
        painter.setPen(QtGui.QPen(QtGui.QColor("white")))
        painter.setBrush(QtGui.QColor("red"))
        painter.drawEllipse(self.boundingRect())


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

    my_item = MyGraphicsItem()
    cl_graphics_scene.addItem(my_item)
    my_item.setPos(QtCore.QPointF(32000, 32000))

    sys.exit(app.exec_())

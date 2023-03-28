import sys
import math

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


class CLGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, scene: QtWidgets.QGraphicsScene = None, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(scene, parent)

        self._middle_mouse_pressed: bool = False
        self._pan_start_x: float = 0.0
        self._pan_start_y: float = 0.0

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MiddleButton:
            self._middle_mouse_pressed: bool = True
            self._pan_start_x: float = event.x()
            self._pan_start_y: float = event.y()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            # self.middleMouseButtonPress(event)
            print("Drag", self._pan_start_x, self._pan_start_y)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MiddleButton:
            # self.middleMouseButtonRelease(event)
            self.setCursor(QtCore.Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class CLGraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent: QtCore.QObject = None):
        super().__init__(QtCore.QRectF(0, 0, 5000, 5000), parent)

        self._major_grid_spacing = 20
        self._minor_grid_spacing = 5

        self._background_color_dark: QtGui.QColor = QtGui.QColor("#393939")
        self._background_color_medium: QtGui.QColor = QtGui.QColor("#292929")
        self._background_color_light: QtGui.QColor = QtGui.QColor("#2f2f2f")

        self._pen_light: QtGui.QPen = QtGui.QPen(self._background_color_light)
        self._pen_light.setWidth(1)
        self._pen_dark: QtGui.QPen = QtGui.QPen(self._background_color_medium)
        self._pen_dark.setWidth(2)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        super().drawBackground(painter, rect)

        self.setBackgroundBrush(self._background_color_dark)

        bound_box_left: int = int(math.floor(rect.left()))
        bound_box_right: int = int(math.ceil(rect.right()))
        bound_box_top: int = int(math.floor(rect.top()))
        bound_box_bottom: int = int(math.ceil(rect.bottom()))

        first_left = bound_box_left - (bound_box_left % self._major_grid_spacing)
        first_top = bound_box_top - (bound_box_top % self._major_grid_spacing)

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


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    # app.setStyle(QtWidgets.QStyleFactory().create("Fusion"))

    cl_graphics_: CLGraphicsScene = CLGraphicsScene()
    cl_graphics_view: CLGraphicsView = CLGraphicsView()

    cl_graphics_view.setScene(cl_graphics_)
    cl_graphics_view.resize(1200, 400)
    cl_graphics_view.show()

    sys.exit(app.exec_())

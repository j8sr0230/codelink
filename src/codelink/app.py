import sys
import math
from typing import Optional, Any

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

        self.setStyleSheet("selection-background-color: black")

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

        self._major_grid_spacing: int = 50

        self._background_color_dark: QtGui.QColor = QtGui.QColor("#1D1D1D")
        self._background_color_light: QtGui.QColor = QtGui.QColor("#282828")

        self._pen_light: QtGui.QPen = QtGui.QPen(self._background_color_light)
        self._pen_light.setWidth(5)

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

        points: list = []
        for x in range(first_left, bound_box_right, self._major_grid_spacing):
            for y in range(first_top, bound_box_bottom, self._major_grid_spacing):
                points.append(QtCore.QPoint(x, y))

        painter.setPen(self._pen_light)
        painter.drawPoints(points)


class Socket(QtWidgets.QLabel):
    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__("   ", parent)
        self.setStyleSheet("color: white;")

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        super().paintEvent(event)

        painter: QtGui.QPainter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtGui.QColor("#E5E5E5")))
        painter.setBrush(QtGui.QColor("#00D6A3"))
        painter.drawEllipse(QtCore.QRectF(0, 0, self.width(), self.width()))


class MyGraphicsItem(QtWidgets.QGraphicsItem):
    def __init__(self, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self._mode: str = ""
        self._is_collapsed: bool = False

        self._title: str = "Curve"
        self._title_x: int = 20

        self._min_width: int = 80
        self._width: int = 160
        self._min_height: int = 25
        self._max_height: int = 80
        self._height: int = self._max_height
        self._header_height: int = 25
        self._corner_radius: int = 5
        self._content_padding: int = 10

        self._node_background_color: QtGui.QColor = QtGui.QColor("#303030")
        self._header_background_color: QtGui.QColor = QtGui.QColor("#1D1D1D")
        self._default_border_color: QtGui.QColor = QtGui.QColor("black")
        self._selected_border_color: QtGui.QColor = QtGui.QColor("#E5E5E5")
        self._default_font_color: QtGui.QColor = QtGui.QColor("#E5E5E5")

        self._default_font: QtGui.QFont = QtGui.QFont()  # QtGui.QFont("Sans Serif", 6)

        self._default_border_pen: QtGui.QPen = QtGui.QPen(self._default_border_color)
        self._selected_border_pen: QtGui.QPen = QtGui.QPen(self._selected_border_color)

        self._shadow: QtWidgets.QGraphicsDropShadowEffect = QtWidgets.QGraphicsDropShadowEffect()
        self._shadow.setColor(QtGui.QColor("black"))
        self._shadow.setBlurRadius(20)
        self._shadow.setOffset(1)
        self.setGraphicsEffect(self._shadow)

        self.setAcceptHoverEvents(True)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable |
                      QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

        self._collapse_item = QtWidgets.QGraphicsTextItem(self)
        self._collapse_item.setDefaultTextColor(self._default_font_color)
        self._collapse_item.setFont(self._default_font)
        self._collapse_item.setPlainText(">")
        collapse_item_x = (self._title_x - QtGui.QFontMetrics(self._default_font).horizontalAdvance(">")) / 2
        self._collapse_item.setPos(collapse_item_x,
                                   (self._header_height - self._collapse_item.boundingRect().height()) / 2)

        self._title_item = QtWidgets.QGraphicsTextItem(self)
        self._title_item.setDefaultTextColor(self._default_font_color)
        self._title_item.setFont(self._default_font)
        self._title_item.setPlainText(self.crop_text(self._title, self._width - 50, self._default_font))
        self._title_item.setPos(self._title_x,
                                (self._header_height - self._title_item.boundingRect().height()) / 2)

        self._content_widget: QtWidgets.QWidget = QtWidgets.QWidget()
        self._content_widget.setStyleSheet("background-color: transparent")
        self._content_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        self._content_layout.setMargin(0)
        self._content_layout.setSpacing(5)

        self._content_widget.setLayout(self._content_layout)

        # self._content_layout.addWidget(Socket(), 0, 0)
        # self._content_layout.addWidget(Socket(), 1, 0)
        # self._content_layout.addWidget(Socket(), 2, 2)

        self._line_edit_1: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self._line_edit_1.setPlaceholderText("Enter value")
        self._line_edit_1.setMinimumWidth(10)
        self._line_edit_1.setFont(self._default_font)
        self._line_edit_1.setStyleSheet("background-color: #545454; color: #E5E5E5; border: 0px; border-radius: 3px;")
        self._content_layout.addWidget(self._line_edit_1)

        self._line_edit_2: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self._line_edit_2.setPlaceholderText("Enter value")
        self._line_edit_2.setMinimumWidth(10)
        self._line_edit_2.setFont(self._default_font)
        self._line_edit_2.setStyleSheet("background-color: #545454; color: #E5E5E5; border: 0px; border-radius: 3px;")
        self._content_layout.addWidget(self._line_edit_2)

        self._line_edit_3: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self._line_edit_3.setPlaceholderText("Enter value")
        self._line_edit_3.setMinimumWidth(10)
        self._line_edit_3.setFont(self._default_font)
        self._line_edit_3.setStyleSheet("background-color: #545454; color: #E5E5E5; border: 0px; border-radius: 3px;")
        self._content_layout.addWidget(self._line_edit_3)

        self._content: QtWidgets.QGraphicsProxyWidget = QtWidgets.QGraphicsProxyWidget(self)
        self._content.setWidget(self._content_widget)
        self._content_rect: QtCore.QRectF = QtCore.QRectF(self._content_padding,
                                                          self._header_height + self._content_padding,
                                                          self._width - 2 * self._content_padding,
                                                          self._content_widget.height())
        self._content.setGeometry(self._content_rect)

        self._height = (self._header_height + self._content_padding + self._content_widget.height() +
                        self._content_padding)

    @staticmethod
    def crop_text(text: str = "Test", width: float = 30, font: QtGui.QFont = QtGui.QFont()) -> str:
        font_metrics: QtGui.QFontMetrics = QtGui.QFontMetrics(font)

        cropped_text: str = "..."
        string_idx: int = 0
        while font_metrics.horizontalAdvance(cropped_text) < width and string_idx < len(text):
            cropped_text = cropped_text[:string_idx] + text[string_idx] + cropped_text[string_idx:]
            string_idx += 1

        if string_idx == len(text):
            cropped_text: str = cropped_text[:len(text)]

        return cropped_text

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._width, self._height)

    def itemChange(self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            new_pos: QtCore.QPointF = value

            snapping_step: int = 10
            x_snap = new_pos.x() // snapping_step * snapping_step
            y_snap = new_pos.y() // snapping_step * snapping_step
            return QtCore.QPointF(x_snap, y_snap)
        else:
            return super().itemChange(change, value)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            if event.pos().x() > self.boundingRect().width() - 10:
                self._mode: str = "RESIZE"
                self.setCursor(QtCore.Qt.SizeHorCursor)

            collapse_item_left: float = self._collapse_item.x()
            collapse_item_right: float = self._collapse_item.x() + self._collapse_item.boundingRect().width()
            collapse_item_top: float = self._collapse_item.y()
            collapse_item_bottom: float = self._collapse_item.y() + self._collapse_item.boundingRect().height()

            if collapse_item_left <= event.pos().x() <= collapse_item_right:
                if collapse_item_top <= event.pos().y() <= collapse_item_bottom:
                    self._mode: str = "COLLAPSE"
                    if not self._is_collapsed:
                        self._collapse_item.setPlainText("<")
                        self._content.hide()
                        self._height = self._min_height
                    else:
                        self._collapse_item.setPlainText(">")
                        self._content.show()
                        self._height = (self._header_height + self._content_padding + self._content_widget.height() +
                                        self._content_padding)

                    self._is_collapsed = not self._is_collapsed

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self._mode == "RESIZE":
            old_x_left: float = self.boundingRect().x()
            old_y_top: float = self.boundingRect().y()

            old_top_left_local: QtCore.QPointF = QtCore.QPointF(old_x_left, old_y_top)
            old_top_left_global: QtCore.QPointF = self.mapToScene(old_top_left_local)

            current_x: int = self.mapToScene(event.pos()).x()
            new_width: float = current_x - old_top_left_global.x()
            if new_width < self._min_width:
                new_width: float = self._min_width

            self._width = new_width
            self._shadow.updateBoundingRect()
            self._title_item.setPlainText(self.crop_text(self._title, self._width - 50, self._default_font))
            self._content_rect: QtCore.QRectF = QtCore.QRectF(self._content_padding,
                                                              self._header_height + self._content_padding,
                                                              self._width - 2 * self._content_padding,
                                                              self._content_widget.height())
            self._content.setGeometry(self._content_rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self._mode = ""
        self.setCursor(QtCore.Qt.ArrowCursor)

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverMoveEvent(event)
        if event.pos().x() > self.boundingRect().width() - 10:
            self.setCursor(QtCore.Qt.SizeHorCursor)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        super().hoverLeaveEvent(event)
        self.setCursor(QtCore.Qt.ArrowCursor)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
              widget: Optional[QtWidgets.QWidget] = None) -> None:

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._node_background_color)
        painter.drawRoundedRect(self.boundingRect(), self._corner_radius, self._corner_radius)

        rect: QtCore.QRectF = QtCore.QRectF(0, 0, self._width, self._header_height)
        painter.setBrush(self._header_background_color)
        painter.drawRoundedRect(rect, self._corner_radius, self._corner_radius)

        painter.setBrush(QtCore.Qt.NoBrush)
        if self.isSelected():
            painter.setPen(self._selected_border_pen)
        else:
            painter.setPen(self._default_border_pen)
        painter.drawRoundedRect(self.boundingRect(), self._corner_radius, self._corner_radius)

        if not self._is_collapsed:
            pen_green: QtGui.QPen = QtGui.QPen(QtGui.QColor("green"))
            pen_green.setWidth(10)
            painter.setPen(pen_green)
            socket_pos_1: QtCore.QPointF = QtCore.QPointF(0, self._line_edit_1.y() + self._header_height +
                                                          self._content_padding + self._line_edit_1.height()/2)
            socket_pos_2: QtCore.QPointF = QtCore.QPointF(0, self._line_edit_2.y() + self._header_height +
                                                          self._content_padding + self._line_edit_1.height()/2)
            socket_pos_3: QtCore.QPointF = QtCore.QPointF(self._width, self._line_edit_3.y() + self._header_height +
                                                          self._content_padding + self._line_edit_1.height()/2)
            painter.drawPoints([socket_pos_1, socket_pos_2, socket_pos_3])


# class MyGraphicsWidget(QtWidgets.QGraphicsWidget):
#     def __init__(self, parent: Optional[QtWidgets.QGraphicsItem] = None,
#                  wFlags: QtCore.Qt.WindowFlags = QtCore.Qt.Window):
#         super().__init__(parent, wFlags)
#
#         self.setGeometry(QtCore.QRectF(0, 0, 200, 100))

    # def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
    #           widget: Optional[QtWidgets.QWidget] = None) -> None:
    #     super().paint(painter, option, widget)
    #     painter.setPen(QtGui.QPen(QtGui.QColor("red")))
    #     painter.drawRoundedRect(0, 0, 200, 100, 5, 5)

    # def paintWindowFrame(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem,
    #                      widget: Optional[QtWidgets.QWidget] = None) -> None:
    #     super().paintWindowFrame(painter, option, widget)
    #     painter.setPen(QtGui.QPen(QtGui.QColor("red")))
    #     painter.drawRoundedRect(20, 20, self.boundingRect().width() - 40, self.boundingRect().height() - 40, 5, 5)


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

    my_item_1 = MyGraphicsItem()
    cl_graphics_scene.addItem(my_item_1)
    my_item_1.setPos(QtCore.QPointF(31900, 32000))

    my_item_2 = MyGraphicsItem()
    cl_graphics_scene.addItem(my_item_2)
    my_item_2.setPos(QtCore.QPointF(32200, 32050))

    sys.exit(app.exec_())

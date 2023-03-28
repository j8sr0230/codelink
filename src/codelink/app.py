import sys

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory().create("Fusion"))
    view: QtWidgets.QWidget = QtWidgets.QWidget()
    view.resize(1200, 400)
    view.show()

    sys.exit(app.exec_())

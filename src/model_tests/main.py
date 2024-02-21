import sys

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets


node_item: QtGui.QStandardItem = QtGui.QStandardItem("Math")

class_key_item: QtGui.QStandardItem = QtGui.QStandardItem("Class")
class_value_item: QtGui.QStandardItem = QtGui.QStandardItem()
class_value_item.setData("nodes.util.scalar_functions.ScalarFunctions", int(QtCore.Qt.EditRole))
node_item.appendRow([class_key_item, class_value_item])

pos_key_item: QtGui.QStandardItem = QtGui.QStandardItem("Position")
pos_value_item: QtGui.QStandardItem = QtGui.QStandardItem()
pos_value_item.setData([0, 0], int(QtCore.Qt.EditRole))
pos_value_item.setData(str(pos_value_item.data(int(QtCore.Qt.EditRole))), int(QtCore.Qt.DisplayRole))
node_item.appendRow([pos_key_item, pos_value_item])

color_key_item: QtGui.QStandardItem = QtGui.QStandardItem("Color")
color_value_item: QtGui.QStandardItem = QtGui.QStandardItem()
color_value_item.setData("#1D1D1D", int(QtCore.Qt.EditRole))
node_item.appendRow([color_key_item, color_value_item])

input_a: QtGui.QStandardItem = QtGui.QStandardItem("A")
class_key_item: QtGui.QStandardItem = QtGui.QStandardItem("Class")
class_value_item: QtGui.QStandardItem = QtGui.QStandardItem()
class_value_item.setData("sockets.value_none.ValueNone", int(QtCore.Qt.EditRole))
input_a.appendRow([class_key_item, class_value_item])
widget_class_key_item: QtGui.QStandardItem = QtGui.QStandardItem("Widget class")
widget_class_value_item: QtGui.QStandardItem = QtGui.QStandardItem()
widget_class_value_item.setData("QLineEdit", int(QtCore.Qt.EditRole))
input_a.appendRow([widget_class_key_item, widget_class_value_item])

node_item.appendRow(input_a)


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)

    model: QtGui.QStandardItemModel = QtGui.QStandardItemModel()
    model.setColumnCount(2)
    model.setHorizontalHeaderLabels(["Key", "Value"])
    model.itemChanged.connect(lambda item: print(item.text()))

    root: QtGui.QStandardItem = model.invisibleRootItem()
    root.appendRow(node_item)

    view: QtWidgets.QTreeView = QtWidgets.QTreeView()
    view.setModel(model)
    view.setWindowTitle("Tree View")
    view.setAlternatingRowColors(True)
    view.show()

    sys.exit(app.exec_())

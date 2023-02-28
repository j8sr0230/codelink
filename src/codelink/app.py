from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtCore import Qt, QModelIndex


if __name__ == "__main__":
    model: QStandardItemModel = QStandardItemModel()
    parent_item: QStandardItem = model.invisibleRootItem()
    item: QStandardItem = QStandardItem("Hello World")
    parent_item.appendRow(item)

    for row in range(model.rowCount()):
        idx: QModelIndex = model.index(row, 0, QModelIndex())
        data: str = model.data(idx, 0)
        print(data)

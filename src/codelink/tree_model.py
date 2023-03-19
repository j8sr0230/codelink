import sys
import inspect

from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import QApplication, QTreeView
from PySide2.QtCore import Qt


class QNodeGraphItem(QStandardItem):

	def __init__(self, text: str = "Add", task: object = lambda a, b: a + b):
		super().__init__(text)

		self.task_label = QStandardItem("Task")
		self.predecessors_label = QStandardItem("Predecessors")
		self.successors_label = QStandardItem("Successors")
		self.value_label = QStandardItem("Value")
		self.appendRows([self.task_label, self.predecessors_label, self.successors_label, self.value_label])

		self.task = QStandardItem()
		self.task.setData(task, Qt.UserRole)
		self.task.setData(str(task), Qt.DisplayRole)
		self.predecessors = QStandardItem()
		self.predecessors.setData([1, 2, 3], Qt.UserRole)
		self.predecessors.setData("[1, 2, 3]", Qt.DisplayRole)
		self.successors = QStandardItem()
		self.successors.setData([], Qt.UserRole)
		self.successors.setData("[]", Qt.DisplayRole)
		self.value = QStandardItem()
		self.value.setData([0], Qt.UserRole)
		self.value.setData("[0]", Qt.DisplayRole)
		self.appendColumn([self.task, self.predecessors, self.successors, self.value])


class QNodeGraph(QStandardItemModel):
	def __init__(self):
		super().__init__()
		self.setHorizontalHeaderLabels(["Node/Property", "Value"])


if __name__ == "__main__":
	add_item = QNodeGraphItem(text="Add", task=lambda a, b: a + b)
	sub_item = QNodeGraphItem(text="Sub", task=lambda a, b: a - b)
	mul_item = QNodeGraphItem(text="Mul", task=lambda a, b: a * b)
	add_item_2 = QNodeGraphItem(text="Add", task=lambda a, b: a + b)

	print("Text:", add_item.text())
	print("Has children:", add_item.hasChildren())
	print(add_item.child(0, 0).data(Qt.DisplayRole), add_item.child(0, 1).data(Qt.UserRole)(1, 2))
	print(add_item.child(1, 0).data(Qt.DisplayRole), add_item.child(1, 1).data(Qt.UserRole))
	print(add_item.child(2, 0).data(Qt.DisplayRole), add_item.child(2, 1).data(Qt.UserRole))
	print(add_item.child(3, 0).data(Qt.DisplayRole), add_item.child(3, 1).data(Qt.UserRole))

	model: QStandardItemModel = QNodeGraph()
	root: QStandardItem = model.invisibleRootItem()
	root.appendRow(add_item)
	root.appendRow(sub_item)
	root.appendRow(mul_item)
	root.appendRow(add_item_2)

	app = QApplication(sys.argv)
	view = QTreeView()
	view.setModel(model)
	view.setAlternatingRowColors(True)
	view.show()
	sys.exit(app.exec_())

from PySide2.QtGui import QStandardItem
from PySide2.QtCore import Qt


class QNodeGraphItem(QStandardItem):

	def __init__(self, text: str = "Add", task: object = lambda a, b: a + b):
		super().__init__(text)

		self.task = QStandardItem()
		self.task.setData(task, Qt.DisplayRole)
		self.appendRow(self.task)

		self.predecessors = QStandardItem()
		self.predecessors.setData([1, 2, 3], Qt.DisplayRole)
		self.appendRow(self.predecessors)

		self.successor = QStandardItem()
		self.successor.setData([], Qt.DisplayRole)
		self.appendRow(self.successor)


if __name__ == "__main__":
	item = QNodeGraphItem(text="Add", task=lambda a, b: a + b)

	print("Text:", item.text())
	print("Has children:", item.hasChildren())
	print("Task:", item.child(0, 0).data(Qt.DisplayRole))
	print("Pre:", item.child(1, 0).data(Qt.DisplayRole))
	print("Suc:", item.child(2, 0).data(Qt.DisplayRole))

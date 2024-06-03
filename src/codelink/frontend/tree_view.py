import PySide2.QtWidgets as QtWidgets

from codelink.backend.delegates import TreeViewDelegate


class TreeView(QtWidgets.QTreeView):
    def __init__(self):
        super().__init__()

        self.setAlternatingRowColors(True)
        self.setItemDelegate(TreeViewDelegate())

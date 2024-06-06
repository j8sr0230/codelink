import PySide2.QtWidgets as QtWidgets

from codelink.frontend.delegates import TreeViewDelegate


class TreeView(QtWidgets.QTreeView):
    def __init__(self) -> None:
        super().__init__()

        self.setAlternatingRowColors(True)
        self.setItemDelegate(TreeViewDelegate())
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

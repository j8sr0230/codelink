from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex, QObject


class TableModel(QAbstractTableModel):

    def __init__(self, parent: QObject = None, nodes=None):
        super().__init__(parent)

        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes

    def rowCount(self, index: QModelIndex = QModelIndex()):
        return len(self.nodes)

    def columnCount(self, index: QModelIndex = QModelIndex()):
        return 2

    def data(self, index, role=Qt.DisplayRole):
        """ Depending on the index and role given, return data. If not
            returning data, return None (PySide equivalent of QT's
            "invalid QVariant").
        """
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.nodes):
            return None

        if role == Qt.DisplayRole:
            name = self.nodes[index.row()]["name"]
            address = self.nodes[index.row()]["address"]

            if index.column() == 0:
                return name
            elif index.column() == 1:
                return address

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return "Node"
            elif section == 1:
                return "Address"

        return None

    def insertRows(self, position, rows=1, index=QModelIndex()):
        """ Insert a row into the model. """
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.nodes.insert(position + row, {"name": "", "address": ""})

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        del self.nodes[position:position + rows]

        self.endRemoveRows()
        return True

    def setData(self, index, value, role=Qt.EditRole):
        """ Adjust the data (set it to <value>) depending on the given
            index and role.
        """
        if role != Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.nodes):
            address = self.nodes[index.row()]
            if index.column() == 0:
                address["name"] = value
            elif index.column() == 1:
                address["address"] = value
            else:
                return False

            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        """ Set the item flags at the given index. Seems like we're
            implementing this function just to see how it's done, as we
            manually adjust each tableView to have NoEditTriggers.
        """
        if not index.isValid():
            return Qt.ItemIsEnabled
        return super().flags(index) | Qt.ItemIsEditable

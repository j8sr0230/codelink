from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtCore import Qt, QModelIndex


if __name__ == "__main__":
    # Creates node graph model as QStandardItemModel and registers listeners
    node_graph: QStandardItemModel = QStandardItemModel()
    parent_node: QStandardItem = node_graph.invisibleRootItem()
    node_graph.rowsInserted.connect(lambda insert_event: print("Row inserted", insert_event))

    # Creates and inserts nodes as QStandardItems into the node graph
    node_a: QStandardItem = QStandardItem("Node A")
    node_a.setData({
        "Title": node_a.text(),
        "inputs": [1, 2, 3],
        "outputs": [4, 5, 6]
        })
    parent_node.appendRow(node_a)

    node_b: QStandardItem = QStandardItem("Node B")
    node_b.setData({
        "Title": node_b.text(),
        "inputs": [1, 2, 3],
        "outputs": [4, 5, 6]
    })
    parent_node.appendRow(node_b)

    # Loops over node graph rows and prints selected data
    for row in range(node_graph.rowCount()):
        node: QStandardItem = node_graph.item(row, 0)
        print(node.data())

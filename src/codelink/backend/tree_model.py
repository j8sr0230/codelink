#!/usr/bin/env python

# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2024 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

from __future__ import annotations
from typing import cast, Any, Optional
import importlib

import networkx as nx
import matplotlib.pyplot as plt

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

from codelink.backend.user_roles import UserRoles
from codelink.frontend.color_palette import ColorPalette
from codelink.backend.undo_cmds import BaseItemEditCommand, TreeItemInsertCommand, TreeItemRemoveCommand
from codelink.backend.tree_item import TreeItem
from codelink.backend.root_item import RootItem
from codelink.backend.base_item import BaseItem
from codelink.backend.node_item import NodeItem
from codelink.backend.seperator_item import SeperatorItem
from codelink.backend.inputs_seperator_item import InputsSeperatorItem
from codelink.backend.outputs_seperator_item import OutputsSeperatorItem
from codelink.backend.property_item import PropertyItem
from codelink.backend.edge_item import EdgeItem
from codelink.backend.edge_validator import EdgeValidator


class TreeModel(QtCore.QAbstractItemModel):
    begin_remove_rows: QtCore.Signal = QtCore.Signal(QtCore.QModelIndex, int, int)

    def __init__(self, data: Optional[dict[str, Any]] = None, undo_stack: Optional[QtWidgets.QUndoStack] = None,
                 parent: QtCore.QObject = None) -> None:
        super().__init__(parent)

        self._undo_stack: QtWidgets.QUndoStack = undo_stack if undo_stack else QtWidgets.QUndoStack()

        if data:
            self._root_item: RootItem = cast(RootItem, self.from_dict(data))
            self._nodes_index: QtCore.QModelIndex = self.index_from_key("Nodes")
            self._edges_index: QtCore.QModelIndex = self.index_from_key("Edges")
            self._frames_index: QtCore.QModelIndex = self.index_from_key("Frames")

        else:
            self._root_item: RootItem = RootItem()
            self._nodes_index: QtCore.QModelIndex = self.append_item(SeperatorItem("Nodes"), QtCore.QModelIndex())
            self._edges_index: QtCore.QModelIndex = self.append_item(SeperatorItem("Edges"), QtCore.QModelIndex())
            self._frames_index: QtCore.QModelIndex = self.append_item(SeperatorItem("Frames"), QtCore.QModelIndex())

        self._edge_validator: EdgeValidator = EdgeValidator(self)

    @property
    def root_item(self) -> RootItem:
        return self._root_item

    @root_item.setter
    def root_item(self, value: RootItem) -> None:
        self._root_item: RootItem = value

    @property
    def nodes_index(self) -> QtCore.QModelIndex:
        return self._nodes_index

    @property
    def edges_index(self) -> QtCore.QModelIndex:
        return self._edges_index

    @property
    def frames_index(self) -> QtCore.QModelIndex:
        return self._frames_index

    @property
    def undo_stack(self) -> QtWidgets.QUndoStack:
        return self._undo_stack

    @property
    def edge_validator(self) -> EdgeValidator:
        return self._edge_validator

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        parent_item: TreeItem = self.item_from_index(parent)
        if not parent_item:
            return QtCore.QModelIndex()

        child_item: Optional[TreeItem] = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)

        return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item: TreeItem = self.item_from_index(index)
        if child_item:
            parent_item: Optional[TreeItem] = child_item.parent
        else:
            parent_item: Optional[TreeItem] = None

        if parent_item == self.root_item or not parent_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        if parent.isValid() and parent.column() != 0:
            return 0

        parent_item: TreeItem = self.item_from_index(parent)
        if not parent_item:
            return 0

        return len(parent_item.children)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 2

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if (role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole and role != QtCore.Qt.BackgroundColorRole
                and role not in [role for role in UserRoles]):
            return None

        tree_item: TreeItem = self.item_from_index(index)

        if isinstance(tree_item, BaseItem):
            base_item: BaseItem = cast(BaseItem, tree_item)
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
                if index.column() == 0:
                    return base_item.key

                if index.column() == 1:
                    return base_item.value

            if role == UserRoles.KEY:
                return base_item.key

            if role == UserRoles.VALUE:
                return base_item.value

            if isinstance(tree_item, PropertyItem):
                prop_item: PropertyItem = cast(PropertyItem, tree_item)
                if role == UserRoles.COLOR:
                    return prop_item.color()

            if isinstance(tree_item, NodeItem):
                node_item: NodeItem = cast(NodeItem, tree_item)
                if role == UserRoles.POS:
                    return node_item.pos

        if type(tree_item) is EdgeItem:
            edge_item: EdgeItem = cast(EdgeItem, tree_item)
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:

                if index.column() == 0:
                    source: TreeItem = self.item_from_uuid(edge_item.source_uuid)
                    destination: TreeItem = self.item_from_uuid(edge_item.destination_uuid)
                    if hasattr(source, "key") and hasattr(destination, "key"):
                        return source.key + " -> " + destination.key

            if role == UserRoles.SRC:
                return edge_item.source_uuid

            if role == UserRoles.DEST:
                return edge_item.destination_uuid

        if isinstance(tree_item, SeperatorItem):
            if role == QtCore.Qt.BackgroundColorRole:
                return QtGui.QColor(ColorPalette.PALEGRAY)

        if role == UserRoles.TYPE:
            return type(tree_item)

        if role == UserRoles.UUID:
            return tree_item.uuid

    def hasChildren(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        return self.rowCount(parent) > 0

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.EditRole) -> bool:
        if role != QtCore.Qt.EditRole and role not in [role for role in UserRoles]:
            return False

        tree_item: TreeItem = self.item_from_index(index)

        if isinstance(tree_item, BaseItem):
            self._undo_stack.push(BaseItemEditCommand(index, value, role))
            return True

        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtCore.Qt.NoItemFlags | QtCore.Qt.NoItemFlags

        tree_item: Optional[TreeItem] = self.item_from_index(index)
        if isinstance(tree_item, BaseItem):
            if index.column() in (0, 1):
                return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole) -> Any:
        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                if role == QtCore.Qt.DisplayRole:
                    return "Key"
                if role == QtCore.Qt.ToolTipRole:
                    return "The name of the property"
            if section == 1:
                if role == QtCore.Qt.DisplayRole:
                    return "Value"
                if role == QtCore.Qt.ToolTipRole:
                    return "The value of the property"

    def removeRow(self, row: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        parent_item: TreeItem = self.item_from_index(parent)
        if not parent_item:
            return False

        child_item: Optional[TreeItem] = parent_item.child(row)
        if child_item:
            self._undo_stack.push(TreeItemRemoveCommand(self, parent, child_item, row))
            return True

        return False

    def insert_item(self, row: int, tree_item: TreeItem, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        parent_item: TreeItem = self.item_from_index(parent)

        if parent_item == self.root_item or not parent_item:
            parent_index: QtCore.QModelIndex = QtCore.QModelIndex()
        else:
            parent_index: QtCore.QModelIndex = parent

        if isinstance(tree_item, SeperatorItem):
            self.beginInsertRows(parent_index, row, row)
            parent_item.insert_child(row, tree_item)
            self.endInsertRows()
        else:
            self._undo_stack.push(TreeItemInsertCommand(self, parent_index, tree_item, row))

        return self.index(row, 0, parent_index)

    def append_item(self, tree_item: TreeItem, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        return self.insert_item(self.rowCount(parent), tree_item, parent)

    def append_node(self, node_item: NodeItem) -> QtCore.QModelIndex:
        node_item.setup_children()
        return self.append_item(node_item, self._nodes_index)

    def append_edge(self, source_uuid: str, destination_uuid: str) -> QtCore.QModelIndex:
        source_index: QtCore.QModelIndex = self.index_from_uuid(source_uuid)
        destination_index: QtCore.QModelIndex = self.index_from_uuid(destination_uuid)

        if self._edge_validator.can_connect(source_index, destination_index):

            if self.is_input(source_index) and self.is_output(destination_index):
                temp_uuid: str = destination_uuid
                destination_uuid: str = source_uuid
                source_uuid: str = temp_uuid

            edge_idx: QtCore.QModelIndex = self.append_item(EdgeItem(source_uuid, destination_uuid), self._edges_index)

            di_graph: nx.DiGraph = self.to_nx()
            nx.draw(
                di_graph, nx.spring_layout(di_graph, seed=225),
                labels={uuid: self.index_from_uuid(uuid).data() for uuid in di_graph.nodes()}
            )
            plt.show()

            return edge_idx

        else:
            return QtCore.QModelIndex()

    def index_from_uuid(
            self, uuid: str, parent: QtCore.QModelIndex = QtCore.QModelIndex()
    ) -> Optional[QtCore.QModelIndex]:
        index_list: list[int] = self.match(
            self.index(0, 0, parent), UserRoles.UUID, uuid, 1,
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive | QtCore.Qt.MatchWrap
        )
        if len(index_list) > 0:
            return cast(QtCore.QModelIndex, index_list[0])

        return None

    def index_from_key(
            self, key: str, parent: QtCore.QModelIndex = QtCore.QModelIndex()
    ) -> Optional[QtCore.QModelIndex]:
        index_list: list[int] = self.match(
            self.index(0, 0, parent), UserRoles.KEY, key, 1,
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive | QtCore.Qt.MatchWrap
        )
        if len(index_list) > 0:
            return cast(QtCore.QModelIndex, index_list[0])

        return None

    def item_from_index(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> TreeItem:
        if index.isValid():
            item: TreeItem = cast(TreeItem, index.internalPointer())
            if item:
                return item

        return self._root_item

    def item_from_uuid(self, uuid: str) -> Optional[TreeItem]:
        index: Optional[QtCore.QModelIndex] = self.index_from_uuid(uuid)
        if index:
            return self.item_from_index(index)

        return None

    def has_parent_recursively(self, index: QtCore.QModelIndex, parent: QtCore.QModelIndex) -> bool:
        if not index.isValid():
            return False

        if index.parent() == parent:
            return True

        return self.has_parent_recursively(index.parent(), parent)

    def is_input(self, index: QtCore.QModelIndex) -> bool:
        if self.data(index.parent(), UserRoles.TYPE) == InputsSeperatorItem:
            return True

        return False

    def is_output(self, index: QtCore.QModelIndex) -> bool:
        if self.data(index.parent(), UserRoles.TYPE) == OutputsSeperatorItem:
            return True

        return False

    def connected_edges(self, index: QtCore.QModelIndex) -> list[QtCore.QModelIndex]:
        uuid: str = index.data(UserRoles.UUID)

        src_list: list[int] = self.match(
            self.index(0, 0, self._edges_index), UserRoles.SRC, uuid, -1,
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive | QtCore.Qt.MatchWrap
        )

        dest_list: list[int] = self.match(
            self.index(0, 0, self._edges_index), UserRoles.DEST, uuid, -1,
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive | QtCore.Qt.MatchWrap
        )

        return cast(list[QtCore.QModelIndex], src_list + dest_list)

    def has_edge(self, source_uuid: str, destination_uuid: str) -> bool:
        for i in range(self.rowCount(self._edges_index)):
            edge_index: QtCore.QModelIndex = self.index(i, 0, self._edges_index)
            connected_uuids: list[str] = [edge_index.data(UserRoles.SRC), edge_index.data(UserRoles.DEST)]

            if source_uuid in connected_uuids and destination_uuid in connected_uuids:
                return True

        return False

    def edge_sibling(self, index: QtCore.QModelIndex, src_dest_index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        if index.data(UserRoles.TYPE) == EdgeItem:

            if self.data(index, UserRoles.SRC) == src_dest_index.data(UserRoles.UUID):
                return self.index_from_uuid(index.data(UserRoles.DEST))

            elif self.data(index, UserRoles.DEST) == src_dest_index.data(UserRoles.UUID):
                return self.index_from_uuid(index.data(UserRoles.SRC))

            else:
                return QtCore.QModelIndex()

        else:
            return QtCore.QModelIndex()

    def remove_index(self, index=QtCore.QModelIndex()) -> bool:
        if issubclass(index.data(UserRoles.TYPE), NodeItem):
            invalid_edges: list[QtCore.QPersistentModelIndex] = []

            for row in [1, 2]:
                sep_index: QtCore.QModelIndex = self.index(row, 0, index)
                for i in range(self.rowCount(sep_index)):
                    prop_index: QtCore.QModelIndex = self.index(i, 0, sep_index)
                    invalid_edges.extend(
                        [QtCore.QPersistentModelIndex(edge_idx) for edge_idx in self.connected_edges(prop_index)]
                    )

            for invalid_edge in invalid_edges:
                invalid_index: QtCore.QModelIndex = QtCore.QModelIndex(invalid_edge)
                self.remove_index(invalid_index)

        return self.removeRow(index.row(), index.parent())

    def open_ends(self) -> list[QtCore.QModelIndex]:
        ends: list[QtCore.QModelIndex] = []

        for i in range(self.rowCount(self._nodes_index)):
            pass

        return ends

    def to_nx(self) -> nx.DiGraph:
        di_graph: nx.DiGraph = nx.DiGraph()

        for edge_i in range(self.rowCount(self._edges_index)):
            edge_index: QtCore.QModelIndex = self.index(edge_i, 0, self._edges_index)

            source_index: QtCore.QModelIndex = self.index_from_uuid(edge_index.data(UserRoles.SRC))
            source_node_idx: QtCore.QModelIndex = source_index.parent().parent()

            destination_index: QtCore.QModelIndex = self.index_from_uuid(edge_index.data(UserRoles.DEST))
            destination_node_idx: QtCore.QModelIndex = destination_index.parent().parent()

            di_graph.add_edge(source_node_idx.data(UserRoles.UUID), destination_node_idx.data(UserRoles.UUID))

        return di_graph

    def to_dict(self, parent_index: QtCore.QModelIndex = QtCore.QModelIndex()) -> dict[str, Any]:
        parent_item: TreeItem = self.item_from_index(parent_index)
        state: dict[str, Any] = parent_item.__getstate__()

        if self.hasChildren(parent_index):
            child_states: list[dict[str, Any]] = []
            row_count: int = self.rowCount(parent_index)

            for row in range(row_count):
                child_index: QtCore.QModelIndex = self.index(row, 0, parent_index)
                child_states.append(self.to_dict(child_index))

            state["children"] = child_states

        return state

    def from_dict(self, state: dict[str, Any]) -> TreeItem:
        try:
            values: list[Any] = list(state.values())
            type_name: str = values.pop(0)

            if "children" in state.keys():
                values.pop()
            values.append(values.pop(0))

            class_name: str = type_name.split(".")[-1]
            module_name: str = type_name[:-len(class_name) - 1]
            tree_item: TreeItem = getattr(importlib.import_module(module_name), class_name)(*values)

            if "children" in state.keys():
                for child_data in state["children"]:
                    tree_item.append_child(self.from_dict(child_data))

            return tree_item

        except (IndexError, ValueError, AttributeError, Exception):
            root_item: RootItem = RootItem()
            root_item.append_child(SeperatorItem("Nodes"))
            root_item.append_child(SeperatorItem("Edges"))
            root_item.append_child(SeperatorItem("Frames"))
            return root_item

    def _repr_recursion(self, tree_item: TreeItem, indent: int = 0) -> str:
        result: str = " " * indent + repr(tree_item) + "\n"
        for child in tree_item.children:
            result += self._repr_recursion(child, indent + 4)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self.root_item)

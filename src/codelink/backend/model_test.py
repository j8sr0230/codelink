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

from typing import cast, Any
import json
from pathlib import Path

import PySide2.QtCore as QtCore

from codelink.backend.user_roles import UserRoles
from codelink.backend.node_factory import NodeFactory
from codelink.backend.tree_model import TreeModel
from codelink.backend.node_item import NodeItem
from codelink.backend.properties.integer_property_item import IntegerPropertyItem
from codelink.backend.edge_item import EdgeItem


if __name__ == "__main__":
    # Load nodes
    node_fac: NodeFactory = NodeFactory()
    node_fac.load_nodes(str(Path("nodes").resolve()))

    # Setup tree model
    model: TreeModel = TreeModel()
    model.rowsInserted.connect(
        lambda parent_idx, first_row_idx, last_row_idx: print("Inserted at:", first_row_idx)
    )
    model.rowsRemoved.connect(
        lambda parent_idx, first_row_idx, last_row_idx: print("Removed at:", first_row_idx)
    )
    model.dataChanged.connect(
        lambda top_left_idx, bottom_right_idx, roles: print(
            "Changed at:", top_left_idx.row(), top_left_idx.column(), "to:",
            top_left_idx.data(roles[0]) if len(roles) > 0 else None)
    )

    # Populate tree model with tree items
    node_item: NodeItem = node_fac.create_node(list(node_fac.nodes.keys())[0])
    node_item_idx: QtCore.QModelIndex = model.append_node(node_item)

    print(model.data(node_item_idx, UserRoles.POS))
    model.setData(node_item_idx, [5, 5], UserRoles.POS)
    print(model.data(node_item_idx, UserRoles.POS))

    print("Outputs index:", model.index_from_key("Outputs", node_item_idx))
    print()

    x_component: IntegerPropertyItem = IntegerPropertyItem(key="X", value=5)
    model.append_item(x_component, model.index(0, 0, node_item_idx))
    z_component: IntegerPropertyItem = IntegerPropertyItem(key="Z", value=99)
    model.append_item(z_component, model.index(0, 0, node_item_idx))
    y_component: IntegerPropertyItem = IntegerPropertyItem(key="Y", value=0)
    model.insert_item(1, y_component, model.index(0, 0, node_item_idx))

    edge: EdgeItem = EdgeItem(x_component.uuid, y_component.uuid)
    edge_idx: QtCore.QModelIndex = model.append_item(edge, model.edges_index)

    # (De-)Serialisation
    print(model)
    # with open("../frontend/data.json", "w", encoding="utf-8") as f:
    #     json.dump(model.to_dict(), f, ensure_ascii=False, indent=4)

    with open("../frontend/data.json", "r", encoding="utf-8") as f:
        deserialized: dict[str, Any] = json.load(f)
        restored_model: TreeModel = TreeModel(data=deserialized)
        print(restored_model)

        restored_nodes_idx: QtCore.QModelIndex = restored_model.index(0, 0, QtCore.QModelIndex())
        restored_node_1_idx: QtCore.QModelIndex = restored_model.index(0, 0, restored_nodes_idx)
        print(restored_node_1_idx.data(UserRoles.POS))

        restored_edges_idx: QtCore.QModelIndex = restored_model.index(1, 0, QtCore.QModelIndex())
        restored_edge_1_idx: QtCore.QModelIndex = restored_model.index(0, 0, restored_edges_idx)
        restored_source: IntegerPropertyItem = cast(
            IntegerPropertyItem, restored_model.data(restored_edge_1_idx, UserRoles.SRC)
        )
        restored_destination: IntegerPropertyItem = cast(
            IntegerPropertyItem, restored_model.data(restored_edge_1_idx, UserRoles.DEST)
        )
        print(
            restored_source.key, ":", restored_source.value, "->",
            restored_destination.key, ":", restored_destination.value
        )

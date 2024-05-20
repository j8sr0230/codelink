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

from typing import Any, Optional, Union, cast
import os
import sys
import importlib.util
import inspect

from codelink.backend.node_item import NodeItem


class NodeFactory:
    def __init__(self) -> None:
        self._nodes_structure: dict[str, Union[dict, str]] = {}
        self._nodes: dict[str, NodeItem] = {}

    @property
    def nodes_structure(self) -> dict[str, Union[dict, str]]:
        return self._nodes_structure

    @property
    def nodes(self) -> dict[str, NodeItem]:
        return self._nodes

    def _load_nodes(self, path: str, name_space: str, structure: dict[str, Union[dict, str]]) -> None:
        try:
            sub_dirs: list[str] = os.listdir(path)
            for sub_dir in sub_dirs:
                path: str = os.path.join(path, sub_dir)

                if not sub_dir.startswith("__"):
                    if os.path.isdir(path):
                        structure[sub_dir] = dict()
                        name_space: str = os.path.join(name_space, sub_dir)
                        self._load_nodes(path, name_space, structure[sub_dir])
                    else:
                        name_space: str = name_space.replace(os.sep, ".") + os.path.splitext(sub_dir)[0]
                        module_spec: Any = importlib.util.spec_from_file_location(name_space, path)
                        module: Any = importlib.util.module_from_spec(module_spec)
                        sys.modules[name_space] = module
                        module_spec.loader.exec_module(module)

                        for name, item in inspect.getmembers(module):
                            print(name)
                            # if inspect.isclass(item) and module.__name__ in str(item):
                            #     self._nodes[name] = cast(NodeItem, item)

        except FileNotFoundError as e:
            print(e)

    def load_nodes(self, nodes_path: str, name_space: str = "my_nodes") -> None:
        for root, dirs, files in os.walk(nodes_path):
            for name in files:
                if not name.startswith("__") and name.endswith(".py"):
                    module_path: str = os.path.join(root, name)
                    prefix_len: int = len(os.path.commonprefix([nodes_path, module_path]))
                    module_name: str = (name_space + module_path[prefix_len:-3]).replace(os.sep, ".")

                    module_spec: Any = importlib.util.spec_from_file_location(module_name, module_path)
                    module: Any = importlib.util.module_from_spec(module_spec)
                    sys.modules[module_name] = module
                    module_spec.loader.exec_module(module)

                    for item_name, item in inspect.getmembers(module):
                        if inspect.isclass(item) and module.__name__ in str(item):
                            self._nodes[module.__name__ + "." + item.__name__] = cast(NodeItem, item)

    def create_node(self, name: str) -> Optional[NodeItem]:
        print(sys.modules[name[:-1]])
        if name in self._node_classes.keys():
            return self._node_classes[name]()

    def reset(self) -> None:
        self._nodes_structure: dict[str, list] = {}
        self._node_classes: dict[str, type] = {}
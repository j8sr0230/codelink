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

from typing import Any, Optional
import os
import sys
import importlib.util
import inspect

from codelink.backend.node_item import NodeItem


class NodeFactory:
    def __init__(self) -> None:
        self._nodes_structure: dict[str, dict] = {}
        self._node_classes: dict[str, type] = {}

    @property
    def nodes_structure(self) -> dict[str, dict]:
        return self._nodes_structure

    @property
    def node_classes(self) -> dict[str, type]:
        return self._node_classes

    def _load_nodes(self, module_path: str, module_name_space: str, structure: dict[str, dict], classes: dict[str, type]) -> None:
        try:
            sub_dirs: list[str] = os.listdir(module_path)
            for sub_dir in sub_dirs:
                nodule_path: str = os.path.join(module_path, sub_dir)

                if not sub_dir.startswith("__"):
                    if os.path.isdir(nodule_path):
                        sub: str = sub_dir.replace("_", " ").title()
                        structure[sub] = dict()
                        module_name_space: str = os.path.join(module_name_space, sub_dir)
                        self._load_nodes(nodule_path, module_name_space, structure[sub], classes)
                    else:
                        module_name_space: str = module_name_space.replace(os.sep, ".") + "." + os.path.splitext(sub_dir)[0]
                        module_spec: Any = importlib.util.spec_from_file_location(module_name_space, nodule_path)
                        module: Any = importlib.util.module_from_spec(module_spec)

                        sys.modules[module_name_space] = module
                        module_spec.loader.exec_module(module)

                        for name, item in inspect.getmembers(module):
                            if inspect.isclass(item) and module.__name__ in str(item):
                                structure[module_name_space + "." + name] = dict()
                                classes[module_name_space + "." + name] = item

        except FileNotFoundError as e:
            print(e)

    def load_nodes(self, path: str) -> None:
        self._load_nodes(path, "my_nodes", self._nodes_structure, self._node_classes)

    def create_node(self, name: str) -> Optional[NodeItem]:
        if name in self._node_classes.keys():
            return self._node_classes[name]()

    def reset(self) -> None:
        self._nodes_structure: dict[str, list] = {}
        self._node_classes: dict[str, type] = {}
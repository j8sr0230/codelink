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

from typing import Any
import os
import sys
import importlib.util
import inspect


class NodeFactory:
    def __init__(self) -> None:
        self._nodes_structure: dict[str, Any] = {"Nodes": []}
        self._nodes_map: dict[str, type] = {}

    @property
    def nodes_structure(self) -> dict[str, Any]:
        return self._nodes_structure

    @property
    def nodes_map(self) -> dict[str, type]:
        return self._nodes_map

    def _load_nodes(self, path: str, nodes_structure: dict, nodes_modules: dict) -> None:
        try:
            sub_dirs: list[str] = os.listdir(path)
            for sub_dir in sub_dirs:
                sub_path: str = os.path.join(path, sub_dir)
                path_items: list[str] = sub_path.split(os.sep)

                if len(path_items) > 0 and not path_items[-1].startswith("__"):
                    last_key: str = list(nodes_structure.keys())[-1]
                    if os.path.isdir(sub_path):
                        sub_menu: str = path_items[-1].replace("_", " ").title()
                        nodes_structure[last_key].append({sub_menu: []})
                        self._load_nodes(sub_path, nodes_structure[last_key][-1], nodes_modules)
                    else:
                        module_name: str = os.path.splitext(path_items[-1])[0]
                        module_spec: Any = importlib.util.spec_from_file_location(module_name, sub_path)
                        module: Any = importlib.util.module_from_spec(module_spec)
                        sys.modules[module_name] = module
                        module_spec.loader.exec_module(module)

                        for name, item in inspect.getmembers(module):
                            if inspect.isclass(item):
                                if str(item).__contains__(module.__name__):
                                    nodes_modules[name] = item
                                    nodes_structure[last_key].append(name)
        except FileNotFoundError as e:
            print(e)

    def load_nodes(self, path: str) -> None:
        self._load_nodes(path, self._nodes_structure, self._nodes_map)
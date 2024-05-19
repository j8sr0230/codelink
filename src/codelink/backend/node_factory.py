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
        self._structure: dict[str, dict] = {}
        self._modules: dict[str, type] = {}

    @property
    def structure(self) -> dict[str, dict]:
        return self._structure

    @property
    def modules(self) -> dict[str, type]:
        return self._modules

    def _load_nodes(self, path: str, structure: dict[str, dict], modules: dict[str, type]) -> None:
        try:
            sub_dirs: list[str] = os.listdir(path)
            for sub_dir in sub_dirs:
                sub_path: str = os.path.join(path, sub_dir)

                if not sub_dir.startswith("__"):
                    if os.path.isdir(sub_path):
                        sub: str = sub_dir.replace("_", " ").title()
                        structure[sub] = dict()
                        self._load_nodes(sub_path, structure[sub], modules)
                    else:
                        module_name: str = os.path.splitext(sub_dir)[0]
                        module_spec: Any = importlib.util.spec_from_file_location(module_name, sub_path)
                        module: Any = importlib.util.module_from_spec(module_spec)
                        sys.modules[module_name] = module
                        module_spec.loader.exec_module(module)

                        for name, item in inspect.getmembers(module):
                            if inspect.isclass(item) and module.__name__ in str(item):
                                structure[name] = dict()
                                modules[name] = item

        except FileNotFoundError as e:
            print(e)

    def load_nodes(self, path: str) -> None:
        self._load_nodes(path, self._structure, self._modules)

    def create_node(self, name: str) -> Optional[NodeItem]:
        if name in self._modules.keys():
            return self._modules[name]()

    def reset(self) -> None:
        self._structure: dict[str, list] = {}
        self._modules: dict[str, type] = {}
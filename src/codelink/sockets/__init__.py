# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2023 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
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
from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module

from socket_widget import SocketWidget

package_dir: str = str(Path(__file__).resolve().parent)
for (_, module_name, _) in iter_modules([package_dir]):
    # Iterates through the modules in the current package

    module: Any = import_module(f"{__name__}.{module_name}")  # Imports the module and ...
    for attribute_name in dir(module):

        # ... iterate through its attributes
        attribute: Any = getattr(module, attribute_name)

        if isclass(attribute) and issubclass(attribute, SocketWidget) and attribute is not SocketWidget:
            # Adds class to the global namespace
            globals()[attribute_name] = attribute
            # print("Registered sockets:", attribute)

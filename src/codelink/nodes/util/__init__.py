from typing import Any
import os
from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module

from node_reg import register_node
from node_item import NodeItem

package_dir: str = str(Path(__file__).resolve().parent)
for (_, module_name, _) in iter_modules([package_dir]):
    # Iterates through the modules in the current package

    module: Any = import_module(f"{__name__}.{module_name}")  # Imports the module and ...
    # print("Registered packages:", module)
    for attribute_name in dir(module):

        # ... iterate through its attributes
        attribute: Any = getattr(module, attribute_name)

        if isclass(attribute) and issubclass(attribute, NodeItem) and attribute is not NodeItem:
            # Adds class to the global namespace
            globals()[attribute_name] = attribute
            category_name: str = os.path.basename(os.path.normpath(package_dir)).capitalize().replace("_", " ")
            register_node(category_name, attribute.REG_NAME, attribute)
            # print("Registered nodes:", attribute)

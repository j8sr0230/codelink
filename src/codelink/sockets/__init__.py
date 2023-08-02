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
            print("Registered sockets:", attribute)
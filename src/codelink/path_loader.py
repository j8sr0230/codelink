import sys
import os
from pathlib import Path


main_path: str = str(Path(__file__).parent)
nodes_path: str = os.path.join(str(Path(__file__).parent), "nodes")
sockets_path: str = os.path.join(str(Path(__file__).parent), "sockets")

app_paths: list[str] = [main_path, nodes_path, sockets_path]
for path in app_paths:
    if path not in sys.path:
        sys.path.append(path)

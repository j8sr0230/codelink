from .scalar_math import ScalarMath

nodes_dict: dict[str, type] = {
    "Scalar Math": ScalarMath
}


def add_node(name: str, cls: type):
    nodes_dict[name] = cls

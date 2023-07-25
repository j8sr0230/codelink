nodes_dict: dict[str, type] = {

}


def register_node(node_name: str, node_cls: type):
    nodes_dict[node_name] = node_cls

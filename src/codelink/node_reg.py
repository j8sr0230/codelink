nodes_dict: dict[str, dict[str, type]] = {

}


def register_node(category_name: str, node_name: str, node_cls: type):
    if category_name in nodes_dict.keys():
        category_dict: dict[str, type] = nodes_dict[category_name]
    else:
        category_dict: dict[str, type] = {}

    category_dict[node_name] = node_cls
    nodes_dict[category_name] = category_dict

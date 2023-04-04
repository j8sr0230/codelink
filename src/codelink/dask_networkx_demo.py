import time

import networkx as nx
from dask.threaded import get
import matplotlib.pyplot as plt


class DefaultTask:
    pass


class InputTask(DefaultTask):
    def __init__(self, a: int = 0):
        self.a = a

    def eval(self) -> int:
        return self.a


class AddTask(DefaultTask):
    @staticmethod
    def eval(a: int = 0, b: int = 0) -> int:
        return a + b


class PowerTask(DefaultTask):
    @staticmethod
    def eval(a: int = 0, b: int = 0) -> int:
        return a ** b


def networkx_to_dask(in_graph: nx.DiGraph, out_graph: dict, target_task: DefaultTask) -> None:
    for predecessor in in_graph.predecessors(target_task):
        networkx_to_dask(in_graph, out_graph, predecessor)

    out_graph[target_task] = (target_task.eval, *in_graph.predecessors(target_task))


# Generate some tasks
t1: DefaultTask = InputTask(1)
t2: DefaultTask = InputTask(9)
t3: DefaultTask = AddTask()
t4: DefaultTask = AddTask()
t5: DefaultTask = PowerTask()

# Build dependency in_graph
G = nx.DiGraph()
G.add_node(t1)
G.add_node(t2)
G.add_node(t3)
G.add_node(t4)
G.add_node(t5)

G.add_edge(t1, t3)
G.add_edge(t2, t3)
G.add_edge(t3, t4)
G.add_edge(t1, t4)
G.add_edge(t4, t5)
G.add_edge(t1, t5)

# Solve graph and print result
start_time = time.time()
dependency_graph = dict()
networkx_to_dask(G, dependency_graph, t5)
result = get(dependency_graph, t5)
end_time = time.time()
print("Result:", result, ", Time:", round(end_time - start_time, 4), "sec")

# Plot in_graph
labels = dict()
labels[t1] = r"$t_1$"
labels[t2] = r"$t_2$"
labels[t3] = r"$t_3$"
labels[t4] = r"$t_4$"
labels[t5] = r"$t_5$"

pos = nx.shell_layout(G)
nx.draw_networkx_labels(G, pos, labels)
nx.draw(G, pos, with_labels=False)
plt.show()

import time

from dask.threaded import get
from dask.delayed import Delayed

from FreeCAD import Vector

import networkx as nx
import matplotlib.pyplot as plt


# class BasicNode:
#     def __init__(self, input_labels: tuple = ("A", "B"), output_labels: tuple = ("C", )):
#         self.input_labels: tuple = input_labels
#         self.output_labels: tuple = output_labels
#
#         self.data: int = 0
#
#     def eval(self, a, b):
#         return a + b
#
#     def to_dict(self):
#         eval_result = dict()
#         eval_result[self.output_labels[0]] = (self.eval, 1, 2)
#         return eval_result
#
#
# n = BasicNode(("x", "y"), ("z", ))
# dsk = n.to_dict()
# result = get(dsk, "z")
# print(result)


# def add(a, b):
#     return a + b
#
#
# # Build graph as dict
# in_a = 5
# dsk = {"x": in_a,
#        "y": 2,
#        "z": (add, "x", "y"),
#        "w": (sum, ["x", "y", "z"]),
#        "vec": (Vector, ["x", "y", "z"])
#        }
#
# # Start timer for performance measurement
# start = time.time()
#
# # Wrapping dsk in a Dask Collection (Delayed)
# # delayed_dsk = Delayed("vec", dsk)
#
# # Compute and print result
# # result = delayed_dsk.compute()
# # print(result)
# result = get(dsk, "vec")
#
# # Stop timer for performance measurement and print time and result
# end = time.time()
# print("Execution result:", result)
# print("Execution time:", round(end - start, 4), "s")
#
# # Visualize graph
# # delayed_dsk.visualize()
# # dask.visualize(delayed_dsk)


class InputTask:
    def __init__(self, a: int = 0):
        self.a = a

    def eval(self) -> int:
        return self.a


class DefaultTask:
    @staticmethod
    def eval(a: int = 0, b: int = 0) -> int:
        return a + b


t1: InputTask = InputTask(1)
t2: InputTask = InputTask(9)
t3: DefaultTask = DefaultTask()
t4: DefaultTask = DefaultTask()

dsk = {
    t1: (t1.eval, ),
    t2: (t2.eval, ),
    t3: (t3.eval, t1, t2),
    t4: (t4.eval, t1, t3)
}

result = get(dsk, t4)
print(result)

G = nx.DiGraph()
G.add_node(t1)
G.add_node(t2)
G.add_node(t3)
G.add_node(t4)

G.add_edge(t1, t3)
G.add_edge(t2, t3)
G.add_edge(t3, t4)
G.add_edge(t1, t4)


def resolve_di_graph(graph: nx.DiGraph, node, level: int = 0) -> None:
    print(node, level)
    predecessors = graph.predecessors(node)
    for node in predecessors:
        sub_level: int = level + 1
        resolve_di_graph(graph, node, sub_level)


resolve_di_graph(G, t4)

labels = dict()
labels[t1] = r"$t_1$"
labels[t2] = r"$t_2$"
labels[t3] = r"$t_3$"
labels[t4] = r"$t_4$"

pos = nx.spectral_layout(G)
nx.draw_networkx_labels(G, pos, labels)
nx.draw(G, pos, with_labels=False)
plt.show()

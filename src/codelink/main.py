import time

from dask.threaded import get
from dask.delayed import Delayed
from FreeCAD import Vector


class BasicNode:
    def __init__(self, input_labels: tuple = ("A", "B"), output_labels: tuple = ("C", )):
        self.input_labels: tuple = input_labels
        self.output_labels: tuple = output_labels

        self.data: int = 0

    def eval(self, a, b):
        return a + b

    def to_dict(self):
        eval_result = dict()
        eval_result[self.output_labels[0]] = (self.eval, 1, 2)
        return eval_result


n = BasicNode(("x", "y"), ("z", ))
dsk = n.to_dict()
result = get(dsk, "z")
print(result)


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

# Copyright (c) 2024, Ronny Scharf-W. (ronny.scharf08@gmail.com)
# LGPL-2.1 License, see https://github.com/j8sr0230/codelink/blob/main/LICENSE

import uuid


FLATTEN = 0
SIMPLIFY = 1
GRAFT = 2


class Edge:
    def __init__(self, start_socket, end_socket, idx=None):
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.idx = uuid.uuid1() if idx is None else idx

    def __eq__(self, other):
        return self.idx == other.idx

    def __str__(self):
        return "Edge: <" + str(self.idx) + ", " + str(self.start_socket) + ", " + str(self.end_socket) + ">"


class Socket:
    def __init__(self, name="Socket", data_type=object, modifiers=None, edges=None, idx=None):
        self.name = name
        self.data_type = data_type
        self.modifiers = [] if modifiers is None else modifiers
        self.edges = [] if edges is None else edges
        self.idx = uuid.uuid1() if idx is None else idx

    def __eq__(self, other):
        return self.idx == other.idx

    def __str__(self):
        return ("Socket: <" + str(self.idx) + ", " + self.name + ", " + str(self.data_type) + ", " +
                str(self.modifiers) + ", " + str(self.edges) + ">")


def add_edge(start_socket, end_socket, idx=None):
    if start_socket == end_socket:
        return None
    elif start_socket.data_type != end_socket.data_type:
        return None
    elif (end_socket in [e.end_socket for e in start_socket.edges] or
          end_socket in [e.start_socket for e in end_socket.edges]):
        print("here")
        return None
    else:
        edge = Edge(start_socket, end_socket, idx)
        start_socket.edges.append(edge)
        end_socket.edges.append(edge)
        return edge


def remove_edge(edge):
    edge.start_socket.edges.remove(edge)
    edge.end_socket.edges.remove(edge)
    return edge


s1 = Socket("s1")
s2 = Socket("s2")
s3 = Socket("s3")

print(s1)
print(s2)
print(s3)
print()

e1: Edge = add_edge(s1, s2)
print(e1)
print(s1)
print(s2)
print(s3)
print()

e1: Edge = add_edge(s2, s1)
print(e1)
print(s1)
print(s2)
print(s3)
print()

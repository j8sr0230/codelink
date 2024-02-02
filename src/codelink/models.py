# Copyright (c) 2024, Ronny Scharf-W. (ronny.scharf08@gmail.com)
# LGPL-2.1 License, see https://github.com/j8sr0230/codelink/blob/main/LICENSE

from __future__ import annotations
from typing import Optional
import uuid


FLATTEN = 0
SIMPLIFY = 1
GRAFT = 2


class Edge:
    def __init__(self, start_socket: Socket, end_socket: Socket, idx: Optional[uuid.UUID] = None) -> None:
        self.start_socket: Socket = start_socket
        self.end_socket: Socket = end_socket
        self.idx: uuid.UUID = uuid.uuid1() if idx is None else idx

    def __eq__(self, other: Edge) -> bool:
        return self.idx == other.idx

    def __str__(self) -> str:
        return "Edge: <" + str(self.idx) + ", " + self.start_socket.name + ", " + self.end_socket.name + ">"


class Socket:
    def __init__(self, name: str = "Socket", data_type: type = int, modifiers: Optional[list[int]] = None,
                 edges: Optional[list[Edge]] = None, idx: Optional[uuid.UUID] = None) -> None:
        self.name = name
        self.data_type = data_type
        self.modifiers = [] if modifiers is None else modifiers
        self.edges = [] if edges is None else edges
        self.idx = uuid.uuid1() if idx is None else idx

    def __eq__(self, other: Socket) -> bool:
        return self.idx == other.idx

    def __str__(self) -> str:
        return str("Socket: <" + str(self.idx) + ", " + str(self.name) + ", " + str(self.data_type) + ", " +
                   str([m for m in self.modifiers]) + ", " + str([e.idx for e in self.edges]) + ">")


def add_edge(start_socket: Socket, end_socket: Socket, idx: Optional[uuid.UUID] = None) -> Optional[Edge]:
    all_edges: list[Edge] = start_socket.edges + end_socket.edges
    all_socket: list[Socket] = [edge.start_socket for edge in all_edges] + [edge.end_socket for edge in all_edges]

    if not (start_socket in all_socket and end_socket in all_socket):
        edge = Edge(start_socket, end_socket, idx)
        start_socket.edges.append(edge)
        end_socket.edges.append(edge)
        return edge


def remove_edge(edge) -> Edge:
    start_socket: Socket = edge.start_socket
    if edge in start_socket.edges:
        start_socket.edges.remove(edge)

    end_socket: Socket = edge.end_socket
    if edge in end_socket.edges:
        end_socket.edges.remove(edge)

    return edge


s1 = Socket(name="s1", data_type=float, modifiers=[SIMPLIFY, GRAFT], edges=None)
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

add_edge(s2, s1)
print(s1)
print(s2)
print(s3)
print()

add_edge(s2, s3)
print(s1)
print(s2)
print(s3)
print()

remove_edge(e1)
print(s1)
print(s2)
print(s3)
print()

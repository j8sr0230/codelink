# Copyright (c) 2024, Ronny Scharf-W. (ronny.scharf08@gmail.com)
# LGPL-2.1 License, see https://github.com/j8sr0230/codelink/blob/main/LICENSE

import uuid


class Edge:
    def __init__(self, idx=None, start_socket=None, end_socket=None):
        self.idx = str(uuid.uuid1()) if idx is None else idx
        self.sockets = [start_socket, end_socket]
        self.callbacks = []

    def reverse_sockets(self):
        self.sockets.reverse()

    def set_socket(self, socket_i, socket):
        if socket_i == 0 or socket_i == 1:
            self.sockets[socket_i] = socket
            for callback in self.callbacks:
                if type(callback) == callable:
                    callback()


a = Edge()
b = Edge(a.idx)

print(a.idx, b.idx)
a.set_socket(0, 1)

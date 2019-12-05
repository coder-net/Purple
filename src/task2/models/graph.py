import json
import networkx as nx
from typing import List
from dataclasses import dataclass


@dataclass
class Point:
    idx: int
    info = None


@dataclass
class Edge:
    idx: int
    weight: float
    points: List[int]


class Graph:
    def __init__(self, points, edges, name='Untitled'):
        self.points = points
        self.edges = edges
        self.name = name
        self.nxgraph = Graph.init_nxgraph(self.points, self.edges)
        self.pos = Graph.normalize_pos(Graph.choose_layout(self.nxgraph))
        self.shortest_edge = Graph.shortest_edge(self.pos)
        self.biggest_idx_len = Graph.biggest_idx_len(self.points)

    def update_point(self, idx, info):
        self.points[idx].info = info

    @staticmethod
    def choose_layout(g):
        methods = [
            nx.layout.spectral_layout,
            nx.layout.fruchterman_reingold_layout,
            nx.kamada_kawai_layout,
            nx.layout.spiral_layout,
        ]
        min_dist = -1
        best = None
        for method in methods:
            pos = method(g)
            dist = Graph.shortest_edge(pos)
            if dist > min_dist:
                min_dist = dist
                best = pos
        return best

    @staticmethod
    def init_nxgraph(points, edges):
        g = nx.Graph()
        g.add_nodes_from(point.idx for point in points.values())
        g.add_edges_from(edge.points for edge in edges.values())
        return g

    @staticmethod
    def normalize_pos(pos):
        x_min = y_min = float('inf')
        x_max = y_max = -float('inf')
        for x, y in pos.values():
            x_min = min(x, x_min)
            x_max = max(x, x_max)
            y_min = min(y, y_min)
            y_max = max(y, y_max)

        eps = 1e-10
        for arr in pos.values():
            arr[0] = (arr[0] - x_min) / (x_max - x_min + eps)
            arr[1] = (arr[1] - y_min) / (y_max - y_min + eps)

        return pos

    @staticmethod
    def shortest_edge(pos):
        shortest = float('inf')
        points = list(pos.values())
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                shortest = min(
                    shortest, Graph._distance(
                        *points[i], *points[j]))
        return shortest

    @staticmethod
    def biggest_idx_len(points):
        return len(str(max(points, key=lambda p: p.idx).idx))

    @staticmethod
    def _distance(x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
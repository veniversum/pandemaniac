import heapq
import networkx as nx
import numpy as np
from strategies.Strategy import Strategy


class ExForce(Strategy):
    def __init__(self):
        super().__init__('ExForce')

    def run(self, graph, seed_node_count, adj_list):
        degrees = []
        for node, adj in adj_list.items():
            exf = 0.
            clusters = []
            cluster = set(adj)
            cluster.add(node)
            for n in adj:
                dj = len(set(adj_list[n]).difference(cluster))
                clusters.append(dj)
            dj_sum = sum(clusters)

            for dj in clusters:
                dj_bar = dj/dj_sum
                exf += -dj_bar * np.log(dj_bar)

            # d = len(adj) + len(outlinks.difference(cluster))
            degrees.append((node, exf))
        # degrees = nx.degree(graph)
        heap = []
        for tup in degrees:
            heapq.heappush(heap, (-tup[1], tup[0]))

        seed_nodes = [0] * seed_node_count
        for i in range(seed_node_count):
            seed_nodes[i] = heapq.heappop(heap)[1]
        return seed_nodes

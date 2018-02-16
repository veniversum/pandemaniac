import heapq
import networkx as nx
from strategies.Strategy import Strategy


class NaiveHighestDegree(Strategy):
    def __init__(self):
        super().__init__('Naive seed nodes with highest degree')

    def run(self, graph, seed_node_count):
        centrality = nx.degree_centrality(graph)
        heap = []
        for tup in centrality.items():
            heapq.heappush(heap, tup[::-1])
        seed_nodes = [0] * seed_node_count
        for i in range(seed_node_count):
            seed_nodes[i] = heapq.heappop(heap)[1]
        return seed_nodes

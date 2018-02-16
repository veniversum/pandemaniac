import heapq
import networkx as nx
from strategies.Strategy import Strategy


class NaiveHighestDegree(Strategy):
    def __init__(self):
        super().__init__('Naive seed nodes with highest degree')

    def run(self, graph, seed_node_count):
        node_count = graph.number_of_nodes()
        degrees = nx.degree(graph)
        heap = []
        for tup in degrees:
            heapq.heappush(heap, (node_count - tup[1], tup[0]))

        seed_nodes = [0] * seed_node_count
        for i in range(seed_node_count):
            seed_nodes[i] = heapq.heappop(heap)[1]
        return seed_nodes

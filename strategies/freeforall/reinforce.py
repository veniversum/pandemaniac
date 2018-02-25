import heapq
import networkx as nx
from strategies.Strategy import Strategy


class Reinforce(Strategy):
    def __init__(self):
        super().__init__('REINFORCE')

    def run(self, G, seed_node_count, adj_list):
        node_count = G.number_of_nodes()
        target_top_degrees_n = max(1, int(seed_node_count/4))
        metrics = nx.degree(G)
        heap = []
        for tup in metrics:
            k, v = tup[0], tup[1]
            if len(heap) < seed_node_count:
                heapq.heappush(heap, (v, k))
            elif v > heap[0][0]:
                heapq.heapreplace(heap, (v, k))
        blacklist = set()
        blacklist2 = set()
        target_top_degrees = [v for k, v in heap]
        for node in target_top_degrees:
            blacklist.update(adj_list[node])
        # for node in blacklist2:
        #     blacklist.update(adj_list[node])
        target_top = [v for k, v in heapq.nlargest(target_top_degrees_n, heap)]

        rest_node_count = seed_node_count - target_top_degrees_n
        heap = []
        for node, adjs in adj_list.items():
            if node in blacklist: continue
            n_in_top = 0
            other_deg = 0
            for adj in adjs:
                if adj in target_top:
                    n_in_top += 2
                else:
                    n_in_top += 1
            if len(heap) < seed_node_count:
                heapq.heappush(heap, (n_in_top, other_deg, node))
            elif (n_in_top, other_deg, node) > heap[0]:
                heapq.heapreplace(heap, (n_in_top, other_deg, node))

        # metrics = nx.betweenness_centrality(G)
        # heap = []
        # for k, v in metrics.items():
        #     if len(heap) < seed_node_count:
        #         heapq.heappush(heap, (v, k))
        #     elif v > heap[0][0]:
        #         heapq.heapreplace(heap, (v, k))

        # seed_nodes = [0] * seed_node_count
        # for i in range(seed_node_count):
        #     seed_nodes[i] = heapq.heappop(heap)[1]
        print([v for _, _, v in heap] + target_top)
        return [v for _, _, v in heap]

import heapq
import networkx as nx
import numpy as np
from strategies.Strategy import Strategy
from strategies.naive_highest_degree import strategy as nhd


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
            if dj_sum == 0:
                continue
            for dj in clusters:
                dj_bar = dj / dj_sum
                if dj_bar == 0: continue
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


class ExForce2(Strategy):
    def __init__(self):
        super().__init__('ExForce2')
        self.enemy = nhd.NaiveHighestDegree()

    def run(self, graph, seed_node_count, adj_list, n_players=8):
        enemy_picks = self.enemy.run(graph, seed_node_count)
        n_reserve = int(seed_node_count * 1.5)  # N seeds to sample from
        heap = []
        enemy_overlap = []
        # heap = []
        # for node, adj in adj_list.items():
        #     exf = 0.
        #     clusters = []
        #     cluster = set(adj)
        #     cluster.add(node)
        #     for n in adj:
        #         dj = len(set(adj_list[n]).difference(cluster))
        #         clusters.append(dj)
        #     dj_sum = sum(clusters)
        #     if dj_sum == 0:
        #         continue
        #     for dj in clusters:
        #         dj_bar = dj / dj_sum
        #         if dj_bar == 0: continue
        #         exf += -dj_bar * np.log(dj_bar)
        #     # d = len(adj) + len(outlinks.difference(cluster))
        #
        #     if len(heap) < seed_node_count - 5:
        #         heapq.heappush(heap, (exf, node))
        #     elif exf > heap[0][0]:
        #         heapq.heapreplace(heap, (exf, node))
        seed_nodes = []#[v for _, v in heap]
        # support = heapq.nlargest(1, heap)[0][1]

        for gg in range(10):
            deg_best = 0
            node_best = None
            for node, adj in adj_list.items():
                if node in seed_nodes: continue
                exf = 0.
                clusters = []
                cluster = set(adj)
                cluster.add(node)
                for n in adj:
                    cluster2 = cluster | set(adj_list[n])
                    for m in adj_list[n]:
                        dj = len(set(adj_list[m]).difference(cluster2))
                        clusters.append(dj)
                dj_sum = sum(clusters)
                if dj_sum == 0:
                    continue
                for dj in clusters:
                    dj_bar = dj / dj_sum
                    if dj_bar == 0: continue
                    exf += -dj_bar * np.log(dj_bar)
                # exf *= np.log(0.5*len(adj))
                if exf > deg_best:
                    deg_best = exf
                    node_best = node
            seed_nodes.append(node_best)

        return set(seed_nodes)

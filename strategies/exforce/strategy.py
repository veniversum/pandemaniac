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

    def run(self, graph, seed_node_count, adj_list, n_players=2):
        enemy_picks = self.enemy.run(graph, seed_node_count)
        n_reserve = int(seed_node_count * 1.5)  # N seeds to sample from
        heap = []
        enemy_overlap = []
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

            if node in enemy_picks:
                enemy_overlap.append((exf, node))
            else:
                if len(heap) < seed_node_count:
                    heapq.heappush(heap, (exf, node))
                elif exf > heap[0][0]:
                    heapq.heapreplace(heap, (exf, node))
        best_not_in = heapq.nlargest(1, heap)
        enemy_overlap = [x for x in enemy_overlap if x[0] > best_not_in[0][0]]
        enemy_overlap.extend(heap)
        enemy_overlap.sort()
        seed_nodes = []

        n_greedy = 5 #int(float(seed_node_count) / (n_players - 1))
        n_safe = 0 #seed_node_count - n_greedy

        for i in range(n_greedy):
            exf, node = enemy_overlap.pop()
            seed_nodes.append(node)
            if (exf, node) in heap: heap.remove((exf, node))
        heap.sort()
        for i in range(n_safe):
            exf, node = heap.pop()
            seed_nodes.append(node)

        return seed_nodes

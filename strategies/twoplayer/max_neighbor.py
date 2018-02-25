import heapq
from collections import defaultdict, Counter

import networkx as nx
import numpy as np
from strategies.Strategy import Strategy
import community
import operator
from strategies.naive_highest_degree import strategy as nc


class MaxNeighbor(Strategy):
    def __init__(self):
        super().__init__('This should beat TA_more')

    def run(self, G, seed_node_count, adj_list):
        D0 = nc.NaiveHighestDegree().run(G, int(seed_node_count / 4))
        D1 = set()
        for d in D0:
            D1.update(adj_list[d])
        D2 = set()
        for d in D1:
            D2.update(adj_list[d])

        heap = []
        for node in D2:
            if node in D1: continue
            adjs = adj_list[node]
            n_in_top = 0
            other_deg = 0
            for adj in adjs:
                if adj in D1:
                    n_in_top += 1
                else:
                    other_deg += 1
            if len(heap) < seed_node_count:
                heapq.heappush(heap, (n_in_top, other_deg, node))
            elif (n_in_top, other_deg, node) > heap[0]:
                heapq.heapreplace(heap, (n_in_top, other_deg, node))

        return [v for _, _, v in heap]
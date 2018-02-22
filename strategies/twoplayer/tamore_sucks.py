import heapq
from collections import defaultdict, Counter

import networkx as nx
import numpy as np
from strategies.Strategy import Strategy
import community
import operator
from strategies.Strategy import Strategy
import community
import operator
from sklearn import cluster
from networkx.algorithms.community import label_propagation_communities
from strategies.naive_highest_degree import strategy as nc
import sim

class TamoreSucks(Strategy):
    def __init__(self):
        super().__init__('This should beat TA_more')

    def run(self, G, seed_node_count, adj_list):
        largest_cc = max(nx.connected_components(G), key=len)
        G = nx.subgraph(G, largest_cc)
        communities = list(label_propagation_communities(G))
        print("List of community sizes:", list(map(len, list(label_propagation_communities(G)))))
        best_community = list(max(communities, key=len))

        V = set()
        N_v = defaultdict(int)


        while len(V) < seed_node_count:
            best_score = 0
            best_node = None
            for node in best_community:
                if node in V: continue
                adjs = adj_list[node]
                score = 0
                for adj in adjs:
                    score += max(1, N_v[adj])
                # score /= len(adjs)
                if score > best_score:
                    best_score = score
                    best_node = node
            V.add(best_node)
            N_v[best_node] += 1
            for n in adj_list[best_node]:
                N_v[n] += 1


        # for node, adjs in adj_list.items():
        #     if node in isolates: continue
        #     # if parts[node] != chosen_part: continue
        #     n_in_top = 0
        #     other_deg = 0
        #     for adj in adjs:
        #         for n in adj_list[adj]:
        #             if parts[n] == chosen_part:
        #                 n_in_top += 2
        #             else:
        #                 n_in_top += 1
        #     if len(heap) < seed_node_count:
        #         heapq.heappush(heap, (n_in_top, other_deg, node))
        #     elif (n_in_top, other_deg, node) > heap[0]:
        #         heapq.heapreplace(heap, (n_in_top, other_deg, node))

        return V

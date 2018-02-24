import heapq
import numpy as np
import networkx as nx


def get_exf_dict(adj_list):
    exf_dict = {}
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
        exf_dict[node] = exf
    return exf_dict


def get_the_best_node(exf_dict):
    best_node = None
    best_exf = -1
    for node, exf in exf_dict.items():
        if exf > best_exf:
            best_node = node
            best_exf = exf
    return best_node


def get_n_best(n, val_dict, bunch):
    heap = []

    for node in bunch:
        heapq.heappush(heap, (-val_dict[node], node))

    best = [0] * n
    for i in range(n):
        best[i] = heapq.heappop(heap)[1]
    return best


class CommunitiesStrategy:
    def __init__(self, name, community_count=2):
        self.name = name
        self.community_count = community_count

    def run(self, adj_list, G):

        # Determine the largest connected component
        connected_components = nx.connected_components(G)
        best_size = -1
        best_n_bunch = None
        for n_bunch in connected_components:
            if len(n_bunch) > best_size:
                best_n_bunch = n_bunch
                best_size = len(n_bunch)

        best_subgraph = nx.subgraph(G, best_n_bunch)
        subgraph_adj_data = best_subgraph.adjacency()
        subgraph_adj_list = {}
        for a, b in subgraph_adj_data:
            subgraph_adj_list[a] = list(b)
        exf_dict = get_exf_dict(subgraph_adj_list)

        communities = list(nx.algorithms.community.asyn_fluidc(best_subgraph, k=self.community_count))
        community_heap = []
        for community in communities:
            community_rating = 0
            for node in community:
                community_rating += exf_dict[node]
            heapq.heappush(community_heap, (-community_rating, community))

        # heapq.heappop(community_heap)
        # if self.community_count > 2:
        #     heapq.heappop(community_heap)
        community_to_use = heapq.heappop(community_heap)[1]

        community_subgraph = nx.subgraph(best_subgraph, community_to_use)
        betweenness = nx.closeness_centrality(community_subgraph)
        offset = 40
        seed_nodes = get_n_best(offset + 10, betweenness, community_to_use)

        return seed_nodes[offset - 1:]

import heapq
import numpy as np
import networkx as nx
from sklearn import cluster


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


def get_n_best_nodes(n, exf_dict, node_bunch):
    heap = []

    for node in node_bunch:
        heapq.heappush(heap, (-exf_dict[node], node))

    best_nodes = [0] * n
    for i in range(n):
        best_nodes[i] = heapq.heappop(heap)[1]
    return best_nodes


class ClusteringStrategy:
    def __init__(self, name, cluster_count=2):
        self.name = name
        self.cluster_count = cluster_count

    def run(self, adj_list, G):
        n = G.number_of_nodes()
        adj_matrix = nx.adjacency_matrix(G)

        # Choose the best cluster and get its exforce
        clustering = cluster.spectral_clustering(adj_matrix, n_clusters=self.cluster_count, eigen_solver='arpack')
        cluster_1 = []
        cluster_2 = []
        for i in range(n):
            i_str = str(i)
            cluster_index = clustering[i]
            if cluster_index == 0:
                cluster_1.append(i_str)
            else:
                cluster_2.append(i_str)
        if len(cluster_1) > len(cluster_2):
            cluster_to_use = cluster_1
        else:
            cluster_to_use = cluster_2
        cluster_subgraph = nx.subgraph(G, cluster_to_use)
        cluster_adj_data = cluster_subgraph.adjacency()
        cluster_adj_list = {}
        for a, b in cluster_adj_data:
            cluster_adj_list[a] = list(b)
        exf_dict = get_exf_dict(cluster_adj_list)

        # Figure out neighbours of the best node. Out of these neighbours, pick 3 best nodes and figure 2 of their
        # best neighbours that weren't seen before.
        best_node = get_the_best_node(exf_dict)
        immediate_neighbours = cluster_adj_list[best_node]
        seen_nodes = {best_node: True}
        for node in immediate_neighbours:
            seen_nodes[node] = True
        best_neighbours = get_n_best_nodes(3, exf_dict, immediate_neighbours)
        seed_nodes = best_neighbours[:]
        seed_nodes.append(best_node)

        # At this point we have 1 best node, and its 3 best neighbours. This leaves us with 6 leftover seed nodes. We
        # find that best neighbours of our new 3 potential nodes that we have *not* seen before, and drop 2 seed
        # nodes in each case.
        for node in best_neighbours:
            neighbours = cluster_adj_list[node]
            potential_nodes = []
            for neighbour in neighbours:
                if seen_nodes.get(neighbour) is None:
                    seen_nodes[neighbour] = True
                    potential_nodes.append(neighbour)
            new_seed_nodes = get_n_best_nodes(2, exf_dict, potential_nodes)
            seed_nodes.extend(new_seed_nodes)

        return seed_nodes

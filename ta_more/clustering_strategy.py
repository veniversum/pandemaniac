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


def get_n_best(n, val_dict, bunch):
    heap = []

    for node in bunch:
        heapq.heappush(heap, (-val_dict[node], node))

    best = [0] * n
    for i in range(n):
        best[i] = heapq.heappop(heap)[1]
    return best


class ClusteringStrategy:
    def __init__(self, name, cluster_count=2):
        self.name = name
        self.cluster_count = cluster_count

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

        # Choose the best cluster and get its exforce
        clustering = cluster.spectral_clustering(nx.adjacency_matrix(best_subgraph), n_clusters=self.cluster_count,
                                                 eigen_solver='arpack')
        cluster_1 = []
        cluster_2 = []
        for i in range(len(clustering)):
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

        # offset = 50
        # seed_nodes = get_n_best(offset + 10, exf_dict, exf_dict.keys())
        #
        # return seed_nodes[offset:]

        # Figure out neighbours of the best node. Out of these neighbours, pick 3 best nodes and figure 2 of their
        # best neighbours that weren't seen before.
        best_node = get_n_best(2, exf_dict, exf_dict.keys())[1]
        immediate_neighbours = cluster_adj_list[best_node]
        seen_nodes = {best_node: True}
        for node in immediate_neighbours:
            seen_nodes[node] = True
        best_neighbours = get_n_best_nodes(10, exf_dict, immediate_neighbours)
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
            try:
                new_seed_nodes = get_n_best_nodes(5, exf_dict, potential_nodes)
                seed_nodes.extend(new_seed_nodes)
            except:
                print('Error!')

        offset = 20
        # seed_nodes = get_n_best(offset + 10, exf_dict, exf_dict.keys())

        return (seed_nodes[offset:])[:20]

        # return seed_nodes

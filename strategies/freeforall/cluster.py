import heapq
from collections import defaultdict, Counter

import networkx as nx
import numpy as np
from strategies.Strategy import Strategy
import community
import operator
from sklearn import cluster
from networkx.algorithms.community import label_propagation_communities, asyn_fluidc
from strategies.naive_highest_degree import strategy as nc
import sim


class Cluster(Strategy):
    def __init__(self):
        super().__init__('This should beat TA_more')

    def run(self, graph, seed_node_count, adj_list):
        print("Number of nodes:", graph.number_of_nodes())
        n_clusters = 3
        print("List of CC sizes:", list(map(len, nx.connected_components(graph))))
        largest_cc = max(nx.connected_components(graph), key=len)
        G = nx.subgraph(graph, largest_cc)

        communities = list(label_propagation_communities(G))
        print("List of community sizes:", list(map(len, communities)))
        best_community = list(max(communities, key=len))
        # best_community, best_community2 = sorted(communities, key=len)[-2:]
        # communities.remove(best_community)
        # best_community2 = list(max(communities, key=len))

        # best_community_nodes = int(float(seed_node_count) * len(best_community) / (len(best_community) + len(best_community2)))
        # best_community2_nodes = seed_node_count - best_community_nodes

        # sc = cluster.SpectralClustering(n_clusters=n_clusters,
        #                                 eigen_solver='arpack',
        #                                 affinity="precomputed", n_init=100, assign_labels='discretize')
        # adj_matrix = nx.to_numpy_matrix(G)
        # sc.fit(adj_matrix)
        # labels = sc.labels_
        # cluster_dict = dict()
        # for i, k in enumerate(G.nodes()):
        #     cluster_dict[k] = labels[i]
        # best_avg_cluster = -1
        # best_cluster_avg = -1
        # best_sum_cluster = -1
        # best_cluster_sum = -1
        # for i in range(n_clusters):
        #     nodes_in_cluster = [k for k, v in cluster_dict.items() if v == i]
        #     cluster_sum = np.sum([tup[1] for tup in G.degree(nodes_in_cluster)])
        #     cluster_avg = np.average([tup[1] for tup in G.degree(nodes_in_cluster)])
        #     # print(i, ':', cluster_sum, ':', cluster_avg, ';', len(nodes_in_cluster))
        #     if cluster_sum > best_cluster_sum:
        #         best_sum_cluster = i
        #         best_cluster_sum = cluster_sum
        #
        #     if cluster_avg > best_cluster_avg:
        #         best_avg_cluster = i
        #         best_cluster_avg = cluster_avg
        # best_community = [n for n in G.nodes() if cluster_dict[n] == best_sum_cluster]

        G = nx.subgraph(graph, best_community)

        target_top_degrees_n = max(1, int(seed_node_count / 4))
        metrics = nx.degree(G)
        heap = []
        for tup in metrics:
            # if tup[0] not in best_community: continue
            k, v = tup[0], tup[1]
            if len(heap) < seed_node_count * 2:
                heapq.heappush(heap, (v, k))
            elif v > heap[0][0]:
                heapq.heapreplace(heap, (v, k))
        target_top_degrees = [v for k, v in heap]
        target_top = [v for k, v in heapq.nlargest(target_top_degrees_n, heap)]

        heap = []
        print("Size of chosen community:", len(best_community))
        for node in best_community:
            if node in target_top_degrees: continue
            adjs = adj_list[node]
            exf = 0.
            clusters = []
            local_cluster = set(adjs)
            local_cluster.add(node)
            for n in adjs:
                dj = len(set(adj_list[n]).difference(local_cluster))
                if n in target_top:
                    dj *= 1.5
                clusters.append(dj)
            dj_sum = sum(clusters)
            if dj_sum == 0:
                continue
            for dj in clusters:
                dj_bar = dj / dj_sum
                if dj_bar == 0: continue
                exf += -dj_bar * np.log(dj_bar)

            n_in_top = 0
            n_in_top = exf
            other_deg = 0
            # for adj in adjs:
            #     if cluster_dict[adj] == best_cluster or cluster_dict[adj] == avg_cluster:
            #         n_in_top += 1.5
            #     else:
            #         n_in_top += 1
            if len(heap) < seed_node_count:
                heapq.heappush(heap, (n_in_top, other_deg, node))
            elif (n_in_top, other_deg, node) > heap[0]:
                heapq.heapreplace(heap, (n_in_top, other_deg, node))

        print(heap)
        heap = [v for _, _, v in heap]

        return heap

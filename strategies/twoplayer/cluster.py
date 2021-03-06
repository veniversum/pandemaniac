import heapq
from collections import defaultdict, Counter

import networkx as nx
import numpy as np
from strategies.Strategy import Strategy
import community
import operator
from sklearn import cluster
from networkx.algorithms.community import label_propagation_communities
from strategies.naive_highest_degree import strategy as nc
import sim


class Cluster(Strategy):
    def __init__(self):
        super().__init__('This should beat TA_more')

    def run(self, G, seed_node_count, adj_list):
        n_clusters = 3
        largest_cc = max(nx.connected_components(G), key=len)
        G = nx.subgraph(G, largest_cc)
        sc = cluster.SpectralClustering(n_clusters=n_clusters,
                                        eigen_solver='arpack',
                                        affinity="precomputed", n_init=100, assign_labels='discretize')
        dbs = cluster.DBSCAN(metric='precomputed')
        adj_matrix = nx.to_numpy_matrix(G)
        sc.fit(adj_matrix)
        labels = sc.labels_
        communities = list(label_propagation_communities(G))
        print("List of community sizes:", list(map(len, list(label_propagation_communities(G)))))
        best_community = list(max(communities, key=len))
        cluster_dict = dict()
        for i, k in enumerate(G.nodes()):
            cluster_dict[k] = labels[i]

        best_cluster = -1
        best_cluster_avg = -1

        avg_cluster = -1
        avg_cluster_avg = -1
        for i in range(n_clusters):
            nodes_in_cluster = [k for k, v in cluster_dict.items() if v == i]
            cluster_sum = np.sum([tup[1] for tup in G.degree(nodes_in_cluster)])
            cluster_avg = np.average([tup[1] for tup in G.degree(nodes_in_cluster)])
            # print(i, ':', cluster_sum, ':', cluster_avg, ';', len(nodes_in_cluster))
            if cluster_avg > avg_cluster_avg:
                avg_cluster = i
                avg_cluster_avg = cluster_avg

            if cluster_sum > best_cluster_avg:
                best_cluster = i
                best_cluster_avg = cluster_sum

        nodes_in_cluster = [k for k, v in cluster_dict.items() if v == best_cluster]
        heap = []
        print("Size of chosen community:", len(best_community))
        for node in best_community:
            adjs = adj_list[node]
            exf = 0.
            clusters = []
            local_cluster = set(adjs)
            local_cluster.add(node)
            for n in adjs:
                dj = len(set(adj_list[n]).difference(local_cluster))
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
            if len(heap) < seed_node_count + 3:
                heapq.heappush(heap, (n_in_top, other_deg, node))
            elif (n_in_top, other_deg, node) > heap[0]:
                heapq.heapreplace(heap, (n_in_top, other_deg, node))

        print(heap)
        heap = [v for _, _, v in heap]
        import itertools
        best = None
        best_score = -1
        from networkx.algorithms.community import k_clique_communities
        # heap = list(k_clique_communities(G, 13))[0]
        for nodes in itertools.combinations(heap, seed_node_count):
            sim_data = {
                'self': nodes,
                'alt': nc.NaiveHighestDegree().run(G, int(1.2 * seed_node_count))
            }
            results = sim.run(adj_list, sim_data)
            if results['self'] > results['alt']:
                print('*** Found good nodes! ****')
            if results['self'] > best_score:
                best = nodes
                best_score = results['self']
                print('New best score:', best_score)

        return best

from sklearn.cluster import spectral_clustering
from strategies.Strategy import Strategy
import networkx as nx
import numpy as np
import math
import heapq


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


class BetweennessClustering(Strategy):
    def __init__(self):
        super().__init__('Best nodes based on clustering and betweenness')

    def run(self, graph, seed_node_count, adj_list):
        n = graph.number_of_nodes()
        best_nodes_per_cluster = 2
        cluster_count = int(math.ceil(seed_node_count / best_nodes_per_cluster))
        labels = spectral_clustering(nx.adjacency_matrix(graph), n_clusters=cluster_count, eigen_solver='arpack')

        # subnodes = []
        # for _ in range(cluster_count):
        #     subnodes.append([])
        # for i in range(n):
        #     subnodes[labels[i]].append(str(i))
        #
        # best_nodes = []
        # for i in range(cluster_count):
        #     print(subnodes[i])
        #     subgraph = graph.subgraph(subnodes[i])
        #     heap = []
        #     for tup in nx.betweenness_centrality(subgraph).items():
        #         heapq.heappush(heap, (-tup[1], tup[0]))
        #
        #     for _ in range(best_nodes_per_cluster):
        #         best_node = heapq.heappop(heap)[1]
        #         print(best_node)
        #         best_nodes.append(best_node)

        heaps = []
        for _ in range(cluster_count):
            heaps.append([])
        # Sort nodes+exforces into heaps by clusters
        exf_map = get_exf_dict(adj_list)
        for i in range(graph.number_of_nodes()):
            label = labels[i]
            i_str = str(i)
            exforce = exf_map.get(i_str)
            if exforce is not None:
                heapq.heappush(heaps[label], (-exforce, i_str))

        # Get best nodes
        best_nodes = []
        index = 0
        for i in range(cluster_count):
            for k in range(best_nodes_per_cluster):
                if index >= seed_node_count:
                    print(best_nodes)
                    return best_nodes
                try:
                    tup = heapq.heappop(heaps[i])
                except:
                    break
                best_nodes.append(tup[1])
                index += 1

        if len(best_nodes) < seed_node_count:
            deficit = seed_node_count - len(best_nodes)
            for i in range(cluster_count):
                while deficit > 0:
                    try:
                        tup = heapq.heappop(heaps[i])
                    except:
                        break
                    best_nodes.append(tup[1])
                    deficit -= 1

        print(best_nodes)

        return best_nodes[:seed_node_count]

import heapq
import networkx as nx
from strategies.Strategy import Strategy
import numpy as np
import sim


class CMAB(Strategy):
    def __init__(self):
        super().__init__('Combinatorial multi-armed bandit')
        self.t = 0

    def run(self, graph, seed_node_count, iters=20, actual=False):
        self.graph = graph
        node_count = graph.number_of_nodes()
        self.node_count = node_count
        self.T = np.zeros(node_count)
        self.mu = np.ones(node_count)
        self.k = seed_node_count
        self.alt_strategy.run(self.graph, self.k)

        choice = []
        for _ in range(iters):
            choice = self.step()
            print(sum(x[1] for x in list(graph.degree(list(map(str, choice))))))

        return choice

    def setup(self, adj_list, alt_strategy):
        self.adj_list = adj_list
        self.alt_strategy = alt_strategy

    def step(self):
        self.t += 1
        mu_bar = np.empty(self.node_count)
        for i in range(self.node_count):
            mu_bar[i] = (self.mu[i] + np.sqrt(3 * np.log(self.t) / (2 * self.T[i])))
        ind = np.argpartition(mu_bar, -self.k)[-self.k:]
        sim_data = {
            'self': [str(x) for x in ind],
            'alt': [str(x) for x in self.alt_picks],
        }
        results = sim.run(self.adj_list, sim_data)
        score = results['self'] / self.node_count
        self.T[ind] += 1
        self.mu[ind] = self.mu[ind] + (score - self.mu[ind]) / self.T[ind]
        return ind

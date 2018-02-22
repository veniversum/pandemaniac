import heapq
import networkx as nx
from strategies.Strategy import Strategy
from strategies.naive_highest_degree import strategy as nhd
from strategies.exforce import strategy as exf
import numpy as np
import sim

ALPHA_0 = 1.
BETA_0 = 1.


class CMAB(Strategy):
    def __init__(self):
        super().__init__('Combinatorial multi-armed bandit')
        self.alt_strategy = exf.ExForce()
        self.t = 0

    def run(self, graph, seed_node_count, adj_list, iters=100, actual=False):
        self.graph = graph
        self.adj_list = adj_list
        node_count = graph.number_of_nodes()
        self.node_count = node_count
        self.T = np.zeros(node_count)
        self.mu = np.zeros(node_count)
        self.k = seed_node_count
        self.alt_picks = self.alt_strategy.run(self.graph, self.k, adj_list=adj_list)
        degrees = graph.degree
        for tup in degrees:
            self.mu[int(tup[0])] = tup[1]
        self.mu /= np.max(self.mu) + 1
        choice = []
        for _ in range(iters):
            choice = self.thompson()
            print(sum(x[1] for x in list(graph.degree(list(map(str, choice))))))
        choice = self.thompson()
        return choice

    def setup(self, adj_list, alt_strategy):
        self.alt_strategy = alt_strategy

    def step(self):
        self.t += 1
        mu_bar = np.empty(self.node_count)
        for i in range(self.node_count):
            mu_bar[i] = np.maximum(self.mu[i] + np.sqrt(3 * np.log(self.t) / (2 * self.T[i])), 2)
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

    def inference(self):
        ind = np.argpartition(self.mu, -self.k)[-self.k:]
        return ind

    def thompson(self):
        self.t += 1
        theta = np.zeros(self.node_count)
        for i in range(self.node_count):
            alpha = ALPHA_0 + self.mu[i]
            beta = BETA_0 + self.T[i] - self.mu[i]
            theta[i] = np.random.beta(alpha, beta)
        ind = np.argpartition(theta, -self.k)[-self.k:]
        sim_data = {
            'self': [str(x) for x in ind],
            'alt': [str(x) for x in self.alt_picks],
        }
        results = sim.run(self.adj_list, sim_data)
        score = results['self'] / self.node_count
        self.T[ind] += 1
        self.mu[ind] += score
        return ind
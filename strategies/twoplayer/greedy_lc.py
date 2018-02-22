import heapq
from collections import defaultdict, Counter

import networkx as nx
import numpy as np
from strategies.Strategy import Strategy
import community
from strategies.naive_highest_degree import strategy as nc
import operator


class Greedy_C_LC(Strategy):
    def __init__(self):
        super().__init__('This should beat TA_more')

    def run(self, G, seed_node_count, adj_list):
        N_memo = {}
        C_lc_memo = {}
        C_lc2_memo = {}
        avoid = nc.NaiveHighestDegree().run(G, int(seed_node_count))
        avoid = avoid[:1]

        def N(v):
            if v in N_memo: return N_memo[v]
            n = set(adj_list[v])
            for i in adj_list[v]:
                n.update(adj_list[i])
            N_memo[v] = len(n)
            return len(n)

        def C_lc(v):
            if v in C_lc_memo: return C_lc_memo[v]
            acc = 0
            for u in adj_list[v]:
                for w in adj_list[u]:
                    acc += N(w)
            C_lc_memo[v] = acc
            return acc

        def C_lc2(V):
            # if V in C_lc2_memo: return C_lc2_memo[V]
            acc = 0
            V_p = set()
            for v in V:
                V_p.update(adj_list[v])
                acc += N(v)
            # for u in V_p:
            #     for w in adj_list[u]:
            #         acc += N(w)
            # C_lc2_memo[V] = acc
            return acc

        V = set()

        while len(V) < seed_node_count:
            bestVal = 0
            bestInd = None
            V_n = set()
            for v in avoid:
                V_n.update(adj_list[v])
            if len(V_n) == 0:
                V_n = set(G.nodes())
            for i in V_n.difference(V).difference(avoid):
                curVal = C_lc2(V | {i})
                if curVal > bestVal:
                    bestVal = curVal
                    bestInd = i
            V.add(bestInd)
            print(bestVal, bestInd)

        return V

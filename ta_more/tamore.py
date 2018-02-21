import sim
import json
import networkx as nx
from ta_more.tamore_strategy import TaMoreStrategy

graphs = [
    '2.10.30',
    '2.10.31',
    '2.10.32',
    '2.10.33',
]


def load_graph(adj_list):
    G = nx.Graph()
    for node, neighbours in adj_list.items():
        G.add_node(node)
        for neighbour in neighbours:
            G.add_edge(node, neighbour)
    return G


def main():
    for graph_name in graphs:
        adj_list = json.load(open('data/{0}.json'.format(graph_name)))
        G = load_graph(adj_list)
        strategy = TaMoreStrategy()
        our_seeds = strategy.run(adj_list, G, 10)
        tamore_all_seeds = json.load(open('data/{0}-seeds.json'.format(graph_name)))['TA_more']

        our_wins = 0
        tamore_wins = 0
        ties = 0
        for tamore_seeds in tamore_all_seeds:
            sim_data = {
                'RabidPandas': our_seeds,
                'TA_more': tamore_seeds
            }
            results = sim.run(adj_list, sim_data)
            if results['TA_more'] > results['RabidPandas']:
                tamore_wins += 1
            elif results['TA_more'] < results['RabidPandas']:
                our_wins += 1
            else:
                ties += 1

        print('{0}:  RabidPandas  {1: <3} -   {2: <3}  TA_more   ({3} ties)'.format(graph_name, our_wins,
                                                                                    tamore_wins, ties))


if __name__ == '__main__':
    main()

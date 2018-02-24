import sim
import json
from os import path
import networkx as nx
from strategies.naive_highest_degree import strategy as nc
from ta_more.clustering_strategy import ClusteringStrategy
from ta_more.communities_strategy import CommunitiesStrategy

graphs = [
    # '2.10.30',
    # '2.10.31',
    # '2.10.32',
    # '2.10.33',
    # '2.10.34',
    '27.10.1',
]

strategies = [
    CommunitiesStrategy('3 communities', 3),
    # CommunitiesStrategy('3 communities', 3),
    # ClusteringStrategy('2 clusters', 2),
    # ClusteringStrategy('3 clusters', 3),
]


def load_graph(adj_list):
    G = nx.Graph()
    for node, neighbours in adj_list.items():
        G.add_node(node)
        for neighbour in neighbours:
            G.add_edge(node, neighbour)
    return G


def main():
    for strategy in strategies:
        print('Strategy `{0}`'.format(strategy.name))
        for graph_name in graphs:
            adj_list = json.load(open('data/{0}.json'.format(graph_name)))
            seed_file = 'data/{0}-seeds.json'.format(graph_name)
            if path.isfile(seed_file):
                team_seeds = json.load(open(seed_file))
            else:
                raise Exception('Nope')

            G = load_graph(adj_list)
            our_seeds = strategy.run(adj_list, G)

            for round_no in range(50):
                sim_data = {
                    'RabidPandas': our_seeds,
                }
                for team, seeds in team_seeds.items():
                    if team != 'RabidPandas':
                        sim_data[team] = seeds[round_no]
                results = sim.run(adj_list, sim_data)
                our_score = results['RabidPandas']
                lost = False
                lost_to = ''
                for team, score in results.items():
                    if team != 'RabidPandas':
                        if score > our_score:
                            lost = True
                            lost_to += ' ' + str(score)
                if not lost:
                    print('Won round {}, {} nodes.'.format(round_no, our_score))
                else:
                    print('--- round {}, {} nodes. Lost to : {}'.format(round_no, our_score, lost_to))


if __name__ == '__main__':
    main()

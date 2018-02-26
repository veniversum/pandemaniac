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
    # '27.10.1',
    '13.20.9',
    # '13.10.6',
]

strategies = [
    # CommunitiesStrategy('2 communities', 2),
    # CommunitiesStrategy('4 communities', 4),
    ClusteringStrategy('2 clusters', 2),
    # ClusteringStrategy('3 clusters', 3),
]


def load_graph(adj_list):
    G = nx.Graph()
    for node, neighbours in adj_list.items():
        G.add_node(node)
        for neighbour in neighbours:
            G.add_edge(node, neighbour)
    return G


output = 'output.txt'


def main():
    for strategy in strategies:
        won_rounds = 0
        print('Strategy `{0}`'.format(strategy.name))
        for graph_name in graphs:
            adj_list = json.load(open('data/{0}.json'.format(graph_name)))
            seed_file = 'data/{0}-seeds.json'.format(graph_name)
            G = load_graph(adj_list)
            if path.isfile(seed_file):
                team_seeds = json.load(open(seed_file))
            else:
                naive_seeds = nc.NaiveHighestDegree().run(G, 120, )
                team_seeds = {
                    'Naive1': [naive_seeds[10:20]],
                    'Naive2': [naive_seeds[30:40]],
                    'Naive3': [naive_seeds[50:60]],
                    'Naive4': [naive_seeds[60:70]],
                    'Naive5': [naive_seeds[80:90]],
                }

            our_seeds = strategy.run(adj_list, G)
            assert len(our_seeds) == 20

            node_output = '\n'.join(str(x) for x in our_seeds) + '\n'
            output_file = open(output, 'w')
            for i in range(50):
                output_file.write(node_output)

            for round_no in range(len(list(team_seeds.values())[0])):
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
                    won_rounds += 1
                else:
                    print('--- round {}, {} nodes. Lost to : {}'.format(round_no, our_score, lost_to))

        print('Strategy `{0}` won {1}/50 rounds'.format(strategy.name, won_rounds))


if __name__ == '__main__':
    main()

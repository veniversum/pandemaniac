#!/usr/bin/env python

import sys
import json
import sim
import networkx as nx
from strategies.naive_highest_degree import strategy as nc
from strategies.close_to_bridges import strategy as ctb
from strategies.combinatorial_multi_armed_bandit import strategy as cmab
from strategies.exforce import strategy as exf
from strategies.freeforall import reinforce as reinforce
from strategies.twoplayer import tamore_sucks as tamore
from strategies.twoplayer import greedy_lc
from strategies.twoplayer import cluster
from strategies.freeforall import cluster as ffacluster
from strategies.freeforall import communities as comm
from strategies.twoplayer import max_neighbor
from collections import defaultdict

strategies = {
    '1': nc.NaiveHighestDegree(),
    '2': ctb.CloseToBridges(),
    '3': cmab.CMAB(),
    '4': exf.ExForce(),
    '5': exf.ExForce2(),
    '7': tamore.TamoreSucks(),
    '8': greedy_lc.Greedy_C_LC(),
    '9': cluster.Cluster(),
    '10': max_neighbor.MaxNeighbor(),

    #Free for all
    '6': reinforce.Reinforce(),
    '11': ffacluster.Cluster(),
    '12': comm.CommunitiesStrategy(''),
}

benchmark_strategy = strategies['1']

graphs = {
    '1': 'graphs/testgraph1.json',
    '2': 'graphs/testgraph2.json',
    'other': 'graphs/27.10.3.json'
}

output = 'output/output.txt'


def load_graph(graph_data):
    graph = nx.Graph()
    for node, neighbours in graph_data.items():
        graph.add_node(node)
        for neighbour in neighbours:
            graph.add_edge(node, neighbour)
    return graph


if __name__ == '__main__':

    # Input start
    input_strategy = None
    if len(sys.argv) < 2 or strategies.get(sys.argv[1]) is None:
        print("Specify strategy number:")
        for i in range(1, len(strategies) + 1):
            print('  {0}   {1}'.format(i, strategies.get(str(i)).name))
        input_strategy = str(input('Strategy number: '))
    else:
        input_strategy = sys.argv[1]
    if strategies.get(input_strategy) is None:
        raise Exception('Invalid option provided: ' + input_strategy)

    input_graph = None
    if len(sys.argv) < 3 or graphs.get(sys.argv[2]) is None:
        print("Specify graph number:")
        for k, v in graphs:
            print("  %s   - %s" % (k, v))
        input_graph = str(input('Graph to use: '))
    else:
        input_graph = sys.argv[2]
    if graphs.get(input_graph) is None:
        raise Exception('Invalid option provided: ' + input_graph)

    # TODO: Extract # of seed nodes from graph name?

    input_seed_nodes = None
    if len(sys.argv) < 4:
        input_seed_nodes = str(input('Number of seed nodes: '))
    else:
        input_seed_nodes = sys.argv[3]

    if len(sys.argv) < 5:
        visualize = False
    else:
        visualize = int(sys.argv[4])
    # Input end

    # Prepare variables
    strategy = strategies.get(input_strategy)
    graph_data = json.load(open(graphs.get(input_graph)))
    graph = load_graph(graph_data)
    seed_node_count = int(input_seed_nodes)

    # Run the strategy
    seed_node_list = strategy.run(graph, seed_node_count, adj_list=graph_data)
    assert len(seed_node_list) == seed_node_count

    # Write output
    node_output = '\n'.join(str(x) for x in seed_node_list) + '\n'
    output_file = open(output, 'w')
    for i in range(50):
        output_file.write(node_output)
    output_file.close()

    print('Wrote output to `{0}`!'.format(output))

    print('Preparing benchmark strategy and running simulation...')

    benchmark_seeds = benchmark_strategy.run(graph, int(seed_node_count), adj_list=graph_data)
    winner_count = defaultdict(int)
    for i in range(0,0):
        print("Run #", i)
        simd = json.load(open('graphs/27.10.2-RabidPandas.json'))
        simd2 = {k: v[i] for k, v in simd.items() if k != 'RabidPandas'}
        simd2['RabidPandas'] = seed_node_list
        sim_data = {
            benchmark_strategy.name + ' (benchmark)': [str(x) for x in benchmark_seeds],
            strategy.name: [str(x) for x in seed_node_list],
        }
        results = sim.run(graph_data, simd2, verbose=0, visualize=visualize)
        print('Results:')
        for strategy_name, node_count in results.items():
            print(' {0: <4} -> {1}'.format(node_count, strategy_name))
        import operator
        winner = max(results.items(), key=operator.itemgetter(1))[0]
        winner_count[winner] += 1
    print('Results:')
    for strategy_name, node_count in winner_count.items():
        print(' {0: <4} -> {1}'.format(node_count, strategy_name))

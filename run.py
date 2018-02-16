#!/usr/bin/env python

import sys
import json
import networkx as nx
from strategies.naive_highest_degree import strategy as nc
from strategies.close_to_bridges import strategy as ctb

strategies = {
    '1': nc.NaiveHighestDegree(),
    '2': ctb.CloseToBridges(),
}

graphs = {
    '1': 'graphs/testgraph1.json',
    '2': 'graphs/testgraph2.json',
}

output = 'output/output.txt'


def load_graph(graph_file):
    graph_data = json.load(open(graph_file))
    graph = nx.Graph()
    for node, neighbours in graph_data.items():
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
        print("  1   - Test graph 1")
        print("  2   - Test graph 2")
        input_graph = str(input('Strategy number: '))
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
    # Input end

    # Prepare variables
    strategy = strategies.get(input_strategy)
    graph = load_graph(graphs.get(input_graph))
    seed_node_count = int(input_seed_nodes)

    # Run the strategy
    seed_node_list = strategy.run(graph, seed_node_count)
    assert len(seed_node_list) == seed_node_count

    # Write output
    node_output = '\n'.join(str(x) for x in seed_node_list) + '\n'
    output_file = open(output, 'w')
    for i in range(50):
        output_file.write(node_output)

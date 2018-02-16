class Strategy:
    def __init__(self, name):
        self.name = name

    def run(self, graph, seed_node_count):
        """
        :param graph: A networkx graph instance
        :param seed_node_count: Number of seed nodes the algorithm needs to produce
        :return: A list of "seed" node indices, i.e. [1, 2, 3] or ["5", "6", "7"]
        """
        raise NotImplementedError('Method run() is not implemented in strategy {0}'.format(self.name))

from strategies.Strategy import Strategy


class BetweennessClustering(Strategy):
    def __init__(self):
        super().__init__('Best nodes based on clustering and betweenness')

    def run(self, graph, seed_node_count, **kwargs):
        return range(seed_node_count)

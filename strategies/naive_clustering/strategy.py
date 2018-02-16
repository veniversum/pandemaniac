from strategies.Strategy import Strategy


class NaiveClustering(Strategy):
    def __init__(self):
        super().__init__('Naive best node in each cluster')

    def run(self, graph, seed_node_count):
        return [1] * seed_node_count

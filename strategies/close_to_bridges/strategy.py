from strategies.Strategy import Strategy


class CloseToBridges(Strategy):
    def __init__(self):
        super().__init__('Best nodes closer to bridges')

    def run(self, graph, seed_node_count):
        raise NotImplementedError('NYI')

import numpy as np
from bayesian_network import BayesianNetworkModel
from pgmpy.inference import VariableElimination

class MonteCarloSimulation:
    def __init__(self, network_model: BayesianNetworkModel):
        self.network_model = network_model
        self.inference = VariableElimination(network_model.network)

    def run_simulation(self, evidence, num_samples=1000):
        results = []
        for _ in range(num_samples):
            sample = self.inference.map_query(variables=evidence.keys(), evidence=evidence)
            results.append(sample)
        return results
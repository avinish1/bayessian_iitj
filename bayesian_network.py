from pgmpy.models import BayesianNetwork
from cpd_builder import CPDBuilder

class BayesianNetworkModel:
    def __init__(self, variables):
        self.variables = variables
        self.network = BayesianNetwork()
        self.cpds = None

    def build_network_structure(self):
        for var in self.variables:
            for parent in (var.cpd.parents if var.cpd else []):
                self.network.add_edge(parent.name, var.name)

    def add_cpds(self):
        cpd_builder = CPDBuilder(self.variables)
        self.cpds = cpd_builder.build_all_cpds()
        for cpd in self.cpds.values():
            self.network.add_cpds(cpd)

    def initialize(self):
        self.build_network_structure()
        self.add_cpds()
        self.network.check_model()

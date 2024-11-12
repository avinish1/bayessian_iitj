# network_builder.py

import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.factors.continuous import ContinuousFactor
from scipy.stats import norm

def create_network_structure(config):
    """
    Creates a Bayesian Network structure from configuration data.
    :param config: Parsed configuration dictionary.
    :return: An instance of pgmpy.models.BayesianNetwork with nodes and edges added.
    """
    network = BayesianNetwork()
    for variable in config['variables']:
        network.add_node(variable)

    for variable, properties in config['variables'].items():
        if "conditional_on" in properties:
            parents = [parent.strip() for parent in properties["conditional_on"].split(",")]
            for parent in parents:
                network.add_edge(parent, variable)

    return network

def define_factors(config):
    """
    Define continuous factors based on the configuration data.
    :param config: Parsed configuration dictionary.
    :return: Dictionary of ContinuousFactor objects keyed by variable name.
    """
    factors = {}
    equations = {}
    for variable, properties in config['variables'].items():
        if properties['type'] == 'continuous':
            if properties['distribution'] == 'normal':
                mean = properties['parameters']['mean']
                std_dev = properties['parameters']['std_dev']
                factors[variable] = ContinuousFactor(
                    variables=[variable],
                    pdf=lambda x, mean=mean, std_dev=std_dev: norm.pdf(x, loc=mean, scale=std_dev)
                )
                equations[variable] = lambda x, mean=mean, std_dev=std_dev: norm.pdf(x, loc=mean, scale=std_dev)
            elif properties['distribution'] == 'conditional':
                # Define conditional distribution based on the specified equation
                equation = properties['equation']
                std_dev = properties.get('std_dev', 1)
                cond_on = [i.strip() for i in properties['conditional_on'].split(",")]

                # Create the PDF function for the conditional factor
                def make_conditional_pdf(equation, std_dev):
                    return lambda x, **inputs: norm.pdf(x, loc=eval(equation, {**inputs, **locals()}), scale=std_dev)

                factors[variable] = ContinuousFactor(
                    variables=[variable] + cond_on,
                    pdf=make_conditional_pdf(equation, std_dev)
                )
                equations[variable] = equation
        elif properties['type'] == 'discrete':
            # Handle discrete variables if required by clipping bounds
            equation = properties['equation']
            bounds = properties['bounds']
            factors[variable] = lambda **inputs: int(np.clip(eval(equation, {**inputs, **locals()}), bounds[0], bounds[1]))

    return factors, equations

def add_factors_to_network(network, factors):
    """
    Add factors to the Bayesian Network.
    :param network: Bayesian Network instance.
    :param factors: Dictionary of ContinuousFactor objects keyed by variable name.
    """
    for variable, factor in factors.items():
        network.add_cpds(factor)

def validate_network(network):
    """
    Validates the Bayesian Network model.
    :param network: Bayesian Network instance.
    """
    try:
        network.check_model()
        print("Digital twin Bayesian network created successfully with dynamic factors.")
    except ValueError as e:
        print(f"Error in the Bayesian network model: {e}")

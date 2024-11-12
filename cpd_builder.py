from models import Variable, CPD
from pgmpy.factors.discrete import TabularCPD
from pgmpy.factors.continuous import LinearGaussianCPD

class CPDBuilder:
    def __init__(self, variables):
        self.variables = variables

    def build_all_cpds(self):
        cpds = {}
        for variable in self.variables:
            cpds[variable.name] = self.build_cpd(variable)
        return cpds

    def build_cpd(self, variable: Variable):
        if variable.distribution == "Gaussian":
            # Handle Gaussian distribution for continuous variables
            mean = variable.parameters.get('mean', 0)
            std_dev = variable.parameters.get('std_dev', 1)
            cpd = LinearGaussianCPD(variable.name, [mean], std_dev)
            print(f"variable is {variable} with cpd : {cpd}")
            return cpd

        elif variable.distribution == "Tabular":
            # Handle Tabular distribution (discrete variables)
            if not variable.cpd or not variable.cpd.parents:
                raise ValueError(f"Missing parents or relationships for TabularCPD in variable: {variable.name}")

            # Collect the relationships for each parent and apply them
            parent_relationships = []
            for parent in variable.cpd.parents:
                relationship_type = parent.relationship_type
                coefficients = parent.coefficients

                if relationship_type == "linear":
                    intercept = coefficients.get("intercept", 0)
                    slope = coefficients.get("slope", 0)
                    parent_relationships.append((parent.name, intercept, slope))
                elif relationship_type == "exponential":
                    a = coefficients.get("a", 1)
                    b = coefficients.get("b", 0)
                    parent_relationships.append((parent.name, a, b))
                else:
                    raise ValueError(f"Unsupported relationship type: {relationship_type}")

            # Create the TabularCPD with the number of possible states (cardinality)
            values = variable.parameters.get('values', [])

            # Returning the TabularCPD (assuming values are the state names)
            return TabularCPD(variable.name, len(values), [values])

        else:
            print(f"Unsupported distribution type: {variable.distribution}")
            return

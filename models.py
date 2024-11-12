from typing import List, Dict, Union, Optional
from pydantic import BaseModel, Field, root_validator, validator

# Represents a parent variable and its relationship with the current variable
class ParentRelationship(BaseModel):
    name: str
    relationship_type: str
    coefficients: Dict[str, Union[float, List[float]]]  # Allow both dict and list for coefficients

# Represents the conditional probability distribution (CPD) for a variable
class CPD(BaseModel):
    parents: List[ParentRelationship]
    values: Optional[List[str]] = None  # Values only used for discrete distributions

# Represents a variable, including its distribution, parameters, and CPD
class Variable(BaseModel):
    name: str
    type: str
    distribution: str
    parameters: Dict[str, Union[float, List[float]]]  # Allow both float and list of floats in parameters
    cpd: Optional[CPD] = None

    @validator("cpd", pre=True, always=True)
    def validate_cpd(cls, v, values):
        # Ensure the relationship type is valid for each parent in CPD
        if v is not None and "parents" in v:
            for parent in v.parents:
                if parent.relationship_type not in ["linear", "exponential"]:
                    raise ValueError(f"Unsupported relationship type: {parent.relationship_type}")
        return v

    @root_validator(pre=True)
    def validate_and_add_cpd(cls, values):
        """ This is a root validator that ensures the CPD is populated if parents are defined. """
        # Check if the variable has parents and handle CPD population
        if "parameters" in values and "parents" in values["parameters"]:
            parents_data = values["parameters"]["parents"]
            parents = [ParentRelationship(**parent) for parent in parents_data]
            values["cpd"] = CPD(parents=parents)

        return values

# Configuration class to hold a list of variables
class Config(BaseModel):
    variables: List[Variable]

    @root_validator(pre=True)
    def populate_cpds(cls, values):
        """
        This is another root validator for the Config class to handle the population of CPDs
        for each variable in the config if it wasn't populated correctly by the Variable model.
        """
        variables = values.get("variables", [])
        for variable in variables:
            # Ensure that if 'parents' are defined, the CPD is populated
            if "parents" in variable and variable.get("cpd", None) is None:
                parents_data = variable["parents"]
                parents = [ParentRelationship(**parent) for parent in parents_data]
                variable["cpd"] = CPD(parents=parents)
        return values


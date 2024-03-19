from typing import Dict, Callable, Union

from handlers.formula import Formula
from handlers.predicate_functions import Predicates


class Specification:
    """
    A class containing all the necessary information for evaluating an MTL formula.
    """

    def __init__(self, formula_info):
        """
        Create a specification from a formula_info dictionary.

        :param formula_info: The formula_info dictionary.
        """
        self._formula_info = formula_info
        self.formula = Formula.from_specification(formula_info)

        self.predicates = {}
        for pred in self._formula_info["predicates_info"]:
            comparison_value = pred.get("predicate_comparison_value", None)
            if str.isnumeric(comparison_value):
                comparison_value = float(comparison_value)
            if comparison_value in ["True", "False"]:
                comparison_value = comparison_value == "True"

            self.predicates[pred["predicate_name"]] = {
                "predicate_logic": pred["predicate_logic"],
                "predicate_comparison_value": comparison_value,
            }
        self.params = self.get_params()

    def get_predicate_logic(self, predicate_name) -> str:
        return self.predicates[predicate_name]["predicate_logic"]

    def set_predicate_logic(self, predicate_name, predicate_logic) -> None:
        self.predicates[predicate_name]["predicate_logic"] = predicate_logic

    def get_predicate_comparison_value(self, predicate_name) -> Union[float, bool, str]:
        return self.predicates[predicate_name]["predicate_comparison_value"]

    def set_predicate_comparison_value(self, predicate_name, predicate_comparison_value) -> None:
        self.predicates[predicate_name]["predicate_comparison_value"] = predicate_comparison_value

    def get_predicate_function(self, predicate_name) -> Callable:
        """
        Get the predicate function for a predicate.
        """
        return Predicates(self.predicates[predicate_name]["predicate_comparison_value"]).__getattribute__(
            self.predicates[predicate_name]["predicate_logic"])

    def get_params_string(self) -> str:
        """
        Create parameter string for the formula.

        Format: "Predicate '<predicate_name>' is set to <predicate_comparison_value>; ..."

        :return: The parameter string.
        """
        params = []
        for pred_name, pred_info in self.predicates.items():
            params.append(f"Predicate '{pred_name}' is set to {pred_info['predicate_comparison_value']}")
        return "; ".join(params)

    def get_params(self) -> Dict[str, Callable]:
        """
        Create parameter string for the formula.

        :return: Mapping from predicate names to predicate functions.
        """
        params = {}
        for pred_name, pred_info in self.predicates.items():
            params[pred_name] = self.get_predicate_function(pred_name)
        return params

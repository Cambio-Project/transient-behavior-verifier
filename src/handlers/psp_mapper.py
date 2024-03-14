import re
from numpy import mat
from soupsieve import match
from handlers.psp_patterns import *


class PSPMapper:
    """A class responsible for the mapping of PSPs to past-MTL formulas"""

    def __init__(self, formula=None, formula_params=None, source_pattern=None):
        self._formula = formula
        self._formula_params = formula_params or {}
        self.source_pattern = source_pattern

    def get_formula(self):
        return self._formula.format(**self._formula_params)

    def get_lower_bound(self):
        return self._formula_params.get("lower_bound")

    def has_lower_bound(self):
        return "lower_bound" in self._formula_params

    def has_upper_bound(self):
        return "upper_bound" in self._formula_params

    def get_upper_bound(self):
        return self._formula_params.get("upper_bound")

    def set_lower_bound(self, lower_bound):
        if not self.has_lower_bound():
            raise Exception("Lower bound not supported by this formula")
        self._formula_params["lower_bound"] = lower_bound

    def set_upper_bound(self, upper_bound):
        if not self.has_upper_bound():
            raise Exception("Upper bound not supported by this formula")
        self._formula_params["upper_bound"] = upper_bound

    @staticmethod
    def map_pattern(input_pattern):
        return PSPMapper.from_psp(input_pattern).get_formula()

    @staticmethod
    def extract_list_predicates(input_pattern):
        """
        Extracts the list of predicates from the input pattern

        :return: the list of predicates
        """
        list_predicates = re.findall('\{\S+\}|\{.+\}|\d+', input_pattern)
        list_predicates_cleaned = []
        for item in list_predicates:
            item = item.replace("{", "")
            item = item.replace("}", "")
            list_predicates_cleaned.append(item)
        list_predicates = list_predicates_cleaned
        return list_predicates

    @staticmethod
    def from_psp(input_pattern) -> "PSPMapper":
        """
        maps a pattern regex to the past-MTL formula

        :return: the past-MTL formula
        """
        list_predicates = PSPMapper.extract_list_predicates(input_pattern)

        if re.match(absence_after_q, input_pattern):
            formula = "always((once({pred1})) -> ((not {pred2}) since {pred1}))"
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
            }

        elif re.match(bounded_absence_after_q, input_pattern):
            formula = "always((once[0,{upper_bound}]({pred1})) -> ((not {pred2}) since {pred1}))"
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
                "upper_bound": list_predicates[2],
            }

        elif re.match(absence_before_r, input_pattern):
            formula = "always({pred1}->(always(not {pred2})))"
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
            }

        elif re.match(bounded_absence_before_r, input_pattern):
            formula = "always({pred1}->(always[0,{upper_bound}](not {pred2})))"
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
                "upper_bound": list_predicates[2],
            }

        elif re.match(absence_between_q_and_r, input_pattern):
            formula = "always({pred2} && not({pred1}) && once ({pred1}))->((not {pred3}) since {pred1})"
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
                "pred3": list_predicates[2],
            }

        elif re.match(bounded_absence_between_q_and_r, input_pattern):
            formula = (
                "always({pred2} && !{pred1} && once {pred1})"
                "->((not {pred3}) since[{lower_bound},{upper_bound}] {pred1})"
            )
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
                "pred3": list_predicates[2],
                "lower_bound": list_predicates[3],
                "upper_bound": list_predicates[4],
            }

        elif re.match(universality_after_q, input_pattern):
            formula = "always((once({pred1})) -> ({pred2} since {pred1}))"
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
            }

        elif re.match(bounded_universality_after_q, input_pattern):
            formula = "always((once[0,{upper_bound}]({pred1})) -> ({pred2} since {pred1}))"
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
                "upper_bound": list_predicates[2],
            }

        elif re.match(universality_before_r, input_pattern):
            formula = "always({pred1}->(always({pred2})))"
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
            }

        elif re.match(bounded_universality_before_r, input_pattern):
            formula = "always({pred1}->(always[0,{upper_bound}]({pred2})))"
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
                "upper_bound": list_predicates[2],
            }

        elif re.match(bounded_universality_between_q_and_r, input_pattern):
            formula = (
                "always({pred2} && !{pred1} && once {pred1})"
                "->({pred3} since[{lower_bound},{upper_bound}] {pred1})"
            )
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
                "pred3": list_predicates[2],
                "lower_bound": list_predicates[3],
                "upper_bound": list_predicates[4],
            }

        elif re.match(bounded_recurrence_globally, input_pattern):
            formula = "always(once[0,{upper_bound}]({pred1}))"
            formula_params = {
                "pred1": list_predicates[0],
                "upper_bound": list_predicates[1],
            }

        elif re.match(bounded_recurrence_between_q_and_r, input_pattern):
            formula = (
                "always(({pred2} && !{pred1} && once {pred1})"
                "-> ((once[0,{upper_bound}]({pred3} or {pred1})) since {pred1}))"
            )
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
                "pred3": list_predicates[2],
                "upper_bound": list_predicates[3],
            }

        elif re.match(bounded_response_globally, input_pattern):
            formula = (
                "always(({pred2} -> once[{lower_bound},{upper_bound}] {pred1})"
                " and not( not({pred2}) since[{upper_bound},inf] {pred1}))"
            )
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
                "lower_bound": list_predicates[2],
                "upper_bound": list_predicates[3],
            }

        elif re.match(bounded_response_between_q_and_r, input_pattern):
            formula = (
                "always(({pred2} && !{pred1} && once {pred1}) -> ( (({pred4} -> once[{lower_bound},{upper_bound}] "
                "{pred3}) and not( not({pred4}) since[{upper_bound},inf] {pred3})) since {pred1}))"
            )
            formula_params = {
                "pred1": list_predicates[0],
                "pred2": list_predicates[1],
                "pred3": list_predicates[2],
                "pred4": list_predicates[3],
                "lower_bound": list_predicates[4],
                "upper_bound": list_predicates[5],
            }

        else:
            raise Exception("PSP pattern could not be matched!")

        return PSPMapper(formula, formula_params, input_pattern)

from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional, Any

import numpy as np

from mtl_evaluation.mtl_evaluator import MTLEvaluator
from handlers.specification import Specification


@dataclass
class Interval:
    __slots__ = ['lower', 'upper']
    lower: Optional[int]
    upper: Optional[int]

    def base1_index(self):
        return Interval(
            lower=self.lower if self.lower is not None else None,
            upper=self.upper if self.upper is not None else None
        )


class MTLPredicateRefiner:
    """
    A class responsible for refining the predicate specification.

    :param formula_info: The formula information.
    :param points_names: The predicate names.
    :param data: The data as multidimensional array.
    """

    def __init__(self, formula_info: Dict, points_names: List[str], data: List):
        self._specification: Specification = Specification(formula_info)
        self._data: List = data
        self._points_names: List[str] = points_names

    def refine_predicate(self, predicate_name, metric_name,) -> Tuple[Tuple[int, int, int], List[bool]]:
        """
        Refines the predicate specification for a given metric.

        If the use_formula parameter is set to False, the predicate is refined
        as if the mtl formula was set to <predicate_name>(<metric_name), but using
        numpy vectorized operations. This is useful for performance reasons when
        the formula is not needed to refine the predicate.

        :param predicate_name: The predicate name.
        :param metric_name: The metric name.
        :return: Evaluated interval (min, max, step) and the result of the refinement.
        """
        if predicate_name not in self._specification.predicates:
            raise ValueError(f"Predicate '{predicate_name}' not found in the specification.")

        values = self._data[self._points_names.index(metric_name)]
        values = np.array(values, dtype=float)
        values[values == np.nan] = 0

        # min and max values for the metric, with a 10% margin
        min_value = max(np.min(values) - np.min(values) / 10, 0)
        max_value = np.max(values) + np.max(values) / 10

        # choose step value so that the number of iterations is limited to 100
        step = (max_value - min_value) / 100

        if max_value > 1:
            # round values to the nearest multiple of 5
            min_value = int(min_value - (min_value % 5))
            max_value = int(max_value + (5 - (max_value % 5)))
            step = int(max(1, step))  # step should be at least 1
            _range = np.arange(min_value, max_value, step)
        else:
            # round min, max and step to 5 decimal places for return
            min_value = np.round(min_value, 5)
            max_value = np.round(max_value, 5)
            step = np.round(step, 5)
            # create range and round to 5 decimal places for iteration
            _range = np.arange(min_value, max_value, step)
            _range = _range.round(5)

        result = []
        for i in _range:
            self._specification.set_predicate_comparison_value(predicate_name, i)
            evaluator = MTLEvaluator(self._specification)
            mtl_result, _ = evaluator.evaluate(self._points_names, self._data, create_plots=False)
            result.append(bool(mtl_result[-1]))

        return (min_value, max_value, step), result


class MTLTimeRefiner:
    """
    A class responsible for refining the timebound of the transient behavior specification.

    :param formula_info: The formula information.
    :param points_names: The predicate names.
    :param data: The data as multidimensional array.
    """

    def __init__(self, formula_info: Dict, points_names: List[str], data: List):
        self._specification: Specification = Specification(formula_info)
        self._is_two_sided_search: bool = (
                self._specification.formula.has_lower_bound()
                and self._specification.formula.has_upper_bound()
        )
        self._data: List = data
        self._max_index: int = len(self._data[0]) - 1
        self._points_names: List[str] = points_names
        if self._is_two_sided_search:
            self._refined_bounds: Interval = Interval(lower=-1, upper=-1)
        else:
            self._refined_bounds: Interval = Interval(lower=None, upper=-1)

    def refine_timebound(self) -> Dict[str, str]:
        """
        Refines the timebound of the transient behavior specification.

        :return: Lower and upper bounds of when the transient behavior specification is satisfied.
        """
        if not (self._specification.formula.has_lower_bound() or self._specification.formula.has_upper_bound()):
            return {'result': 'false', 'intervals': [], 'lower_bound': None, 'upper_bound': None}

        current_bounds = Interval(
            lower=0,
            upper=self._max_index if self._is_two_sided_search else 0
        )

        success = False
        while not success and (current_bounds.lower <= self._max_index and current_bounds.upper <= self._max_index):
            self._update_bounds(current_bounds)
            is_satisfied, _ = self._evaluate_formula()

            if self._is_two_sided_search:
                success = self._refine_bounds_two_sided(is_satisfied, current_bounds)
            else:
                success = self._refine_bounds_one_sided(is_satisfied, current_bounds)

        if success:
            self._update_bounds(self._refined_bounds)
            is_satisfied, interval = self._evaluate_formula()
        else:  # no interval found
            is_satisfied = False
            interval = []

        result = {
            'result': str(is_satisfied),
            'intervals': interval,
            'lower_bound': self._refined_bounds.base1_index().lower,
            'upper_bound': self._refined_bounds.base1_index().upper,
        }
        return result

    def _refine_bounds_two_sided(self, is_satisfied: bool, current_bounds: Interval):
        """
        Refines the timebound of the transient behavior specification for a two-sided search.
        Determines the lower and upper bounds of when the transient behavior specification is satisfied.

        :param is_satisfied: Whether the formula is satisfied with the current bounds.
        :param current_bounds: The current bounds to be refined.
        :return: Whether the timebound has been refined.
        """
        if self._refined_bounds.lower < 0:
            if not is_satisfied and not current_bounds.lower == 0:
                # found lower bound if the formula is not satisfied and the previous one was
                current_bounds.lower = current_bounds.lower - 1
                self._refined_bounds.lower = current_bounds.upper = current_bounds.lower
            else:
                current_bounds.lower += 1

        elif self._refined_bounds.upper < 0:
            if is_satisfied:
                # found upper bound if the formula is satisfied and the previous one was not
                self._refined_bounds.upper = current_bounds.upper
                return True
            else:
                current_bounds.upper += 1
        return False

    def _refine_bounds_one_sided(self, is_satisfied: bool, current_bounds: Interval):
        """
        Refines the timebound of the transient behavior specification for a one-sided search.
        Determines upper bound until which the transient behavior specification is satisfied.

        :param is_satisfied: Whether the formula is satisfied with the current bounds.
        :param current_bounds: The current bounds to be refined.
        :return: Whether the timebound has been refined.
        """
        if self._refined_bounds.upper < 0:
            if not is_satisfied and not current_bounds.upper == 0:
                self._refined_bounds.upper = current_bounds.upper - 1
                return True
            elif current_bounds.upper == self._max_index:
                self._refined_bounds.upper = self._max_index
                return True
            else:
                current_bounds.upper += 1
        return False

    def _update_bounds(self, bounds: Interval):
        """
        Updates the lower and upper bounds of the transient behavior specification.

        :param bounds: New bounds of specification.
        :return: None
        """
        if self._specification.formula.has_lower_bound():
            self._specification.formula.set_lower_bound(bounds.lower)
        if self._specification.formula.has_upper_bound():
            self._specification.formula.set_upper_bound(bounds.upper)

    def _evaluate_formula(self) -> Tuple[bool, List]:
        """
        Evaluates the formula.

        :return: Whether the formula is satisfied and the interval.
        """
        evaluator = MTLEvaluator(self._specification)
        mtl_result, interval = evaluator.evaluate(self._points_names, self._data, create_plots=False)
        return mtl_result[-1], interval

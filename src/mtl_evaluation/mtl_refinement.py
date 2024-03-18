from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
from mtl_evaluation.mtl_evaluator import MTLEvaluator
from handlers.formula_handler import FormulaHandler
from handlers.psp_mapper import PSPMapper


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


class MTLRefiner:
    """
    A class responsible for refining the timebound of the transient behavior specification.

    :param formula_info: The formula information.
    :param points_names: The predicate names.
    :param data: The data as multidimensional array.
    """

    def __init__(self, formula_info: Dict, points_names: List[str], data: List):
        self._mapper: PSPMapper = PSPMapper.from_psp(formula_info['specification'])
        self._params_string: str = FormulaHandler().get_params_string(formula_info)
        self._is_two_sided_search: bool = self._mapper.has_lower_bound() and self._mapper.has_upper_bound()
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
        if not (self._mapper.get_lower_bound() or self._mapper.get_upper_bound()):
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
        if self._mapper.has_lower_bound():
            self._mapper.set_lower_bound(bounds.lower)
        if self._mapper.has_upper_bound():
            self._mapper.set_upper_bound(bounds.upper)

    def _evaluate_formula(self) -> Tuple[bool, List]:
        """
        Evaluates the formula.

        :return: Whether the formula is satisfied and the interval.
        """
        evaluator = MTLEvaluator(self._mapper.get_formula(), self._params_string)
        mtl_result, interval = evaluator.evaluate(self._points_names, self._data, create_plots=False)
        return mtl_result[-1], interval

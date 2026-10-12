import re

from monitors import mtl
from handlers.specification import Specification
from mtl_evaluation.mtl_plotter import MTLPlotter
import numpy as np


class MTLEvaluator:
    """A class responsible for the execution of the formula verification"""

    def __init__(self, specification: Specification):
        self.specification = specification
        self.formula = self.specification.formula.to_string()
        self.params = self.specification.get_params()

    def _post_process_intervals(self, intervals, value_assignments):
        """
        Post process the intervals and add the predicate values to the log string.

        :param intervals: The intervals to post process.
        :param value_assignments: The value assignments for each metric over time.
        :return: The post processed intervals.
        """
        predicate_values_string = self.specification.get_params_string()
        for i, row in enumerate(intervals):
            mtl_result = bool(row[2])
            if not mtl_result:
                log_str = f"{predicate_values_string} Input measurements: {value_assignments[row[0]]} at time {row[0]};"
                row = (row[0], row[1], mtl_result, log_str)
            else:
                row = (row[0], row[1], mtl_result)
            intervals[i] = row
        return intervals

    @staticmethod
    def _sanitize_identifier(name: str) -> str:
        """Convert a data source name into a valid MTL variable identifier."""
        sanitized = re.sub(r"\W", "_", str(name).strip())
        sanitized = re.sub(r"_+", "_", sanitized)
        if not sanitized:
            sanitized = "metric"
        if sanitized[0].isdigit():
            sanitized = f"metric_{sanitized}"
        return sanitized

    @classmethod
    def _build_safe_point_name_mapping(cls, points_names):
        mapping = {}
        used_names = set()
        for point_name in points_names:
            base_name = cls._sanitize_identifier(point_name)
            sanitized_name = base_name
            suffix = 1
            while sanitized_name in used_names:
                sanitized_name = f"{base_name}_{suffix}"
                suffix += 1
            used_names.add(sanitized_name)
            mapping[point_name] = sanitized_name
        return mapping

    @classmethod
    def _sanitize_formula(cls, formula: str, points_names):
        """Replace metric names containing dots or other illegal chars with safe identifiers."""
        mapping = cls._build_safe_point_name_mapping(points_names)
        sanitized_formula = formula
        for original_name, sanitized_name in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
            sanitized_formula = sanitized_formula.replace(original_name, sanitized_name)
        return sanitized_formula

    def evaluate(self, points_names, data_array, reverse=False, create_plots: bool = True):
        # my_mtl_monitor = mtl.monitor(self.formula, **self.params)
        # data = np.array(data_array, dtype=float)
        # data[data == np.nan] = 0

        point_name_mapping = self._build_safe_point_name_mapping(points_names)
        safe_point_names = list(point_name_mapping.values())
        sanitized_formula = self._sanitize_formula(self.formula, points_names)
        my_mtl_monitor = mtl.monitor(sanitized_formula, **self.params)

        data = np.array(data_array, dtype=float)
        data[np.isnan(data)] = 0

        # list of value assignments for each metric over time:
        # [{'x': 1, 'y': 2, 'z': 3}, {'x': 2, 'y': 3, 'z': 4}, ...]
        # value_assignments = [dict(zip(points_names, row)) for row in data.T]
        value_assignments = [dict(zip(safe_point_names, row)) for row in data.T]
        mtl_eval_output = [my_mtl_monitor.update(**assignment) for assignment in value_assignments]

        plotter = MTLPlotter(mtl_eval_output, points_names, data_array, [], reverse)
        if create_plots:
            intervals = plotter.create_plot()
        else:
            intervals = plotter.create_intervals()

        intervals = self._post_process_intervals(intervals, value_assignments)

        return mtl_eval_output, intervals

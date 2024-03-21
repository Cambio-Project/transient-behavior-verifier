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

    def evaluate(self, points_names, data_array, reverse=False, create_plots: bool = True):
        my_mtl_monitor = mtl.monitor(self.formula, **self.params)

        data = np.array(data_array, dtype=float)
        data[data == np.nan] = 0

        # list of value assignments for each metric over time:
        # [{'x': 1, 'y': 2, 'z': 3}, {'x': 2, 'y': 3, 'z': 4}, ...]
        value_assignments = [dict(zip(points_names, row)) for row in data.T]
        mtl_eval_output = [my_mtl_monitor.update(**assignment) for assignment in value_assignments]

        plotter = MTLPlotter(mtl_eval_output, points_names, data_array, [], reverse)
        if create_plots:
            intervals = plotter.create_plot()
        else:
            intervals = plotter.create_intervals()

        intervals = self._post_process_intervals(intervals, value_assignments)

        return mtl_eval_output, intervals

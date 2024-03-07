from monitors import mtl
from handlers import predicate_functions
from mtl_evaluation.mtl_plotter import MTLPlotter
import numpy as np
import re


class MTLEvaluator:
    """A class responsible for the execution of the formula verification"""

    def __init__(self, formula, params_string):
        self.formula = formula
        self.params_string = params_string

    def _create_monitor(self):
        """
        Create a monitor object with the formula and the parameters.

        :return: MTL monitor object.
        """
        def save_eval(x):
            """ Evaluate only in predefined context """
            return eval(x, {}, {"predicate_functions": predicate_functions})

        params_dict = dict(param.split('=') for param in self.params_string.split(','))
        params_dict = {key: save_eval(value) for key, value in params_dict.items()}
        return mtl.monitor(self.formula, **params_dict)

    def _create_predicate_string(self) -> str:
        """
        Read the params_string and create a string with the predicate names and their values.

        :return: The predicate values string.
        """
        predicate_values_string = ''
        predicate_comparison_values = self.params_string.split(',')
        for predicate in predicate_comparison_values:
            pred_name, pred_func = predicate.split('=')
            if not ('boolean' in pred_func or 'trend' in pred_func):
                predicate_values = re.findall(r'\(\S+\)', pred_func)
                predicate_values_string += f"Predicate '{pred_name}' is set to {''.join(predicate_values)}; "
        return predicate_values_string

    def _post_process_intervals(self, intervals, value_assignments):
        """
        Post process the intervals and add the predicate values to the log string.

        :param intervals: The intervals to post process.
        :param value_assignments: The value assignments for each metric over time.
        :return: The post processed intervals.
        """
        predicate_values_string = self._create_predicate_string()
        for i, row in enumerate(intervals):
            mtl_result = bool(row[2])
            if not mtl_result:
                log_str = f"{predicate_values_string} Input measurements: {value_assignments[row[0]]} at time {row[0]};"
                row = (row[0], row[1], mtl_result, log_str)
            else:
                row = (row[0], row[1], mtl_result)
            intervals[i] = row
        return intervals

    def evaluate(self, points_names, data_array, reverse=False):
        my_mtl_monitor = self._create_monitor()

        data = np.array(data_array, dtype=float)
        data[data == np.nan] = 0

        # list of value assignments for each metric over time:
        # [{'x': 1, 'y': 2, 'z': 3}, {'x': 2, 'y': 3, 'z': 4}, ...]
        value_assignments = [dict(zip(points_names, row)) for row in data.T]
        mtl_eval_output = [my_mtl_monitor.update(**assignment) for assignment in value_assignments]

        intervals = MTLPlotter(mtl_eval_output, points_names, data_array, [], reverse).create_plot()
        intervals = self._post_process_intervals(intervals, value_assignments)

        return mtl_eval_output, intervals

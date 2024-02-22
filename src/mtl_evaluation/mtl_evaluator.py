from monitors import mtl
from handlers import predicate_functions
from mtl_evaluation.mtl_plotter import MTLPlotter
import matplotlib.pyplot as plt
import numpy as np
import re


class MTLEvaluator():
    """A class responsible for the execution of the formula verification"""

    # executes the verification
    def evaluate(self, formula, params_string, points_names, data_array, reverse=False):

        # creates empty result log file
        # with open("result_log.txt", 'w') as f:
        #     pass

        mtl_eval_output = []
        predicate_comparison_values = params_string.split(',')
        predicate_values_string = ''
        for predicate in predicate_comparison_values:
            predicate_info = predicate.split('=')
            if('boolean' not in predicate_info[1] and 'trend' not in predicate_info[1]):
                predicate_values = re.findall('\(\S+\)', predicate_info[1])
                predicate_values_string = predicate_values_string+"Predicate '" + \
                    predicate_info[0]+"' is set to " + \
                    ''.join(predicate_values)+'; '

        # for debugging purposes you can use the additional print_source_code parameter
        # to print the code of the sequential network and the update rules
        # my_mtl_monitor = eval(
        #     "mtl.monitor("+'"'+formula+"\","+params_string+",print_source_code=True)")

        my_mtl_monitor = eval(
            "mtl.monitor("+'"'+formula+"\","+params_string+")")


        predicate_input_values = []
        for j in range(len(data_array[0])):
            eval_string = "my_mtl_monitor.update("
            for i in range(len(data_array)):

                if i == len(data_array)-1:

                    if(str(data_array[i][j]) == "NaN"):
                        data_array[i][j] = 0
                    eval_string = eval_string + \
                        points_names[i]+"="+str(data_array[i][j])
                else:
                    if(str(data_array[i][j]) == "NaN"):
                        data_array[i][j] = 0
                    eval_string = eval_string + \
                        points_names[i]+"="+str(data_array[i][j])+","

            predicate_input_values.append(eval_string.replace(
                "my_mtl_monitor.update", "")+")")

            eval_string = eval_string+")"
            output = eval(eval_string)
            #print(my_mtl_monitor.time, output,
            #      my_mtl_monitor.states, predicate_input_values[-1])
            mtl_eval_output.append(output)

            # with open("result_log.txt", "a") as external_file:
            #     add_text = my_mtl_monitor.time, output, my_mtl_monitor.states, predicate_input_values[-1]
            #     print(add_text, file=external_file)
            #     external_file.close()

        intervals = MTLPlotter(mtl_eval_output, points_names,
                               data_array, predicate_input_values, reverse).create_plot()

        for i in range(len(intervals)):
            if intervals[i][2] == False:
                intervals[i] = (intervals[i][0], intervals[i][1], intervals[i][2],
                                predicate_values_string+" Input measurements: "+predicate_input_values[intervals[i][0]]+' at time ' + str(intervals[i][0]) + ';')

        return mtl_eval_output, intervals

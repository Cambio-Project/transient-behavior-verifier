from cProfile import label
import random
from matplotlib import colors
import matplotlib.pyplot as plt
import numpy as np


class MTLPlotter():
    """A class responsible for the plotting of the results"""

    def __init__(self,  mtl_results, points_names, data_array, predicate_values, reverse=False):
        self.mtl_results = mtl_results
        self.point_names = points_names
        self.data_array = data_array
        self.predicate_values = predicate_values
        self.colors = ['blue', 'red', 'purple', 'black', 'maroon']
        self.reverse = reverse

    def return_last_result(self):
        return str(self.mtl_results[-1])

    def create_plot(self):

        #y_offset = 1.10

        #fig, ax = plt.subplots()

        #if self.reverse:
        #    plt.xlabel('reversed time (future-MTL converted)')

        #else:
        #    plt.xlabel('time')

        #for i in range(len(self.data_array)):
        #    if i == 0:
        #        color = random.choice(self.colors)
        #        self.colors.remove(color)
        #        data_converted = [float(x) for x in self.data_array[i]]
        #        plt.plot(data_converted, c=color,
        #                 label=self.point_names[i])
        #        ax.tick_params('y', colors=color)
        #        ax.set_ylabel(self.point_names[i], color=color)

        #    if i == 1:
        #        color = random.choice(self.colors)
        #        self.colors.remove(color)
        #        ax2 = ax.twinx()
        #        data_converted = [float(x) for x in self.data_array[i]]
        #        plt.plot(data_converted, c=color,
        #                 label=self.point_names[i])
        #        ax2.tick_params('y', colors=color)
        #        ax2.set_ylabel(self.point_names[i], color=color)
        #    if i >= 2:
        #        color = random.choice(self.colors)
        #        self.colors.remove(color)
        #        ax3 = ax.twinx()
        #        ax3.spines.right.set_position(("axes", y_offset))
        #        data_converted = [float(x) for x in self.data_array[i]]
        #        plt.plot(data_converted, c=color,
        #                 label=self.point_names[i])
        #        ax3.tick_params('y', colors=color)
        #        ax3.set_ylabel(self.point_names[i], color=color)
        #        y_offset = y_offset+0.1

        intervals = []
        start_interval = 0

        for i in range(1, len(self.mtl_results)):
            if self.mtl_results[i-1] == self.mtl_results[i]:
                pass
            elif self.mtl_results[i-1] != self.mtl_results[i]:
                intervals.append((start_interval, i, self.mtl_results[i-1]))
                start_interval = i
            if i == len(self.mtl_results)-1:
                intervals.append((start_interval, i, self.mtl_results[i]))


        #for item in intervals:
        #    if item[2] == True:
        #        plt.axvspan(item[0], item[1], facecolor='green', alpha=0.25)
        #    else:
        #        plt.axvspan(item[0], item[1], facecolor='red', alpha=0.25)

        # fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
        #           fancybox=True, shadow=True, ncol=2)

        # plt.savefig('static/results.pdf', bbox_inches="tight")
        # plt.show()

        return intervals

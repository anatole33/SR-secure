#!/usr/bin/env python3
import os
import sys
import matplotlib.pyplot as plt
sys.path.append(os.path.relpath("."))
from tools import parse_json_output, check_results, plot_lines_K
import numpy as np
import warnings
warnings.simplefilter("ignore")

nb_runs = 30
# set_random != 0 means that random seed will be chosen classicaly, using time
# set_random == 0 means that random seed is fixed to 1 each time an algo is executed nb_runs times
set_random = 1
algos = ["SR", "SR_S1", "SR_S2"]
algos_names = ["SR", "SR-R", "SR-C"]

######### Experiment on real world data
# Directory must already exist and scenarios must be defined
scenarios = ["Jester-small", "Jester-large"]
DIR_EXP = "experiment_real_data/"

N = 100000

aggregates_time = dict()
for algo in algos:
        aggregates_time[algo] = list()

for scenario in scenarios:
        input_file = DIR_EXP + "data_" + scenario + ".txt"
        aggregates_all = dict()
        R_list = dict()
        for algo in algos:
                print ("*" * 10 + " Scenario=", scenario, "N=", N, "algo=", algo)
                output_file = DIR_EXP + scenario + "_N_" + str(N) + "_" + algo + ".txt"
                #os.system("python3 " + algo + ".py " + str(nb_runs) + " " + str(N) + " " + input_file + " " + output_file + " " + str(set_random))
                R_list[algo], aggregate_time, aggregates_all[algo] = parse_json_output(output_file)
                aggregates_time[algo].append(aggregate_time)            
        # check that all algorithms output the same result if the random seed is fixed
        if set_random == 0:
                check_results(R_list, algos)


# plot bars
plt.figure(figsize=(10, 6))
plt.rcParams.update({'font.size':14})
x = np.arange(len(scenarios))  # the label locations
plt.xticks(x, scenarios)
width = 0.5  # the width of the bars
plt.bar(x - width/3, aggregates_time["SR"], width/3, color='paleturquoise', edgecolor='black')
plt.bar(x , aggregates_time["SR_S1"], width/3, color='royalblue', edgecolor='black')
plt.bar(x + width/3, aggregates_time["SR_S2"], width/3, color='deepskyblue', edgecolor='black')
plt.ylabel('Time (seconds)')
plt.legend(algos_names, bbox_to_anchor=(0.3, 0.9), ncol=1)
plt.savefig(DIR_EXP + "plot_jester.pdf")


nb_runs = 5
scenarios = ["MovieLens"]
algos = ["SR", "SR_S1", "SR_S2", "SR_SP"]
algos_names = ["SR", "SR-R", "SR-C", "SR-P"]
aggregates_time = dict()
for algo in algos:
        aggregates_time[algo] = list()

for scenario in scenarios:
        input_file = DIR_EXP + "data_" + scenario + ".txt"
        aggregates_all = dict()
        R_list = dict()
        for algo in algos:
                print ("*" * 10 + " Scenario=", scenario, "N=", N, "algo=", algo)
                output_file = DIR_EXP + scenario + "_N_" + str(N) + "_" + algo + ".txt"
                #os.system("python3 " + algo + ".py " + str(nb_runs) + " " + str(N) + " " + input_file + " " + output_file + " " + str(set_random))
                R_list[algo], aggregate_time, aggregates_all[algo] = parse_json_output(output_file)
                aggregates_time[algo].append(aggregate_time)            
        # check that all algorithms output the same result if the random seed is fixed
        if set_random == 0:
                check_results(R_list, algos)
# plot bars
plt.figure(figsize=(8, 5))
plt.rcParams.update({'font.size':14})

x = np.arange(len(scenarios))  # the label locations
plt.xticks(x, scenarios)
width = 0.5  # the width of the bars
plt.bar(x - width/2, aggregates_time["SR"], width/3, color='paleturquoise', edgecolor='black')
plt.bar(x - width/6, aggregates_time["SR_S1"], width/3, color='royalblue', edgecolor='black')
plt.bar(x + width/6, aggregates_time["SR_S2"], width/3, color='deepskyblue', edgecolor='black')
plt.bar(x + width/2, aggregates_time["SR_SP"], width/3, color='blue', edgecolor='black')
plt.yscale('log')
plt.ylabel('Time (seconds)')
plt.legend(algos_names, bbox_to_anchor=(0.3, 0.9), ncol=1)
plt.savefig(DIR_EXP + "plot_movie.pdf")

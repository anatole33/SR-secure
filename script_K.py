#!/usr/bin/env python3
import os
import sys
import matplotlib.pyplot as plt
sys.path.append(os.path.relpath("."))
from tools import parse_json_output, check_results, plot_lines_K
import warnings
warnings.simplefilter("ignore")

nb_runs = 30
# set_random != 0 means that random seed will be chosen classicaly, using time
# set_random == 0 means that random seed is fixed to 1 each time an algo is executed nb_runs times
set_random = 1
algos = ["SR", "SR_1", "SR_2", "SR_S1", "SR_S2"]
algos_names = ["SR", "SR-Ring'", "SR-Centralized'", "SR-Ring", "SR-Centralized"]


######### Experiment 2: Vary K for fixed N and random_mode = 1 (bernoulli)
K_vals = [100, 200, 300, 400]
N = 100000
DIR_EXP2 = "experiment_K/"
os.system("mkdir -p " + DIR_EXP2)

aggregates_time = dict()
for algo in algos:
        aggregates_time[algo] = list()
aggregates_all = dict()
for K in K_vals:
        scenario = "_K_" + str(K)
        input_file = DIR_EXP2 + "scenario" + scenario + ".txt"
        f = open(input_file, "w")
        f.write(str(K) + "\n1" + "\n0.9" + "\n0.8" * (K-1))
        f.close()
        R_list = dict()
        for algo in algos:
                print ("*" * 10 + " Scenario", scenario, "N=", N, "algo=", algo)
                output_file = DIR_EXP2 + "scenario" + scenario + "_N_" + str(N) + "_" + algo + ".txt"
                #os.system("python3 " + algo + ".py " + str(nb_runs) + " " + str(N) + " " + input_file + " " + output_file + " " + str(set_random))
                R_list[algo], aggregate_time, aggregates_all[algo] = parse_json_output(output_file)
                aggregates_time[algo].append(aggregate_time)
        # check that all algorithms output the same result if the random seed is fixed
        if set_random == 0:
                check_results(R_list, algos)

# generate plot
plot_lines_K("K_varies", algos, algos_names, "Number of arms K", False, K_vals, aggregates_time, DIR_EXP2)

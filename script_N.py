#!/usr/bin/env python3
import os
import sys
import matplotlib.pyplot as plt
sys.path.append(os.path.relpath("."))
from tools import parse_json_output, check_results, plot_lines_and_pie
import warnings
warnings.simplefilter("ignore")

nb_runs = 30
# set_random != 0 means that random seed will be chosen classicaly, using time
# set_random == 0 means that random seed is fixed to 1 each time an algo is executed nb_runs times
set_random = 1
algos = ["SR", "SR_1", "SR_2", "SR_S1", "SR_S2"]
algos_names = ["SR", "SR-R'", "SR-C'", "SR-R", "SR-C"]

######### Experiment 1: Vary N for fixed K
# Random_mode is defined in each scenario. 1 is uniform in [mu - epsilon, mu + epsilon] and 2 is bernoulli
K = 10
scenarios = ["1", "2"]
N_vals = [100, 1000, 10000, 100000]
DIR_EXP = "experiment_N/"
os.system("mkdir -p " + DIR_EXP)

for scenario in scenarios:
        input_file = DIR_EXP + "scenario" + scenario + ".txt"
        f = open(input_file, "w")
        if scenario == "1":
                f.write(str(K) + "\n0" + "\n5" + "\n28" + "\n28" * (K-1))
        elif scenario == "2":
                f.write(str(K) + "\n1" + "\n0.8" + "\n0.8" * (K-1))
        f.close()
        aggregates_time = dict()
        for algo in algos:
                aggregates_time[algo] = list()
        aggregates_all = dict()
        for N in N_vals:
                R_list = dict()
                for algo in algos:
                        print ("*" * 10 + " Scenario=", scenario, "N=", N, "algo=", algo)
                        output_file = DIR_EXP + "scenario" + scenario + "_N_" + str(N) + "_" + algo + ".txt"
                        #os.system("python3 " + algo + ".py " + str(nb_runs) + " " + str(N) + " " + input_file + " " + output_file + " " + str(set_random))
                        R_list[algo], aggregate_time, aggregates_all[algo] = parse_json_output(output_file)
                        aggregates_time[algo].append(aggregate_time)
                # check that all algorithms output the same result if the random seed is fixed
                if set_random == 0:
                        check_results(R_list, algos)
        # generate plot
        plot_lines_and_pie(scenario, algos, algos_names, "Budget N", True, N_vals, aggregates_time, aggregates_all, "N=" + str(N), DIR_EXP)

#!/usr/bin/env python3
import os
import sys
import matplotlib.pyplot as plt
sys.path.append(os.path.relpath("."))
from tools import parse_json_output, check_results
import warnings
warnings.simplefilter("ignore")

nb_runs = 100
# set_random != 0 means that random seed will be chosen classicaly, using time
# set_random == 0 means that random seed is fixed to 1 each time an algo is executed nb_runs times
set_random = 1
algos = ["SR_Secure_ISPEC", "SR_SP"]

######### Experiment: Vary N and K

# Random_mode is 0, uniform between mu - epsilon and mu + epsilon
N_vals = [25000, 50000, 75000, 100000]
K_vals = [10, 5]

DIR = "experiment_SR_SP/"
os.system("mkdir -p " + DIR)

aggregates_time = dict()
for K in K_vals:
        aggregates_time["SR_SP_" + str(K)] = list()
        aggregates_time["SR_Secure_ISPEC_" + str(K)] = list()
        input_file = DIR + "scenario_K=" + str(K) + ".txt"
        f = open(input_file, "w")
        f.write(str(K) + "\n0" + "\n5" + "\n40" + "\n38" * (K-1))
        f.close()
        aggregates_all = dict()
        for N in N_vals:
                R_list = dict()
                for algo in algos:
                        print ("*" * 10 + " K=", K, "N=", N, "algo=", algo)
                        output_file = DIR + "K_" + str(K) + "_N_" + str(N) + "_" + algo + ".txt"
                        os.system("python3 " + algo + ".py " + str(nb_runs) + " " + str(N) + " " + input_file + " " + output_file + " " + str(set_random))
                        R_list[algo], aggregate_time, aggregates_all[algo] = parse_json_output(output_file)
                        aggregates_time[algo + "_" + str(K)].append(aggregate_time)

# generate plot
algos=[]
algos_names=[]
for K in K_vals:
  algos.append("SR_Secure_ISPEC_" + str(K))
  algos.append("SR_SP_" + str(K))
  algos_names.append("K=" + str(K) + ", SR-Paillier-Old")
  algos_names.append("K=" + str(K) + ", SR-Paillier")

# plot one line for each algorithm
plt.figure(figsize=(8, 4))
plt.rcParams.update({'font.size':14})
ax = plt.subplot(121)
markers = ('x', 'o', '*', '.', '', '', '')
for algo in algos:
        plt.plot(N_vals, aggregates_time[algo], marker=markers[algos.index(algo)], fillstyle='none', markersize=10)
plt.legend(algos_names, bbox_to_anchor=(2.25, 0.75))
plt.xticks(N_vals, N_vals)
plt.xlabel("Budget N")
plt.ylabel('Time (seconds)')
plt.subplots_adjust(top=0.92, bottom=0.2)
plt.savefig(DIR + "plot_lines_SR_P" + ".pdf")
plt.clf()

# pie chart only for some point
my_N = 100000
my_K = 10
input_file = "scenario_K=" + str(my_K) + ".txt"
output_file = DIR + "K_" + str(my_K) + "_N_" + str(my_N) + "_SR_SP.txt"
a, b, aggregates_all["SR_SP"] = parse_json_output(output_file)
plt.figure(figsize=(5, 4))
plt.rcParams.update({'font.size':14})
plt.title("Zoom on SR-Paillier, N=" + str(my_N) + ", K=" + str(my_K))
components = ["time Comp", "time DO", "time BAI"]
time_per_component = [aggregates_all["SR_SP"][component] for component in components]
components = list(map (lambda x: x[5:], components)) # remove "time " from the left of each key
wedges, _ = plt.pie(time_per_component, labels=components, colors=["gray", "pink", "black"], textprops={'fontsize': 18})
for w in wedges:
	w.set_edgecolor("none")
plt.savefig(DIR + "plot_pie_SR_P" + ".pdf")
plt.clf()

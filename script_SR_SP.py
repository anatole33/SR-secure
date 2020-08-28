#!/usr/bin/env python3
import os
import sys
import matplotlib.pyplot as plt
sys.path.append(os.path.relpath("."))
from tools import parse_json_output, check_results
import warnings
warnings.simplefilter("ignore")

def plot_lines_and_pie(algos, algos_names, left_xlabel, left_xlog, left_x, left_data, right_aggregates_all, right_message, OUTPUT_DIR):
        plt.figure(figsize=(12, 4))
        plt.rcParams.update({'font.size':14})

        # left : plot one line for each algorithm
        ax = plt.subplot(121)
        markers = ('x', 'o', '*', '.', '', '', '')
        for algo in algos:
                plt.plot(left_x, left_data[algo], marker=markers[algos.index(algo)], fillstyle='none', markersize=10)
        plt.legend(algos_names, bbox_to_anchor=(1.95, 0.75))

        if left_xlog:
                plt.xscale('log')
                font_size_pie = 14
        else:
                plt.xticks(left_x, left_x)
                font_size_pie = 6
        plt.xlabel(left_xlabel)
        plt.ylabel('Time (seconds)')
        plt.yticks([5,10,15])
        plt.subplots_adjust(top=0.92, bottom=0.05)

        plt.savefig(OUTPUT_DIR + "plot_lines_SR_P" + ".pdf")
        plt.clf()

        # right : pie chart only for some point
        ax = plt.subplot(111)                
        plt.title("Zoom on SR-Paillier for " + right_message)
        components = ["time Comp", "time DO", "time BAI", "time U"]
        time_per_component = [right_aggregates_all["SR_SP"][component] for component in components]
        components = list(map (lambda x: x[5:], components)) # remove "time " from the left of each key

        #colors = ["#FF0033","#2D5DF5","#FFBB22","#1B9978","#5A82F1","#E9953F","#EBD86D","#3BECA4","#1E0968","#2952B0","#2E01A6","#2613DF","#5AC0AB","#1FD9EF","#441A71","#AA64AC","#960DC9","#BF6434","#21C13D","#1A8990","#B75EC4","#CFDE9F","#04350E","#B3CF0A","#E26F5D","#2EFD6E","#BEA469","#3F4696","#F46962","#162FE9","#E26CD6","#6433F1"]
        cm = plt.get_cmap('gist_rainbow')
        NUM_COLORS = len(components) + 1
        colors = []
        for i in range(NUM_COLORS):
                colors.append(cm(1.*i/NUM_COLORS))
        # If time values are too small the pie is not a pie
        time_scaled = [time_per_component[i]*1000 for i in range(len(time_per_component))]

        wedges, _ = ax.pie(time_scaled, labels=components[:-1] + ["DC"], colors=colors, textprops={'fontsize': 18})

        # Sperarate the slices of the pie with black color
        for w in wedges:
                w.set_edgecolor('black')

        plt.subplots_adjust(top=0.92, bottom=0.015)
        
        plt.savefig(OUTPUT_DIR + "plot_pie_SR_P" + ".pdf")
        plt.clf()
        
nb_runs = 30
# set_random != 0 means that random seed will be chosen classicaly, using time
# set_random == 0 means that random seed is fixed to 1 each time an algo is executed nb_runs times
set_random = 1
algos = ["SR_SP", "SR_Secure_ISPEC"]

######### Experiment: Vary N and K

# Random_mode is 0, uniform between mu - epsilon and mu + epsilon
N_vals = [20000, 40000, 60000, 80000, 100000]
K_vals = [5, 10]

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
                        #os.system("python3 " + algo + ".py " + str(nb_runs) + " " + str(N) + " " + input_file + " " + output_file + " " + str(set_random))
                        R_list[algo], aggregate_time, aggregates_all[algo] = parse_json_output(output_file)
                        aggregates_time[algo + "_" + str(K)].append(aggregate_time)

# generate plot
algos = ["SR_SP_" + str(i) for i in K_vals] + ["SR_Secure_ISPEC_" + str(i) for i in K_vals]
algos_names = ["SR-Paillier K = " + str(i) for i in K_vals] + ["SR-Paillier old version K = " + str(i) for i in K_vals]

my_N = 100000
my_K = 10
input_file = "scenario_K=" + str(my_K) + ".txt"
output_file = DIR + "K_" + str(my_K) + "_N_" + str(my_N) + "_SR_SP.txt"
# If you want to run the algo but my_K = 10 then no need to uncomment the next line, the files have already
# been created. It is to avoid ploting the pie with too much nodes R if K_vals takes big values.
#os.system("python3 SR_SP.py" str(nb_runs) + " " + str(my_N) + " " + input_file + " " + output_file + " " + str(set_random))
a, b, aggregates_all["SR_SP"] = parse_json_output(output_file)

plot_lines_and_pie(algos, algos_names, "Budget N", False, N_vals, aggregates_time, aggregates_all, "N=" + str(my_N) + " K=" + str(my_K), DIR)

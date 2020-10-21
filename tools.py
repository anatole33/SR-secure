import random
import sys
import json

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
rng = np.random.RandomState(1)

# Get a random reward
def pull(random_mode, mu):
        if random_mode == 1:
                return int(random.uniform(0, 1) < mu)
        elif random_mode[0] == 0:
                return random.randint(mu - random_mode[1], mu + random_mode[1])

# Return a list of a random permutation over [1,K]
def generate_permutation(K):
        sigma_dict = {}
        for element in range(1, K+1):
                sigma_dict[element] = rng.randint(0, sys.maxsize)
        vals_sorted = sorted(sigma_dict.values())
        sigma = []
        for element in sigma_dict.keys():
                sigma.append(vals_sorted.index(sigma_dict[element]) + 1)
        return sigma

# Convert a byte type list deciphered with AES into an int list
# Usefull when sending a permutation tau, random_mode
# or several elements at once in general.
# Works with a list [] or ()
# Similar to 'split()' function but return a float list
def parser(dec):
        if len(dec) == 1:
                return int(chr(dec[0]))
        res = []
        i = 1
        while dec[i] != 93 and dec[i]!= 41:
                tmp_list = []
                tmp_val = 0
                while dec[i] != 44 and dec[i] != 93 and dec[i] != 41:
                        tmp_list.append(chr(dec[i]))
                        i += 1
                l = len(tmp_list)
                for x in range(l):
                        tmp_val += int(tmp_list[l - x - 1]) * (10**(x))
                res.append(tmp_val)
                if dec[i] == 44:
                        i += 2
        return res

# Use sigma, a permutation of range(1, len(lsum)+1) to define the minimum element
# of a list in case there is an equality. If sigma is randomly chosen,
# then the minimum element is also random (among all minimums)
def argmin(lsum, sigma):
        S_m = lsum[0]
        i_m = 0
        for i in range(1, len(lsum)):
                if lsum[i] < S_m or (lsum[i] == S_m and sigma[i] < sigma[i_m]):
                        S_m = lsum[i]
                        i_m = i
        return i_m

def permute(List, permu):
        K = len(List)
        permu_list = [0] * K
        for i in range(K):
                permu_list[permu[i]-1] = List[i]
        return permu_list

def unpermute(List, permu):
        K = len(List)
        unpermu_list = []
        for i in range(K):
                unpermu_list.append(List[permu[i]-1])
        return unpermu_list

# Use AES-CBC to encrypt data
def e_aes(data, iv, key):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.encrypt(pad(str(data).encode('utf-8'), AES.block_size))

# Decrypt data, a ciphertext of AES-CBC
def d_aes(data, iv, key):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(data), AES.block_size)


# ------------     Plot functions    --------------

# Run the experiment defined in a given file (argv[3]) and write the results
# of nb_runs executions in an other file (argv[4])
def run_experiment(algo):
        nb_runs = int(sys.argv[1])
        N =  int(sys.argv[2])
        K, random_mode, mu = get_mu_from_file(sys.argv[3])
        output_file = sys.argv[4]
        set_random = int(sys.argv[5])
        if set_random == False:
                random.seed(1)

        result = dict()
        for run in range(nb_runs):
                print ("run", run + 1)
                result[run] = algo(N, K, random_mode, mu)

        with open(output_file, 'w') as fp:
                json.dump(result, fp)

# Return K, random_mode and the list of all mu from a file correctly filled
def get_mu_from_file(file_name):
        f = open(file_name, "r")
        K = int(f.readline())
        mode = int(f.readline())
        if mode == 0:
                epsilon = int(f.readline())
                random_mode = (mode, epsilon)
        else:
                random_mode = mode

        mu = dict()
        if mode == 0:
                for i in range(K):
                        mu[i] = int(f.readline())
        elif mode == 1:
                for i in range(K):
                        mu[i] = float(f.readline())

        f.close()
        return (K, random_mode, mu)

# Take as input the file containing 'nb_runs' results of an algorithm
# Returns R_list, a list of best arm and sums of arms computed for each run,
# aggregate_time, the mean computation time, and aggregates, a dictionary of
# mean time of every participant
def parse_json_output(file_name):
        with open(file_name, 'r') as f:
                result = json.load(f)
        nb_runs = len(result)
        R_list = []
        aggregate_time = 0
        aggregates = dict()
        for run in range(nb_runs):
                run = str(run)
                R_list.append(result[run]["arm_max"])
                R_list.append(result[run]["sums"])
                aggregate_time += result[run]["time"]
                if run == '0':  
                        for key, values in result[run].items():
                                if key != "arm_max" and key != "sums" and key != "time":
                                        aggregates[key] = result[run][key]
                else:
                        for key, values in result[run].items():
                                if key != "arm_max" and key != "sums" and key != "time":
                                        aggregates[key] += result[run][key]

        aggregate_time /= nb_runs
        for key in aggregates.keys():
                aggregates[key] /= nb_runs
        return (R_list, aggregate_time, aggregates)

# R_list is a dict() containing 'nb_runs' couples 'best arm, [list of all sums of arms]'
# for all algorithms in algos. It signals an error if the result of two algorithms
# are differents.
def check_results(R_list, algos):
        for j in range(len(R_list) - 1):
                l1 = R_list[algos[j]]
                l2 = R_list[algos[j+1]]
                for e in range(len(l1)):
                        assert(l1[e]==l2[e]), 'results are not equal'

# Used in script_N
def plot_lines_and_pie(scenario, algos, algos_names, left_xlabel, left_xlog, left_x, left_data, right_aggregates_all, right_message, OUTPUT_DIR):
        plt.figure(figsize=(12, 4))
        plt.rcParams.update({'font.size':14})

        # left : plot one line for each algorithm
        ax = plt.subplot(121)
        markers = ('.', 'v', '*', 'd', 'x', 'o')
        
        for algo in algos:
                plt.plot(left_x, left_data[algo], marker=markers[algos.index(algo)], fillstyle='none', markersize=12)
        plt.legend(algos_names, bbox_to_anchor=(1.8, 0.7))

        if left_xlog:
                plt.xscale('log')
                font_size_pie = 14
        else:
                plt.xticks(left_x, left_x)
                font_size_pie = 6
        #plt.yscale('log')
        plt.xlabel(left_xlabel)
        plt.ylabel('Time (seconds)')

        plt.subplots_adjust(top=0.94, bottom=0.15)

        plt.savefig(OUTPUT_DIR + "plot_lines_" + scenario + ".pdf")
        plt.clf()

        # right : pie chart only for some point
        
        plt.figure(figsize=(12, 4.2))
        plt.rcParams.update({'font.size':16})
        
        
        # SR_S1 N = 100 000
        ax = plt.subplot(121)                
        plt.title("Zoom on SR-Ring for " + right_message)
        K = len(right_aggregates_all["SR_S1"].keys()) - 3
        components = ["time BAI", "time DO", "time U"] + ["time R" + str(i) for i in range(1, K+1)]
        time_per_component = [right_aggregates_all["SR_S1"][component] for component in components]
        components = list(map (lambda x: x[5:], components)) # remove "time " from the left of each key
        components = [components[0]] + ["" for i in range(1,K+3)] # print label only for BAI

        cm = plt.get_cmap('gist_rainbow')
        NUM_COLORS = len(components)
        colors = ["black"]
        for i in range(NUM_COLORS-1):
                colors.append(cm(1.*i/NUM_COLORS))
        colors.append("gray")        

        wedges, _ = ax.pie(time_per_component, labels=components, colors=colors, textprops={'fontsize': 16})
        # Sperarate the slices of the pie with black color
        for w in wedges:
                w.set_edgecolor("none")

        # SR_S2 N = 100 000
        ax = plt.subplot(122)                
        plt.title("Zoom on SR-Centralized for " + right_message)
        K = len(right_aggregates_all["SR_S2"].keys()) - 4
        components = ["time BAI", "time DO", "time U"] + ["time R" + str(i) for i in range(1, K+1)] + ["time Comp"]
        time_per_component = [right_aggregates_all["SR_S2"][component] for component in components]
        components = list(map (lambda x: x[5:], components)) # remove "time " from the left of each key
        components = [components[0]] + ["" for i in range(1,K+3)] + [components[K+3]] # print label only for BAI, Comp

        wedges, _ = ax.pie(time_per_component, labels=components, colors=colors, textprops={'fontsize': 16})

        # Sperarate the slices of the pie with black color
        for w in wedges:
                w.set_edgecolor('none')
        
        plt.savefig(OUTPUT_DIR + "plot_pie_" + scenario + ".pdf")
        plt.clf()

# Used in script_K
def plot_lines_K(scenario, algos, algos_names, left_xlabel, left_xlog, left_x, left_data, OUTPUT_DIR):
        plt.figure(figsize=(12, 4))
        plt.rcParams.update({'font.size':14})

        # plot one line for each algorithm
        plt.subplot(121)
        markers = ('.', 'v', '*', 'd', 'x', 'o')
        for algo in algos:
                plt.plot(left_x, left_data[algo], marker=markers[algos.index(algo)], fillstyle='none', markersize=12)
        plt.legend(algos_names, bbox_to_anchor=(1.7, 0.75))

        if left_xlog:
                plt.xscale('log')
                font_size_pie = 14
        else:
                plt.xticks(left_x, left_x)
                font_size_pie = 6
        #plt.yscale('log')
        plt.xlabel(left_xlabel)
        plt.ylabel('Time (seconds)')
        plt.subplots_adjust(top=0.9, bottom=0.2)

        plt.savefig(OUTPUT_DIR + "plot_" + scenario + ".pdf")
        plt.clf()

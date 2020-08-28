#!/usr/bin/env python3
import os
import sys
import json
sys.path.append(os.path.relpath("."))


# Convert dataset .txt files from bernoulli distribution to uniform distribution

file_names = ['data_MovieLens.txt', 'data_Jester_small.txt', 'data_Jester_large.txt']

for file in file_names:
    f = open(file, "r")
    K = int(f.readline())
    f.readline()
    random_mode = 0
    epsilon = 100

    F = open('new_' + file, 'w')
    F.write(str(K) + '\n')
    F.write(str(random_mode) + '\n')
    F.write(str(epsilon) + '\n')

    for i in range (K):
        tmp = str(float(f.readline()) * 100000)
        while tmp[0] != '.':
            F.write(tmp[0])
            tmp = tmp[1:]
        F.write('\n')

    f.close()
    F.close()



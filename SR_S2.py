import itertools
import math
import time

from tools import *
from Crypto.Random import get_random_bytes

#               SUCCESSIVE REJECTS WITH CENTRALIZED COMPARISON

# Self made useful functions are in tools
# This is the mother file of SR_S1 and SR_SP so it has all functions of nodes

# Step "number" refers to the steps as described in main.pdf section 3.3

class DataOwner():
        # Initialize DataOwner, who knows K the number of arms, mu a list of K random
        # distributions of type random_mode, and the AES-CBC key of the network
        def __init__(self, K, random_mode, mu, key):
                self.time = 0
                t = time.time()
                self.K = K
                self.random_mode = random_mode
                self.mu = mu
                self.tau = generate_permutation(self.K)
                self.key = key
                self.time += time.time() - t

        # Step 0: Give to node Ri a mu, chosen with tau, and the random_mode
        def outsource_mu_i(self, i):
                t = time.time()
                iv1 = get_random_bytes(16)
                ciphertext_mu_i = e_aes(self.mu[self.tau[i-1] - 1], iv1, self.key)
                iv2 = get_random_bytes(16)
                ciphertext_random = e_aes(self.random_mode, iv2, self.key)
                self.time += time.time() - t
                return (ciphertext_mu_i, iv1), (ciphertext_random, iv2)

        # Step 1: Share tau with U
        def send_tau(self):
                t = time.time()
                iv = get_random_bytes(16)
                ciphertext_tau = e_aes(self.tau, iv, self.key)
                self.time += time.time() - t
                return ciphertext_tau, iv

# User is the Data Client
class User():
        # Initialize User, who has a budget N
        def __init__(self, N, key):
                self.time = 0
                t = time.time()
                self.N = N
                self.key = key
                self.time += time.time() - t

        # Step 0: Receive the permutation tau from DO
        def receive_tau(self, data_DO_BAI):
                t = time.time()
                ciphertext_tau, iv = data_DO_BAI
                self.tau = parser(d_aes(ciphertext_tau, iv, self.key))
                self.time += time.time() - t

        # Step 1: Send the budget to BAI
        def send_budget(self):
                t = time.time()
                iv = get_random_bytes(16)
                ciphertext_N = e_aes(self.N, iv, self.key)
                self.time += time.time() - t
                return ciphertext_N, iv

        # Step 6: Receive the the index of the best node computed by the cloud
        # and retrieve the best arm using tau
        def receive_max(self, data_BAI_U):
                t = time.time()
                ciphertext_a_max, iv = data_BAI_U
                self.max = self.tau[int(d_aes(ciphertext_a_max, iv, self.key)) - 1]
                self.time += time.time() - t

# The node who launches the K-1 phases, and remove the minimal arm at
# the end of each
class Best_Arm_Identificator():
        def __init__(self, K, key):
                self.time = 0
                t = time.time()
                self.K = K
                self.key = key
                self.list_arm = [i for i in range(1, K+1)]
                self.time += time.time() - t

        # Step 1: Receive the budget N from U
        def receive_budget(self, data_U_BAI):
                t = time.time()
                ciphertext_N, iv = data_U_BAI
                self.N = int(d_aes(ciphertext_N, iv, self.key))
                self.time += time.time() - t

        # Step 1: From N, compute the list of n_j, the number of pull
        # each potential arm has to do at phase j
        def compute_N_j(self):
                t = time.time()
                log_K = 1/2
                for i in range(2, self.K+1):
                        log_K += 1/i
                self.Nj = []
                for j in range(self.K-1):
                        nj = math.ceil((1/log_K) * (self.N - self.K)/(self.K-j))
                        for i in range(0, j):
                                nj -= self.Nj[i]
                        self.Nj.append(nj)
                self.time += time.time() - t

        # Step 2: Send n_j to all node Ri still candidate at phase j
        # Step 3: Receive their encrypted sums and construct a list with it
        def send_Ri(self):
                t = time.time()
                self.lsum = []
                iv = get_random_bytes(16)
                ciphertext_n_j = e_aes(self.Nj[self.j-1], iv, self.key)
                self.time += time.time() - t
                for i in self.list_arm:
                        self.lsum.append(self.list_Ri[i-1].send_back_BAI((ciphertext_n_j, iv)))


        # Step 4: Choose at random a permutation of the encrypted list of sums
        # of rewards and send it to Comp
        def send_Comp(self):
                t = time.time()
                self.o = generate_permutation(self.K - self.j + 1)
                lsum_permu = permute(self.lsum, self.o)
                self.time += time.time() - t
                return lsum_permu

        # Step 5: Receive the index of the minimal element of the permuted list of rewards.
        # Unpermute the index and remove the corresponding arm in list_arm
        def end_round(self, index_min):
                t = time.time()
                a_min = self.o.index(index_min + 1)
                del(self.list_arm[a_min])
                self.time += time.time() - t

        # Step 6: At the end, send the index of the best computed node to the User
        def send_U(self):
                t = time.time()
                iv = get_random_bytes(16)
                ciphertext_a_max = e_aes(self.list_arm[0], iv, self.key)
                self.time += time.time() - t
                return ciphertext_a_max, iv

# Node responsible of drawing rewards for one arm.
# There are K nodes R in total
class R_node():
        # Initialize node Ri who has the AES-CBC key of the network, and the key of node Comp
        def __init__(self, key, key_comp):
                self.time = 0
                t = time.time()
                self.s = 0
                self.n_j = 0
                self.key = key
                self.key_comp = key_comp
                self.time += time.time() - t

        # Step 0: Node Ri receives its mu_i that is outsourced by DataOwner, and the random_mode
        def receive_outsourced_mu(self, data_DO_Ri):
                t = time.time()
                ciphertext_random, iv = data_DO_Ri[1]
                self.random_mode = parser(d_aes(ciphertext_random, iv, self.key))
                ciphertext_mu_i, iv = data_DO_Ri[0]
                if self.random_mode == 1:
                        self.mu_i = float(d_aes(ciphertext_mu_i, iv, self.key))
                elif self.random_mode[0] == 0:
                        self.mu_i = int(d_aes(ciphertext_mu_i, iv, self.key))
                self.time += time.time() - t

        # Step 3: Receive n_j if node Ri is still a candidate node,
        # draw n_j rewards and update his sum.
        # Encrypt the sum with the key of Comp and send it to BAI
        def send_back_BAI(self, data_BAI_Ri):
                t = time.time()
                iv = data_BAI_Ri[1]
                self.n_j = int(d_aes(data_BAI_Ri[0], iv, self.key))
                for x in range(self.n_j):
                        self.s += pull(self.random_mode, self.mu_i)
                iv = get_random_bytes(16)
                # Encrypt with the key shared with Comp
                ciphertext_s = e_aes(self.s, iv, self.key_comp)
                self.time += time.time() - t
                return (ciphertext_s, iv)


# Node responsible of choosing the minimal element to remove. Only he can decrypt the
# sum of rewards, but he does not know which reward correspond to which arm
class Comparator():
        # He only has to know the key he shares with the nodes R
        def __init__(self, key_comp):
                self.time = 0
                t = time.time()
                self.key_comp = key_comp
                self.time += time.time() - t

        # Step 5: Receive a permuted list of cumulative rewards.
        # Decrypt it and send back the index of its minimal element
        def send_back_min(self, lsum_permu):
                t = time.time()
                decrypted_lsum = []
                for i in range(len(lsum_permu)):
                        iv = lsum_permu[i][1]
                        decrypted_lsum.append(float(d_aes(lsum_permu[i][0], iv, self.key_comp)))
                index_min = decrypted_lsum.index(min(decrypted_lsum))
                self.time += time.time() - t
                return index_min


def SR_S2_computation (N, K, random_mode, mu):
        assert K > 1, 'K must be greater than 1'
        assert N > 0, 'N must be greater than 0'

        t_start = time.time()
        # Initialisation of the key shared by all participants except Comp,
        # and the key shared by Comp and the nodes R
        key = get_random_bytes(32)
        key_comp = get_random_bytes(32)

        # Initialisation of participants
        DO = DataOwner(K, random_mode, mu, key)
        # User is the Data Client
        U = User(N, key)
        Comp = Comparator(key_comp)
        BAI = Best_Arm_Identificator(K, key)
        BAI.list_Ri = [R_node(key, key_comp) for i in range(1, K+1)]

        # Step 0: DO shares the random distribution of each arm to the Ri
        for i in range(1, K+1):
                BAI.list_Ri[i-1].receive_outsourced_mu(DO.outsource_mu_i(i))

        # Step 1: BAI receives the budget and initializes the number of pulls to do at each round
        BAI.receive_budget(U.send_budget())
        BAI.compute_N_j()
        # U receives the permutation tau from DO
        U.receive_tau(DO.send_tau())
        
        # Step 2 to 5 done K-1 times. At the end of each, BAI removes
        # an arm from the list of potential best arms
        for j in range(1, K):
                BAI.j = j
                # BAI asks for updated sums to the nodes still candidates
                BAI.send_Ri()
                # BAI asks Comp which arm should be removed, he deceives
                # Comp by permuting the list of sum before sending it
                BAI.end_round(Comp.send_back_min(BAI.send_Comp()))

        # Step 6: BAI sends the best computed node to the User
        # who will retrieve the best arm using tau
        U.receive_max(BAI.send_U())

        # Time computation results
        t_stop = time.time() - t_start
        result = dict()
        result["arm_max"] = U.max
        result["time"] = t_stop

        # final_sums is used to check that all algorithms compute identical sums
        final_sums = [0] * K
        for i in range(K):
                final_sums[DO.tau[i] - 1] = BAI.list_Ri[i].s
        result["sums"] = final_sums
        
        result["time DO"] = DO.time
        result["time U"] = U.time
        result["time BAI"] = BAI.time
        result["time Comp"] = Comp.time
        
        for i in range(1, K+1):
                result["time R" + str(i)] = BAI.list_Ri[i-1].time
        return result

if __name__ == "__main__":
        run_experiment(SR_S2_computation)

# ----- Tests -----
"""
random.seed(1)
N = 50; K = 5; random_mode = (0,5)
mu = [30,30] + [28] * (K-2)
print(SR_S2_computation(N, K, random_mode, mu))
"""

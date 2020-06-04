import math
import time

from tools import *

#           SUCCESSIVE REJECTS ALGORITHM

# Useful self made functions are in tools

# Step "number" refers to steps as defined in main.pdf section 3.1

class DataOwner_basic():
        # Initialize DataOwner, who knows K the number of arms, mu a list of K random
        # distributions of type random_mode
        def __init__(self, K, random_mode, mu):
                self.time = 0
                t = time.time()
                self.K = K
                self.random_mode = random_mode
                self.mu = mu
                self.tau = generate_permutation(K)
                self.time += time.time() - t

        # Send all mu to BAI, but in a permuted order using tau
        def outsource_mu(self):
                t = time.time()
                mu_permu = [0] * self.K
                for i in range(self.K):
                        mu_permu[i] = self.mu[self.tau[i] -1]
                return self.random_mode, mu_permu

        # Step 1: Share tau with the User
        def send_tau(self):
                return self.tau

class User():
        # Initialize User, who has a budget N
        def __init__(self, N):
                self.time = 0
                t = time.time()
                self.N = N
                self.time += time.time() - t
                
        # Step 0: Receive tau from the Data Owner
        def receive_tau(self, tau):
                t = time.time()
                self.tau = tau
                self.time += time.time() - t

        # Step 1: Send the budget to BAI
        def send_budget(self):
                return self.N

        # At the end, receives the best arm computed by the cloud
        # and retrieves the correct one using tau
        def receive_max(self, a_max):
                t = time.time()
                self.max = self.tau[a_max - 1]
                self.time += time.time() - t

# The node who launches the K-1 phases, and removes the minimal arm at
# the end of each
class Best_Arm_Identificator_basic():
        def __init__(self, K):
                self.time = 0
                t = time.time()
                self.K = K
                self.list_arm = [i for i in range(1, K+1)]
                self.lsum = [0] * K
                self.all_sums = [0] * K
                self.time += time.time() - t

        # Step 0: Receive all mu from DO
        def receive_mu(self, data_DO_BAI):
                t = time.time()
                self.random_mode = data_DO_BAI[0]
                self.mu = data_DO_BAI[1]
                self.time += time.time() - t

        # Step 1: Receive budget from the User
        def receive_budget(self, N):
                t = time.time()
                self.N = N
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

        # One of the K - 1 phases of step 2
        def one_turn(self, j):
                t = time.time()
                i = 0
                for a in self.list_arm:
                        for x in range(self.Nj[j-1]):
                                self.lsum[i] += pull(self.random_mode, self.mu[a-1])
                        i += 1
                o = generate_permutation(self.K - j + 1)
                self.i_m = argmin(self.lsum, o)

                # Keep in memory the sum of the arms rejected.
                # Useful to check that results are identical.
                arm_min = self.list_arm[self.i_m]
                self.all_sums[arm_min - 1] = self.lsum[self.i_m]

                # Remove the worst arm
                del(self.list_arm[self.i_m])
                del(self.lsum[self.i_m])

                # Keep in memory the last sum too
                if j == self.K - 1:
                        self.all_sums[self.list_arm[0] - 1] = self.lsum[0]
                self.time += time.time() - t

        # At the end, sends the best computed arm to the User
        def send_U(self):
                return self.list_arm[0]

def SR_computation(N, K, random_mode, mu):
        t_start = time.time()
        # Initialisation of participants
        DO = DataOwner_basic(K, random_mode, mu)
        # User is the Data Client
        U = User(N)
        BAI = Best_Arm_Identificator_basic(K)
        
        # Step 0: DO shares the random distribution of each arm with BAI
        BAI.receive_mu(DO.outsource_mu())
        
        # Step 1: U gives its budget N to BAI, who will compute the number of
        # pulls to do at each round. He then receives the permutation tau from DO.        
        BAI.receive_budget(U.send_budget())
        BAI.compute_N_j()
        U.receive_tau(DO.send_tau())

        # Step 2: BAI executes the Successive Rejects algorithm
        for j in range(1, K):
                BAI.one_turn(j)

        # BAI gives its result to the User who uses tau to retrieve the best arm
        U.receive_max(BAI.send_U())

        # Time computation results
        t_stop = time.time() - t_start
        result = dict()
        result["arm_max"] = U.max
        result["time"] = t_stop

        # final_sums is used to check that all algorithms compute identical sums
        final_sums = [0] * K
        for i in range(K):
                final_sums[DO.tau[i]-1] = BAI.all_sums[i]
        result["sums"] = final_sums

        result["time DO"] = DO.time
        result["time U"] = U.time
        result["time BAI"] = BAI.time

        return result

if __name__ == "__main__":
	run_experiment(SR_computation)


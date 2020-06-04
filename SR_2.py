from SR import *

#               SUCCESSIVE REJECTS WITH CENTRALIZED COMPARISON

# It is the same algorithm as SR_S2 but without any encryption

# Self made useful functions are in tools
# Import unchanged functions from SR

# Step "number" refers to the steps as described in main.pdf section 3.3

class DataOwner(DataOwner_basic):
        # Step 0: Gives to node Ri a mu, chosen with tau, and the random_mode
        def outsource_mu_i(self, i):
                return self.mu[self.tau[i-1] - 1], self.random_mode
        

class Best_Arm_Identificator(Best_Arm_Identificator_basic):
        def __init__(self, K):
                self.time = 0
                t = time.time()
                self.K = K
                self.list_arm = [i for i in range(1, K+1)]
                self.time += time.time() - t
                
        # Step 2: Send n_j to all node Ri still candidate at phase j
        # Step 3: Receive their encrypted sums and construct a list with it
        def send_Ri(self):
                self.lsum = []
                for i in self.list_arm:
                        self.lsum.append(self.list_Ri[i-1].send_back_BAI(self.Nj[self.j-1]))
    
        # Step 4: Choose at random a permutation of the list of sums of rewards
        # and send it to Comp    
        def send_Comp(self):
                t = time.time()
                self.o = generate_permutation(self.K - self.j + 1)
                lsum_permu = [0] * (self.K - self.j + 1)
                for i in range (self.K - self.j + 1):
                        lsum_permu[self.o[i]-1] = self.lsum[i]
                self.time += time.time() - t
                return lsum_permu

        # Step 5: Receive the index of the minimal element of the permuted list of rewards.
        # Unpermute the index and remove the corresponding arm in list_arm
        def end_round(self, index_min):
                t = time.time()
                a_min = self.o.index(index_min + 1)
                del(self.list_arm[a_min])
                self.time += time.time() - t
   
# Node responsible of choosing the minimal element to remove.
# He doesn't know which reward correspond to which arm
class Comparator():
        def __init__(self):
                self.time = 0

        # Step 5: Receive a permuted list of cumulative rewards. Send to BAI its minimal index
        def send_back_index_min(self, lsum_permu):
                t = time.time()
                index_min = lsum_permu.index(min(lsum_permu))
                self.time += time.time() - t
                return index_min

class R_node():
        def __init__(self):
                self.time = 0
                t = time.time()
                self.s = 0
                self.n_j = 0
                self.time += time.time() - t

        # Step 0: Node Ri receives its mu_i that is outsourced by DataOwner, and the random_mode
        def receive_outsourced_mu(self, data_DO_Ri):
                t = time.time()
                self.random_mode = data_DO_Ri[1]
                self.mu_i = data_DO_Ri[0]
                self.time += time.time() - t

        # Step 3: Receive n_j if node Ri is still a candidate node,
        # draw n_j rewards and update his sum.
        # Send the sum back to BAI
        def send_back_BAI(self, data_BAI_Ri):
                t = time.time()
                self.n_j = data_BAI_Ri
                for x in range(self.n_j):
                        self.s += pull(self.random_mode, self.mu_i)
                self.time += time.time() - t
                return self.s


def SR_2_computation (N, K, random_mode, mu):
        t_start = time.time()
        # Initialisation of participants
        DO = DataOwner(K, random_mode, mu)
        # User is the Data Client
        U = User(N)
        Comp = Comparator()
        BAI = Best_Arm_Identificator(K)
        BAI.list_Ri = [R_node() for i in range(1, K+1)]

        # Step 0: DO shares the random distribution of each arm to the Ri
        for i in range(1, K+1):
                BAI.list_Ri[i-1].receive_outsourced_mu(DO.outsource_mu_i(i))

        # Step 1: U receives the permutation tau from DO
        U.receive_tau(DO.send_tau())
        # BAI receives the budget and initialize the number of pulls to do at each round
        BAI.receive_budget(U.send_budget())
        BAI.compute_N_j()

        # Step 2 to 5 done K-1 times. At the end of each, BAI removes
        # an arm from the list of potential best arms
        for j in range(1, K):
                Comp.j = j
                BAI.j = j
                # BAI asks for updated sums to the nodes still candidates
                BAI.send_Ri()
                # BAI asks Comp which arm should be removed, he deceives
                # Comp by permuting the list of sum before sending it
                BAI.end_round(Comp.send_back_index_min(BAI.send_Comp()))

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
        run_experiment(SR_2_computation)

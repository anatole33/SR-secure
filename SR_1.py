from SR_2 import *

#               SUCCESSIVE REJECTS WITH RING COMPARISON

# It is the same algorithm as SR_S1 but without any encryption

# Import unchanged functions from SR_2

# Step "number" refers to steps as described in main.pdf section 3.2

class Ring_BAI(Best_Arm_Identificator_basic):
        def __init__(self, K):
                self.time = 0
                t = time.time()
                self.K = K
                self.list_arm = [i for i in range(1, K+1)]
                self.time += time.time() - t
                
        # Step 2: Send the components n_j, first and next for each candidate node
        # Then start a loop with the first node
        def R_send_Ri(self):
                t = time.time()
                self.o = generate_permutation(self.K - self.j + 1)
                index = 0
                self.time += time.time() - t
                for i in self.list_arm:
                        t = time.time()
                        if self.o[index] == 1:
                                first_i = 1
                                first_node = self.list_Ri[i-1]
                        else:
                                first_i = 0
                        if self.o[index] != (self.K - self.j + 1):
                                next_i = self.list_arm[self.o.index(self.o[index]+1)]
                        else:
                                next_i = 0
                        index += 1
                        self.time += time.time() - t
                        self.list_Ri[i-1].R_receive_BAI((self.Nj[self.j-1], first_i, next_i))
                first_node.start_ring()

        # Step 3: At the end of each phases get the index of the minimum node R.
        # Remove it from the list of candidate arms
        def R_end_round(self, i_m):
                t = time.time()
                self.list_arm.remove(i_m)
                self.time += time.time() - t         


class Ring_R_node(R_node):
        # Initialize R node i
        def __init__(self, i):
                self.time = 0
                t = time.time()
                self.i = i
                self.s = 0
                self.n_j = 0
                self.time += time.time() - t

        # Step 2: At the begening of each phases, receive n_j, first and next
        # if the node is still a candidate node. Update the sum s with n_j rewards
        def R_receive_BAI(self, data_BAI_Ri):
                t = time.time()
                self.n_j = data_BAI_Ri[0]
                self.first = data_BAI_Ri[1]
                self.next = data_BAI_Ri[2]
                for i in range(self.n_j):
                        self.s += pull(self.random_mode, self.mu_i)
                self.time += time.time() - t

        # Step 3: The node with component first = 1 will use this function
        def start_ring(self):
                t = time.time()
                self.S_m = self.s        
                self.time += time.time() - t
                self.list_Ri[self.next-1].R_receive_Ri((self.S_m, self.i))

        # Step 3: Receive S_m and i_m from an other node R. Change them if needed
        # and then transfer to the next node or to BAI if next = 0
        def R_receive_Ri(self, data_Ri_Ri):
                t = time.time()
                self.S_m, self.i_m = data_Ri_Ri
                if self.S_m > self.s:
                        self.S_m = self.s
                        self.i_m = self.i
                if self.next == 0:
                        self.time += time.time() - t
                        self.BAI.R_end_round(self.i_m)
                else:
                        self.time += time.time() - t
                        self.list_Ri[self.next-1].R_receive_Ri((self.S_m, self.i_m))


def SR_1_computation (N, K, random_mode, mu):
        t_start = time.time()
        # Initialization of participants
        DO = DataOwner(K, random_mode, mu)
        # User is the Data Client
        U = User(N)
        BAI = Ring_BAI(K)
        BAI.list_Ri = [Ring_R_node(i) for i in range(1, K+1)]

        # Step 0: DO shares the random distribution of each arm to the Ri
        for i in range(1, K+1):
                BAI.list_Ri[i-1].receive_outsourced_mu(DO.outsource_mu_i(i))
                # Makes the Ri know each other
                BAI.list_Ri[i-1].list_Ri = BAI.list_Ri
                BAI.list_Ri[i-1].BAI = BAI

        # Step 1: BAI receives the budget and initialize the number of pulls
        # to do at each round
        BAI.receive_budget(U.send_budget())
        BAI.compute_N_j()
        # U receives tau from DO
        U.receive_tau(DO.send_tau())

        # Step 2 and 3 done K-1 times. At the end of each, BAI removes an arm
        # from the list of potential best arms
        for j in range(1, K):
                BAI.j = j
                BAI.R_send_Ri()

        # Step 4: BAI sends the best computed node to the User
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
        for i in range(1, K+1):
                result["time R" + str(i)] = BAI.list_Ri[i-1].time
        return result

if __name__ == "__main__":
        run_experiment(SR_1_computation)

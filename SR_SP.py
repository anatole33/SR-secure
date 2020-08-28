from SR_S2 import *
from phe import paillier

#                SUCCESSIVE REJECTS WITH PAILLIER

# Import unchanged functions from SR_S2

# Step "number" refers to the steps as described in main.pdf section 3.4

class Paillier_DataOwner(DataOwner):
        # Initialize DataOwner, who knowns K the number of arms, mu a list
        # of K random distributions of type random_mode, the AES key of
        # the network and the paillier public key of node Comp
        def __init__(self, K, random_mode, mu, key, pk_comp):
                self.time = 0
                t = time.time()
                self.K = K
                self.random_mode = random_mode
                self.mu = mu
                self.tau = generate_permutation(self.K)
                self.key = key
                self.pk_comp = pk_comp
                self.time += time.time() - t

        # Step 0: DataOwner outsources the random distribution of the arms
        # to BAI using tau, but encrypted with Comp public key
        def outsource_mu(self):
                t = time.time()
                cipher_mu = [self.pk_comp.encrypt(self.mu[self.tau[i]-1]) for i in range(self.K)]
                iv = get_random_bytes(16)
                ciphertext_random = e_aes(self.random_mode, iv, self.key)
                self.time += time.time() - t
                return (cipher_mu, ciphertext_random, iv)

# BAI inherits of the BAI in SR_S2, and additionaly uses Comp's Paillier key 
class Paillier_BAI(Best_Arm_Identificator):
        def __init__(self, K, key, pk_comp):
                self.time = 0
                t = time.time()
                self.K = K
                self.key = key
                self.pk_comp = pk_comp
                self.list_arm = [i for i in range(1, K+1)]
                self.lsum = [pk_comp.encrypt(0) for _ in range(K)]
                self.final_sums = [0] * K
                self.time += time.time() - t

        # Receive the random distribution of each arm encrypted with Comp's key
        def receive_mu(self, data_DO_BAI):
                t = time.time()
                cipher_mu = data_DO_BAI[0]
                ciphertext_random = data_DO_BAI[1]
                iv = data_DO_BAI[2]
                self.mu = cipher_mu
                self.random_mode = parser(d_aes(ciphertext_random, iv, self.key))
                if self.random_mode[0] == 0:
                        self.epsilon = self.random_mode[1]
                self.time += time.time() - t

        # Step 2: Draw n_j rewards for the remaining arms at round j and
        # update their encrypted sum of rewards
        def update_sums(self):
                t = time.time()
                n_j = self.Nj[self.j-1]

                for i in range(self.K - self.j + 1):
                        arm = self.list_arm[i]
                        mu_arm = self.mu[arm-1]
                        reward = 0
                        for _ in range(n_j):
                                reward += random.randint(-self.epsilon, self.epsilon)
                        enc_reward = self.pk_comp.encrypt(reward)
                        self.lsum[i] += enc_reward + mu_arm * n_j
                self.time += time.time() - t

        # Step 3: Receive the permuted index of the minimal element among all sums.
        # Remove the sum and the associated arm from the candidate arms,
        # and add the sum in final_sums. It is used to compare the results
        # of different algorithms
        def end_round(self, index_min):
                t = time.time()
                a_min = self.o.index(index_min + 1)
                self.final_sums[self.list_arm.pop(a_min)-1] = self.lsum.pop(a_min)
                if self.j == self.K-1:
                        self.final_sums[self.list_arm[0]-1] = self.lsum[0]
                self.time += time.time() - t

# Node responsible of choosing the minimal element to remove. Only he can decrypt the
# sum of rewards, but he does not know which reward correspond to which arm
class Paillier_Comparator():
        def __init__(self, pk_comp, sk_comp):
                self.time = 0
                t = time.time()
                self.pk = pk_comp
                self.sk = sk_comp
                self.time += time.time() - t

        # Step 3: Receive a permuted list of cumulative rewards. Decrypt it and
        # send back the index of its minimal element
        def send_back_min(self, lsum_permu):
                t = time.time()
                decrypted_lsum = []
                for i in range(len(lsum_permu)):
                        decrypted_lsum.append(self.sk.decrypt(lsum_permu[i]))
                index_min = decrypted_lsum.index(min(decrypted_lsum))
                self.time += time.time() - t
                return index_min


def SR_SP_computation (N, K, random_mode, mu):
        assert K > 1, 'K must be greater than 1'
        assert N > 0, 'N must be greater than 0'

        assert type(random_mode) == tuple and random_mode[0] == 0, 'random mode invalid'

        # Initialisation of the key shared by all participants except Comp
        key = get_random_bytes(32)
        pk_comp, sk_comp = paillier.generate_paillier_keypair()

        t_start = time.time()

        # Initialisation of participants
        Comp = Paillier_Comparator(pk_comp, sk_comp)       
        DO = Paillier_DataOwner(K, random_mode, mu, key, pk_comp)
        # User is the Data Client
        U = User(N, key)
        BAI = Paillier_BAI(K, key, pk_comp)
        
        # Step 0: DO shares the random distribution of each arm to BAI
        BAI.receive_mu(DO.outsource_mu())

        
        # Step 1: BAI receives the budget and initialize the number of
        # pulls to do at each round
        BAI.receive_budget(U.send_budget())
        BAI.compute_N_j()
        # U receives the permutation tau from DO
        U.receive_tau(DO.send_tau())

        # Step 2 and 3, done K-1 times. At the end of each, BAI removes
        # an arm from the list of potential best arms
        for j in range(1, K):
                BAI.j = j
                BAI.update_sums()
                # BAI asks Comp which arm should be removed, he deceives
                # Comp by permuting the list of sums before sending it
                BAI.end_round(Comp.send_back_min(BAI.send_Comp()))

        # Step 4: BAI sends the best computed arm to the User
        U.receive_max(BAI.send_U())

        # Time computation results
        t_stop = time.time() - t_start
        result = dict()
        result["arm_max"] = U.max
        result["time"] = t_stop

        # final_sums is used to check that all algorithms compute identical sums
        final_sums = [0] * K
        for i in range(K):
                final_sums[DO.tau[i]-1] = Comp.sk.decrypt(BAI.final_sums[i])
        result["sums"] = final_sums
        
        result["time DO"] = DO.time
        result["time U"] = U.time
        result["time BAI"] = BAI.time
        result["time Comp"] = Comp.time

        return result

if __name__ == "__main__":
        run_experiment(SR_SP_computation)
"""
random.seed(1)
N = 50; K = 3; random_mode = (0,5)
mu = [30,30] + [28] * (K-2)
print(SR_SP_computation(N, K, random_mode, mu))
"""

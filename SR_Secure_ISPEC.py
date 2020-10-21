from SR_SP import *

#               SUCCESSIVE REJECTS - SECURE as in ISPEC2019

# Import DataOwner, User and Best_arm_identificator from SR_S2 (through SR_S2P)
# Import Paillier_Comparator from SR_S2P

class Paillier2_DataOwner(DataOwner):
        # Initialize DataOwner, who knowns K the number of arms, mu a list
        # of K random distributions, epsilon the common parameter for pulling
        # an arm, and the paillier public key of node Comp
        def __init__(self, K, epsilon, mu, pk_comp):
                self.time = 0
                t = time.time()
                self.K = K
                self.epsilon = epsilon
                self.mu = mu
                self.pk_comp = pk_comp
                self.time += time.time() - t

        # Step 0: DataOwner outsources the random distribution of the arms
        # to a node RPj using tau, but encrypted with Comp public key
        def outsource_mu(self, list_RP):
                t = time.time()
                cipher_mu = [self.pk_comp.encrypt(self.mu[i]) for i in range(self.K)]
                self.time += time.time() - t
                for j in range(self.K - 1):
                        tj = time.time()
                        cipher_epsilon = list_RP[j].pk.encrypt(self.epsilon)
                        self.time += time.time() - tj
                        list_RP[j].receive_mu(cipher_mu, cipher_epsilon)

class User2():
        def __init__(self, N, pk_u, sk_u):
                self.time = 0
                t = time.time()
                self.N = N
                self.pk = pk_u
                self.sk = sk_u
                self.time += time.time() - t

        def send_budget(self):
                return self.N
        
        def receive_max(self, cipher_max):
                t = time.time()
                self.max = self.sk.decrypt(cipher_max)
                self.time += time.time() - t

# The node who launches the K-1 phases, and remove the minimal arm at
# the end of each
class Paillier_BAI(Best_Arm_Identificator):
        def __init__(self, K, pk_comp):
                self.time = 0
                t = time.time()
                self.K = K
                self.pk_comp = pk_comp
                self.list_arm = [i for i in range(1, K+1)]
                self.lsum = [pk_comp.encrypt(0) for _ in range(K)]
                self.final_sums = [0] * K
                self.time += time.time() - t

        def receive_budget(self, N):
                t = time.time()
                self.N = N
                self.time += time.time() - t

        def one_round(self, j):
                t = time.time()
                # Encrypt nj the number of pulls to do on each arm at round j
                cipher_nj = self.list_RP[j-1].pk.encrypt(self.Nj[j-1])
                # Encrypt the list of arms still candidate
                cipher_list_arm = [self.list_RP[j-1].pk.encrypt(self.list_arm[a]) for a in range(self.K-j+1)]
                # Ask node RP_j to draw rewards and update the list of sums
                # Don't add to self the time taken by node RP
                self.time += time.time() - t
                self.lsum = self.list_RP[j-1].update_sum(cipher_nj, cipher_list_arm, self.lsum)

                # Ask node Comp to decrypt the list of sums and return the
                # index of the minimal element. Permute the list before sending it
                t = time.time()
                sigma = generate_permutation(self.K-j+1)
                permuted_lsum = permute(self.lsum, sigma)
                self.time += time.time() - t
                index_min = self.Comp.send_back_min(permuted_lsum)

                # Remove the minimal arm in list_arm and its sum in list_sums
                # Save the sum (encrypted) in final_sums for correctness check
                t = time.time()
                a_min = sigma.index(index_min + 1)
                self.final_sums[self.list_arm.pop(a_min)-1] = self.lsum.pop(a_min)
                if j == self.K-1:
                        self.final_sums[self.list_arm[0]-1] = self.lsum[0]
                self.time += time.time() - t

        def send_U(self):
                t = time.time()
                cipher_max = self.User.pk.encrypt(self.list_arm[0])
                self.time += time.time() - t
                return cipher_max


class RP_node():
        def __init__(self, pk, sk, pk_comp):
                self.time = 0
                t = time.time()
                self.sk = sk
                self.pk = pk
                self.pk_comp = pk_comp
                self.time += time.time() - t

        def receive_mu(self, cipher_mu, cipher_epsilon):
                t = time.time()
                self.mu = cipher_mu
                self.epsilon = self.sk.decrypt(cipher_epsilon)
                self.time += time.time() - t

        def update_sum(self, cipher_nj, cipher_list_arm, lsum):
                t = time.time()
                n_j = self.sk.decrypt(cipher_nj)
                list_arm = [self.sk.decrypt(cipher_list_arm[a]) for a in range(len(cipher_list_arm))]
                # Update the sum of each candidate arm with n_j pulls
                for i in range(len(list_arm)):
                        arm = list_arm[i]
                        mu_arm = self.mu[arm-1]
                        reward = 0
                        for x in range(n_j):
                                reward += random.randint(-self.epsilon, self.epsilon)
                        enc_reward = self.pk_comp.encrypt(reward)
                        lsum[i] += enc_reward + mu_arm * n_j
                self.time += time.time() - t
                return lsum

def SR_ISPEC_computation (N, K, random_mode, mu):
        assert K > 1, 'K must be greater than 1'
        assert N > 0, 'N must be greater than 0'

        assert type(random_mode) == tuple and random_mode[0] == 0, 'random mode invalid'
        epsilon = random_mode[1]

        # Initialisation of the keys
        pk_comp, sk_comp = paillier.generate_paillier_keypair()
        pk_u, sk_u = paillier.generate_paillier_keypair()
        R_keys = []
        for _ in range(K-1):
                R_keys.append((paillier.generate_paillier_keypair()))
        
        t_start = time.time()

        # Initialisation of participants
        Comp = Paillier_Comparator(pk_comp, sk_comp)       
        DO = Paillier2_DataOwner(K, epsilon, mu, pk_comp)
        U = User2(N, pk_u, sk_u)
        BAI = Paillier_BAI(K, pk_comp)
        BAI.Comp = Comp
        BAI.list_RP = [RP_node(R_keys[i][0], R_keys[i][1], pk_comp) for i in range(K-1)]
        BAI.User = U

        # DO shares the random distribution of each arm to the Ri
        DO.outsource_mu(BAI.list_RP)
        
        # Step 1
        # BAI receives the budget and initialize the number of pulls to do at each round
        BAI.receive_budget(U.send_budget())
        BAI.compute_N_j()

        for j in range(1, K):
                BAI.one_round(j)

        # Step 6: BAI sends the best computed arm to the User
        U.receive_max(BAI.send_U())

        # Time computation results
        t_stop = time.time() - t_start
        result = dict()
        result["arm_max"] = U.max
        result["time"] = t_stop
        final_sums = [0] * K
        for i in range(K):
                final_sums[i] = Comp.sk.decrypt(BAI.final_sums[i])
        result["sums"] = final_sums
        
        result["time DO"] = DO.time
        result["time U"] = U.time
        result["time BAI"] = BAI.time
        result["time Comp"] = Comp.time
        
        for j in range(1, K):
                result["time RP" + str(j)] = BAI.list_RP[j-1].time
        return result

if __name__ == "__main__":
        run_experiment(SR_ISPEC_computation)

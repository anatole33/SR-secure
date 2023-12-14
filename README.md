This code allows to reproduce the empirical evaluation from our TDSC paper **[Secure Protocols for Best Arm Identification in Federated Stochastic Multi-Armed Bandits](https://ieeexplore.ieee.org/document/9721650)**.
If you use our code, please cite:

```
@article{CDLS23,
  author    = {Ciucanu, R. and Delabrouille, A. and Lafourcade, P. and Soare, M.},
  title     = {{Secure Protocols for Best Arm Identification in Federated Stochastic Multi-Armed Bandits}},
  journal   = {IEEE Transactions on Dependable and Secure Computing (TDSC)},
  volume    = {20},
  number    = {2},
  pages     = {1378--1389},
  year      = {2023}
}
```


We detail next the experimental setup and results in Section 5.3 and 6.2 of our paper.

We implemented our protocols: SR-Ring (`SR_S1.py`), SR-Centralized (`SR_S2.py`), and SR-Paillier (`SR_SP.py`).

We also implemented: the standard Successive Rejects (`SR.py`), two distributed protocols SR-Ring' (`SR_1.py`) and SR-Centralized' (`SR_2.py`) that are the same as SR-Ring and SR-Centralized, after removing all encryptions/decryptions such that all messages are communicated in clear between participants, and the old protocol proposed in the conference version of our paper (`SR_Secure_ISPEC.py`). 

The scripts to reproduce our figures are:

- `script_N.py` generates Fig. 7(a) and 7(b) in the folder `experiment_N`.
- `script_K.py` generates Fig. 7(c) in the folder `experiment_K`.
- `script_SR_SP.py` generates Fig. 9(a) and 9(b) in the folder `experiment_SR_SP`.
- `script_real_data.py` generates Fig. 7(d) and 9(c) in the folder `experiment_real_data`.

All these scripts generate the figures using the results of our previous runs, saved as `*.txt` files in the corresponding folders. If you want to re-run the protocols, you simply need to uncomment the lines starting with `#os.system("python3 " + algo + ".py "...` in the scripts

The script `install-python-and-libraries.sh` installs Python3 and the necessary
libraries.

This code allows to reproduce the empirical evaluation from our paper **Secure Protocols for Best Arm Identification in Stochastic Multi-Armed Bandits**.
We detail the experimental setup and results in Section 4.6 and 5.5 of our paper.

We implemented our all protocols: SR-Ring (`SR_S1.py`), SR-Centralized (`SR_S2.py`), and SR-Paillier (`SR_SP.py`).

We also implemented: the standard Successive Rejects (`SR.py`), two distributed protocols SR-Ring' (`SR_1.py`) and SR-Centralized' (`SR_2.py`) that are the same as SR-Ring, SR-Centralized, after removing all encryptions/decryptions such that all messages are communicated in clear between participants, and the old protocol proposed in the conference version of our paper (`SR_Secure_ISPEC`). 

The scripts to reproduce our figures are:

- `script_N.py` generates Fig. 8(a) and 8(b) in the folder `experiment_N`.
- `script_K.py` generates Fig. 8(c) in the folder `experiment_K`.
- `script_SR_SP.py` generates Fig. 11(a) and 11(b) in the folder `experiment_SR_SP`.
- `script_real_data.py` generates Fig. 8(d) and 11(c) in the folder `experiment_real_data`.

All these scripts generate the figures using the results of our previous runs, saved as `*.txt` files in the corresponding folders. If you want to re-run the protocols, you simply need to uncomment the lines starting with `#os.system("python3 " + algo + ".py "...` in the scripts

The script `install-python-and-libraries.sh` installs Python3 and the necessary
libraries.

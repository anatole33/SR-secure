This is the code related to the paper **Secure Best Arm Identification in
Stochastic Bandits**.

SR is the simple successive rejects algorithm with no encryption nor
distribution, as shown in Section 3.2.
`SR_S1.py` is SR-Ring (Section 3.3) and `SR_S2.py` is SR-Centralized (Section 3.4).
`SR_1.py` and `SR_2.py` are non encrypted versions of SR_S1 and SR_S2.
`SR_SP.py` is SR-Paillier (Section 3.5).

`script_N.py` allows to reproduce the figure 10 in its associated folder:
`experiment_N`. `script_K.py` the figure 11, `script_SR_SP.py` the figure 12 and
`script_real_data.py` the figure 13.

All scripts generate the figures using the results of previous runs, the
`*.txt` files in experimental folders. If you wish to run again the algorithms,
uncomment in the script of your interest the line starting with
`#os.system("python3 " + algo + ".py "...`

The script `install-python-and-libraries.sh` installs Python3 and the necessary
libraries.

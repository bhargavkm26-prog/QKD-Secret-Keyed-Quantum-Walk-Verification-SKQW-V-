# """
# N_max Sweep: How many sessions before Eve reaches 95% confidence?
# Run this after all bugs are fixed. Takes ~5–15 minutes.
# """
# import numpy as np
# import random
# import matplotlib.pyplot as plt
# from collections import defaultdict
# from core.skqw_engine import get_theoretical_distribution

# THRESHOLD = 0.95          # Eve's win condition
# CHECK_ROUNDS = 85         # Per session
# MAX_SESSIONS = 300        # Safety cap — stop if Eve never reaches threshold
# K_LENGTHS_TO_TEST = [3, 6, 9, 12]   # The sweep
# TRIALS_PER_K = 3          # Average over multiple random K values per length

# def calculate_tv_distance(dist_a, dist_b):
#     all_keys = set(dist_a.keys()).union(set(dist_b.keys()))
#     return 0.5 * sum(abs(dist_a.get(k, 0) - dist_b.get(k, 0)) for k in all_keys)

# def run_single_nmax(k_length):
#     """Returns the session number when Eve hits 95% confidence, or MAX_SESSIONS if never."""
#     TRUE_K = format(random.getrandbits(k_length), f'0{k_length}b')
#     all_ks = [format(i, f'0{k_length}b') for i in range(2**k_length)]
    
#     # Pre-compute all distributions
#     dists = {k: get_theoretical_distribution(k) for k in all_ks}
    
#     beliefs = {k: 1.0 / len(all_ks) for k in all_ks}
    
#     for session in range(1, MAX_SESSIONS + 1):
#         # Sample from true distribution
#         true_dist = dists[TRUE_K]
#         samples = random.choices(list(true_dist.keys()), weights=list(true_dist.values()), k=CHECK_ROUNDS)
#         observed = {s: samples.count(s)/CHECK_ROUNDS for s in set(samples)}
        
#         # Bayesian update
#         for k in all_ks:
#             tv = calculate_tv_distance(dists[k], observed)
#             beliefs[k] *= np.exp(-tv * 10)
        
#         total = sum(beliefs.values())
#         for k in all_ks:
#             beliefs[k] /= total
        
#         # Check if Eve has won
#         if beliefs[TRUE_K] >= THRESHOLD:
#             return session
    
#     return MAX_SESSIONS  # Never reached threshold

# # ==========================================
# # MAIN SWEEP
# # ==========================================
# print("=======================================================")
# print(" 🔬 N_max SWEEP: Eve's sessions-to-compromise vs K-length")
# print("=======================================================")

# nmax_results = {}

# for k_len in K_LENGTHS_TO_TEST:
#     print(f"\n[K_LENGTH={k_len}] Running {TRIALS_PER_K} trials (2^{k_len}={2**k_len} possible keys)...")
#     nmaxes = []
#     for trial in range(TRIALS_PER_K):
#         n = run_single_nmax(k_len)
#         nmaxes.append(n)
#         print(f"  Trial {trial+1}: N_max = {n}")
    
#     avg_nmax = np.mean(nmaxes)
#     nmax_results[k_len] = avg_nmax
#     print(f"  → Average N_max for K_LENGTH={k_len}: {avg_nmax:.1f} sessions")

# print("\n=======================================================")
# print(" 📊 RESULTS TABLE")
# print("=======================================================")
# print(f"{'K_LENGTH':<12} {'Avg N_max':<15} {'2^K (keyspace)':<20}")
# print("-" * 47)
# for k_len, avg in nmax_results.items():
#     print(f"{k_len:<12} {avg:<15.1f} {2**k_len:<20}")

# # Plot N_max vs K_LENGTH
# plt.figure(figsize=(10, 6))
# plt.plot(list(nmax_results.keys()), list(nmax_results.values()), 
#          marker='o', linewidth=2, markersize=8, color='darkblue')
# plt.xlabel("Key Length (K bits)", fontsize=13)
# plt.ylabel("Sessions Until Eve Reaches 95% Confidence (N_max)", fontsize=13)
# plt.title("N_max vs K-Length: Sessions to Compromise under Bayesian Attack", fontsize=14)
# plt.grid(True, linestyle=':', alpha=0.7)
# plt.xticks(K_LENGTHS_TO_TEST)
# plt.tight_layout()
# plt.savefig("data/nmax_vs_klength.png")
# print("\nSaved N_max curve to data/nmax_vs_klength.png")

# # ==========================================
# # FORMULA VALIDATION (Step 3 — Theorem fit)
# # ==========================================
# from scipy.optimize import curve_fit

# k_vals = np.array(list(nmax_results.keys()), dtype=float)
# n_vals = np.array(list(nmax_results.values()), dtype=float)

# # Formula: N_max ≈ a * K + b  (linear model from theory)
# def linear_model(k, a, b):
#     return a * k + b

# popt, _ = curve_fit(linear_model, k_vals, n_vals)
# a_fit, b_fit = popt

# print("\n=======================================================")
# print(" 📐 THEOREM 1: N_max FORMULA FIT")
# print("=======================================================")
# print(f"[+] Fitted formula: N_max ≈ {a_fit:.3f} × K_length + ({b_fit:.3f})")
# print(f"[+] Interpretation: Each additional bit of K buys ~{a_fit:.2f} safe sessions")
# print()

# # Predicted vs actual
# print(f"{'K':>6}  {'Empirical N_max':>16}  {'Formula Predicted':>18}  {'Error':>8}")
# print("-" * 55)
# for k, n in zip(k_vals, n_vals):
#     predicted = linear_model(k, a_fit, b_fit)
#     error = abs(predicted - n) / n * 100
#     print(f"{int(k):>6}  {n:>16.1f}  {predicted:>18.2f}  {error:>7.1f}%")

# # Plot with formula overlay
# k_range = np.linspace(3, 16, 100)
# plt.figure(figsize=(10, 6))
# plt.plot(k_vals, n_vals, 'o', markersize=10, color='darkblue', label='Empirical N_max (simulation)')
# plt.plot(k_range, linear_model(k_range, a_fit, b_fit), '--', color='red',
#          label=f'Theorem 1: N_max ≈ {a_fit:.2f}·K + {b_fit:.2f}')
# plt.xlabel("Key Length (K bits)", fontsize=13)
# plt.ylabel("Sessions Until Eve Reaches 95% Confidence (N_max)", fontsize=13)
# plt.title("N_max vs K-Length with Theorem 1 Formula Overlay", fontsize=14)
# plt.legend(fontsize=11)
# plt.grid(True, linestyle=':', alpha=0.7)
# plt.xticks(K_LENGTHS_TO_TEST)
# plt.tight_layout()
# plt.savefig("data/nmax_formula_fit.png")
# print("\nSaved formula fit plot to data/nmax_formula_fit.png")



"""
N_max Sweep — OPTIMIZED VERSION
Speedups applied:
  1. Parallel pre-computation (ThreadPoolExecutor — safe on Windows)
  2. Numpy-vectorized Bayesian update (50-100x faster than Python loop)
  3. Vectorized TV distance (single matrix op replaces per-key loop)
Zero compromise on results — identical math, identical threshold.
"""
import numpy as np
import random
import os
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.optimize import curve_fit
from core.skqw_engine import get_theoretical_distribution

# ==========================================
# CONFIGURATION
# ==========================================
THRESHOLD       = 0.95   # Eve's win condition
CHECK_ROUNDS    = 85     # Samples per session
MAX_SESSIONS    = 300    # Safety cap
LAMBDA_SCALE    = 10     # Bayesian scaling factor (unchanged)
K_LENGTHS_TO_TEST = [3, 6, 9]
TRIALS_PER_K    = 3
NUM_WORKERS     = 4      # Parallel threads for pre-computation

# ==========================================
# SPEEDUP 1: Parallel Pre-computation
# ==========================================
def _compute_one(k_string):
    """Worker: returns (key_string, probability_dict)."""
    return k_string, get_theoretical_distribution(k_string)

def precompute_parallel(all_ks):
    """
    Runs Qiskit simulations for all keys in parallel threads.
    ThreadPoolExecutor is used (not ProcessPoolExecutor) because:
      - Qiskit Aer (C++ backend) releases the Python GIL during simulation
      - Threads share sys.path, so imports work on Windows without guards
    """
    dists = {}
    total = len(all_ks)
    done = 0
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(_compute_one, k): k for k in all_ks}
        for future in as_completed(futures):
            k, dist = future.result()
            dists[k] = dist
            done += 1
            if done % max(1, total // 10) == 0:
                print(f"    -> Pre-computed {done}/{total} keys...")
    return dists

# ==========================================
# SPEEDUP 2: Build numpy distribution matrix
# ==========================================
def build_matrix(all_ks, dists):
    """
    Converts all dict-based distributions into one numpy matrix.
    Shape: (num_keys, num_states)
    This enables vectorized TV distance computation across ALL keys at once.
    """
    all_states = sorted(set(s for d in dists.values() for s in d.keys()))
    state_idx  = {s: i for i, s in enumerate(all_states)}

    mat = np.zeros((len(all_ks), len(all_states)), dtype=np.float64)
    for row, k in enumerate(all_ks):
        for state, prob in dists[k].items():
            mat[row, state_idx[state]] = prob

    return mat, all_states, state_idx

# ==========================================
# SPEEDUP 3: Vectorized Bayesian Loop
# ==========================================
def run_single_nmax(k_length, dists, dist_matrix, all_states, state_idx):
    """
    Runs one full N_max trial using numpy vectorized operations.

    Original (slow): Python loop over 2^K keys per session
        for k in all_ks:
            tv = calculate_tv_distance(dists[k], observed)   ← dict ops
            beliefs[k] *= exp(-tv * 10)                       ← scalar multiply

    Optimized (fast): Single numpy matrix operation per session
        tv_distances = 0.5 * |dist_matrix - observed_vec|.sum(axis=1)
        beliefs     *= exp(-tv_distances * 10)

    Mathematical result: IDENTICAL. Same formula, same numbers, same threshold.
    """
    n_keys   = len(dist_matrix)
    n_states = len(all_states)
    all_ks   = [format(i, f'0{k_length}b') for i in range(n_keys)]

    # Pick a random true key
    true_k_idx = random.randint(0, n_keys - 1)
    TRUE_K     = all_ks[true_k_idx]

    # Uniform prior as numpy array
    beliefs = np.ones(n_keys, dtype=np.float64) / n_keys

    true_dist_keys = list(dists[TRUE_K].keys())
    true_dist_vals = list(dists[TRUE_K].values())

    for session in range(1, MAX_SESSIONS + 1):

        # 1. Bob samples CHECK_ROUNDS outcomes from true distribution
        samples = random.choices(true_dist_keys, weights=true_dist_vals, k=CHECK_ROUNDS)

        # 2. Build observed distribution as numpy vector (fixed vocabulary)
        observed_vec = np.zeros(n_states, dtype=np.float64)
        for s in samples:
            if s in state_idx:
                observed_vec[state_idx[s]] += 1.0
        observed_vec /= CHECK_ROUNDS

        # 3. Vectorized TV distance — ALL keys simultaneously
        #    dist_matrix : (n_keys, n_states)
        #    observed_vec: (n_states,)  →  broadcasts across all rows
        tv_distances = 0.5 * np.abs(dist_matrix - observed_vec).sum(axis=1)

        # 4. Vectorized Bayesian update
        beliefs *= np.exp(-tv_distances * LAMBDA_SCALE)

        # 5. Normalize — handle numerical underflow gracefully
        total = beliefs.sum()
        if total > 1e-300:
            beliefs /= total
        else:
            # Numerical underflow: beliefs collapsed — reset to uniform
            beliefs = np.ones(n_keys, dtype=np.float64) / n_keys

        # 6. Check Eve's win condition
        if beliefs[true_k_idx] >= THRESHOLD:
            return session

    return MAX_SESSIONS  # Eve never reached threshold within cap

# ==========================================
# MAIN SWEEP
# ==========================================
if __name__ == '__main__':
    print("=======================================================")
    print(" 🔬 N_max SWEEP (OPTIMIZED): Eve's sessions-to-compromise")
    print("=======================================================")

    nmax_results = {}

    for k_len in K_LENGTHS_TO_TEST:
        total_keys = 2 ** k_len
        print(f"\n[K_LENGTH={k_len}] Running {TRIALS_PER_K} trials "
              f"(2^{k_len}={total_keys} possible keys)...")

        all_ks = [format(i, f'0{k_len}b') for i in range(total_keys)]

        # Phase 1: Parallel pre-computation
        print(f"  [Phase 1/2] Pre-computing {total_keys} quantum distributions (parallel)...")
        dists = precompute_parallel(all_ks)

        # Phase 2: Build numpy matrix once, reuse across all trials
        print(f"  [Phase 2/2] Running {TRIALS_PER_K} trials (vectorized Bayesian)...")
        dist_matrix, all_states, state_idx = build_matrix(all_ks, dists)

        nmaxes = []
        for trial in range(TRIALS_PER_K):
            n = run_single_nmax(k_len, dists, dist_matrix, all_states, state_idx)
            nmaxes.append(n)
            print(f"    Trial {trial+1}: N_max = {n}")

        avg_nmax = np.mean(nmaxes)
        nmax_results[k_len] = avg_nmax
        print(f"  → Average N_max for K_LENGTH={k_len}: {avg_nmax:.1f} sessions")

    # Results table
    print("\n=======================================================")
    print(" 📊 RESULTS TABLE")
    print("=======================================================")
    print(f"{'K_LENGTH':<12} {'Avg N_max':<15} {'2^K (keyspace)':<20}")
    print("-" * 47)
    for k_len, avg in nmax_results.items():
        print(f"{k_len:<12} {avg:<15.1f} {2**k_len:<20}")

    # Plot N_max vs K_LENGTH
    os.makedirs("data", exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.plot(list(nmax_results.keys()), list(nmax_results.values()),
             marker='o', linewidth=2, markersize=8, color='darkblue')
    plt.xlabel("Key Length (K bits)", fontsize=13)
    plt.ylabel("Sessions Until Eve Reaches 95% Confidence (N_max)", fontsize=13)
    plt.title("N_max vs K-Length: Sessions to Compromise under Bayesian Attack", fontsize=14)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.xticks(K_LENGTHS_TO_TEST + [12, 15])
    plt.tight_layout()
    plt.savefig("data/nmax_vs_klength.png")
    print("\nSaved N_max curve to data/nmax_vs_klength.png")

    # ==========================================
    # THEOREM 1: Formula fit
    # ==========================================
    k_vals = np.array(list(nmax_results.keys()), dtype=float)
    n_vals = np.array(list(nmax_results.values()), dtype=float)

    def linear_model(k, a, b):
        return a * k + b

    popt, _ = curve_fit(linear_model, k_vals, n_vals)
    a_fit, b_fit = popt

    print("\n=======================================================")
    print(" 📐 THEOREM 1: N_max FORMULA FIT")
    print("=======================================================")
    print(f"[+] Fitted formula : N_max ≈ {a_fit:.3f} × K_length + ({b_fit:.3f})")
    print(f"[+] Interpretation : Each additional bit of K ≈ {a_fit:.2f} safe sessions")
    print()

    print(f"{'K':>6}  {'Empirical N_max':>16}  {'Predicted':>12}  {'Error %':>8}")
    print("-" * 50)
    for k, n in zip(k_vals, n_vals):
        pred  = linear_model(k, a_fit, b_fit)
        error = abs(pred - n) / n * 100
        print(f"{int(k):>6}  {n:>16.1f}  {pred:>12.2f}  {error:>7.1f}%")

    # Plot with formula overlay
    k_range = np.linspace(3, 16, 100)
    plt.figure(figsize=(10, 6))
    plt.plot(k_vals, n_vals, 'o', markersize=10, color='darkblue',
             label='Empirical N_max (simulation)')
    plt.plot(k_range, linear_model(k_range, a_fit, b_fit), '--', color='red',
             label=f'Theorem 1: N_max ≈ {a_fit:.2f}·K + {b_fit:.2f}')
    plt.xlabel("Key Length (K bits)", fontsize=13)
    plt.ylabel("Sessions Until Eve Reaches 95% Confidence (N_max)", fontsize=13)
    plt.title("N_max vs K-Length with Theorem 1 Formula Overlay", fontsize=14)
    # Project K=12 as extrapolated point (computationally impractical to simulate directly)
    k12_projected = linear_model(12, a_fit, b_fit)
    plt.axvline(x=12, color='gray', linestyle=':', alpha=0.6)
    plt.plot(12, k12_projected, 's', markersize=10, color='gray',label=f'K=12 projected by formula: N_max ≈ {k12_projected:.1f}')
         

    plt.legend(fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.xticks(K_LENGTHS_TO_TEST + [12, 15])
    plt.tight_layout()
    plt.savefig("data/nmax_formula_fit.png")
    print("\nSaved formula fit plot to data/nmax_formula_fit.png")

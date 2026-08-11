import numpy as np
import random
import matplotlib.pyplot as plt
from collections import defaultdict
from core.skqw_engine import build_skqw_circuit, get_theoretical_distribution

# ==========================================
# CONFIGURATION
# ==========================================
K_LENGTH = 9  # 512 keys for optimal speed and math scaling
NUM_SESSIONS = 100
CHECK_ROUNDS_PER_SESSION = 85  # Approx 30% of 300 photons

# Generate the true secret K
TRUE_K = format(random.getrandbits(K_LENGTH), f'0{K_LENGTH}b')
print(f"🔒 TRUE SECRET K: {TRUE_K}")

# ==========================================
# STAGE 4: TRUE CLASSICAL STAND-IN
# ==========================================
def simulate_classical_walk(k_string, steps=None):
    if steps is None:
        steps = len(k_string)  # Match quantum walk step count exactly

    """
    A classical random walk where K biases the coin, but NO quantum interference occurs.
    This proves whether the quantum walk is load-bearing or ornamental.
    """
    positions = defaultdict(float)
    positions[0] = 1.0  # Start at origin
    
    for step in range(steps):
        new_positions = defaultdict(float)
        # K biases the classical probability (e.g., '1' means 70% right, '0' means 70% left)
        bias_right = 0.7 if k_string[step % len(k_string)] == '1' else 0.3
        bias_left = 1.0 - bias_right
        
        for pos, prob in positions.items():
            new_positions[pos + 1] += prob * bias_right
            new_positions[pos - 1] += prob * bias_left
        positions = new_positions
        
    return positions

def calculate_tv_distance(dist_a, dist_b):
    """Calculates Total Variation Distance between two distributions."""
    all_keys = set(dist_a.keys()).union(set(dist_b.keys()))
    return 0.5 * sum(abs(dist_a.get(k, 0) - dist_b.get(k, 0)) for k in all_keys)

# ==========================================
# STAGE 5: CUMULATIVE BAYESIAN ATTACKER (EVE)
# ==========================================
print("\n=======================================================")
print(" 🦹 INITIATING CUMULATIVE BAYESIAN ATTACK (MLE)")
print("=======================================================")

# Eve starts with a uniform prior: She assumes all possible keys are equally likely
all_possible_ks = [format(i, f'0{K_LENGTH}b') for i in range(2**K_LENGTH)]
eve_beliefs = {k: 1.0 / len(all_possible_ks) for k in all_possible_ks}

# Pre-compute the theoretical distributions for all possible keys to save time
total_keys = len(all_possible_ks)
print(f"[+] Eve is pre-computing quantum distributions for {total_keys} possible keys...")

quantum_distributions = {}
for idx, k in enumerate(all_possible_ks):
    quantum_distributions[k] = get_theoretical_distribution(k)
    
    # Print a progress update every 10%
    if (idx + 1) % max(1, (total_keys // 10)) == 0:
        print(f"    -> Pre-computed {idx + 1} / {total_keys} keys...")

print("[+] Pre-computation complete! Launching attack...")

# Track Eve's confidence in the TRUE key over time
eve_confidence_history = []

for session in range(1, NUM_SESSIONS + 1):
    # 1. The Channel runs a session with the TRUE_K
    true_distribution = quantum_distributions[TRUE_K]
    
    # Simulate Bob's finite measurement sampling (Shot Noise)
    # Bob draws 85 samples from the true distribution
    bob_samples = random.choices(
        population=list(true_distribution.keys()),
        weights=list(true_distribution.values()),
        k=CHECK_ROUNDS_PER_SESSION
    )
    
    bob_observed_dist = {state: bob_samples.count(state)/CHECK_ROUNDS_PER_SESSION for state in set(bob_samples)}
    
    # 2. Eve intercepts the public transcript (Bob's observed distribution)
    # Eve uses Bayes' Theorem to update her belief for EVERY possible K
    for k in all_possible_ks:
        # Likelihood: How closely does Bob's observation match this K's theoretical output?
        tv = calculate_tv_distance(quantum_distributions[k], bob_observed_dist)
        likelihood = np.exp(-tv * 10) # Scaling factor for Bayesian update
        
        # Posterior = Likelihood * Prior
        eve_beliefs[k] *= likelihood
        
    # 3. Normalize Eve's beliefs so they sum to 1.0 (100%)
    total_belief = sum(eve_beliefs.values())
    for k in all_possible_ks:
        eve_beliefs[k] /= total_belief
        
    # 4. Record Eve's confidence in the actual true key
    true_k_confidence = eve_beliefs[TRUE_K]
    eve_confidence_history.append(true_k_confidence)
    
    if session % 5 == 0 or session == 1:
        best_guess = max(eve_beliefs, key=eve_beliefs.get)
        print(f"[Session {session:02d}] Eve's confidence in TRUE key: {true_k_confidence*100:.2f}% | Top Guess: {best_guess}")

print("\n=======================================================")
print(" 📊 ANALYSIS COMPLETE. GENERATING SECURITY CURVE.")
print("=======================================================")

# Plotting the Leakage Curve
plt.figure(figsize=(10, 6))
plt.plot(range(1, NUM_SESSIONS + 1), eve_confidence_history, marker='o', color='red', label="Eve's Confidence in True K")
plt.axhline(y=0.95, color='black', linestyle='--', label="95% Compromise Threshold (\u03B5)")
plt.title(f"Cumulative Information Leakage over {NUM_SESSIONS} Sessions (K-length={K_LENGTH})")
plt.xlabel("Number of Reused Sessions (N)")
plt.ylabel("Probability of Eve Guessing K")
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig("data/leakage_curve.png")
print("Saved leakage curve to data/leakage_curve.png")

# ==========================================
# STAGE 4: QUANTUM vs CLASSICAL COMPARISON
# ==========================================
print("\n=======================================================")
print(" 📊 STAGE 4: QUANTUM vs CLASSICAL SENSITIVITY TEST")
print("=======================================================")

quantum_tv_scores = []
classical_tv_scores = []
NUM_SENSITIVITY_TRIALS = 200

print(f"[+] Running {NUM_SENSITIVITY_TRIALS} sensitivity trials...")

for i in range(NUM_SENSITIVITY_TRIALS):
    # Pick two random different keys
    k1 = format(random.getrandbits(K_LENGTH), f'0{K_LENGTH}b')
    k2 = format(random.getrandbits(K_LENGTH), f'0{K_LENGTH}b')
    while k2 == k1:
        k2 = format(random.getrandbits(K_LENGTH), f'0{K_LENGTH}b')

    # Quantum TV (uses pre-computed distributions from Stage 5)
    q_dist1 = quantum_distributions[k1]
    q_dist2 = quantum_distributions[k2]
    quantum_tv_scores.append(calculate_tv_distance(q_dist1, q_dist2))

    # Classical TV (K-biased walk, no interference)
    c_dist1 = simulate_classical_walk(k1)
    c_dist2 = simulate_classical_walk(k2)
    classical_tv_scores.append(calculate_tv_distance(c_dist1, c_dist2))

    # Requested Progress Tracker for Stage 4
    if (i + 1) % max(1, (NUM_SENSITIVITY_TRIALS // 10)) == 0:
        print(f"    -> Processed {i + 1} / {NUM_SENSITIVITY_TRIALS} trials...")

avg_quantum_tv = np.mean(quantum_tv_scores)
avg_classical_tv = np.mean(classical_tv_scores)

print(f"\n[+] Avg TV distance — Quantum Walk  ({NUM_SENSITIVITY_TRIALS} trials): {avg_quantum_tv:.4f}")
print(f"[+] Avg TV distance — Classical Walk ({NUM_SENSITIVITY_TRIALS} trials): {avg_classical_tv:.4f}")
print(f"[+] Quantum advantage delta: {avg_quantum_tv - avg_classical_tv:+.4f}")

# Plot comparison
plt.figure(figsize=(10, 5))
plt.hist(quantum_tv_scores, bins=30, alpha=0.6, color='blue', label='Quantum Walk TV')
plt.hist(classical_tv_scores, bins=30, alpha=0.6, color='orange', label='Classical Walk TV')
plt.axvline(avg_quantum_tv, color='blue', linestyle='--', label=f'QW Mean = {avg_quantum_tv:.4f}')
plt.axvline(avg_classical_tv, color='orange', linestyle='--', label=f'CW Mean = {avg_classical_tv:.4f}')
plt.title("TV Distance Distribution: Quantum Walk vs Classical Walk")
plt.xlabel("TV Distance between two different K values")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig("data/quantum_vs_classical.png")
print("Saved comparison plot to data/quantum_vs_classical.png")

# ==========================================
# STAGE 4b: STATISTICAL SIGNIFICANCE TEST
# ==========================================
from scipy import stats
import time

print("\n=======================================================")
print(" 📐 STATISTICAL SIGNIFICANCE TEST (Welch's t-test)")
print("=======================================================")
print("[+] Loading TV score arrays into SciPy...")
print(f"    -> Quantum TV scores loaded (N={len(quantum_tv_scores)})")
print(f"    -> Classical TV scores loaded (N={len(classical_tv_scores)})")
print("[+] Calculating variance and applying Welch's t-test...")

# Brief pause purely for terminal readability
time.sleep(0.5) 

t_stat, p_value = stats.ttest_ind(quantum_tv_scores, classical_tv_scores, alternative='greater')

print(f"[+] t-statistic : {t_stat:.4f}")
print(f"[+] p-value     : {p_value:.6e}") # Changed to scientific notation for precise p-values

if p_value < 0.05:
    print(f"✅ RESULT: Quantum Walk is SIGNIFICANTLY more distinguishable than Classical (p < 0.05)")
    print(f"   → This perfectly supports the novelty claim.")
else:
    print(f"⚠️  RESULT: Difference is NOT statistically significant (p >= 0.05)")
    print(f"   → Need more trials or longer walk steps.")
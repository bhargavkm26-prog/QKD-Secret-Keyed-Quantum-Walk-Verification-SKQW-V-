import random
import numpy as np
from core.skqw_engine import get_theoretical_distribution
from rx_node.verification_layer import verify_session

def classical_prf_stand_in(K: str, shots: int):
    """
    Stage 4: Classical stand-in for benchmarking.
    Simulates a classical random walk with matching per-step probabilities but NO interference.
    """
    np.random.seed(int(K, 2))
    outcomes = []
    for _ in range(shots):
        # Fake a classical binomial distribution output
        outcomes.append(format(np.random.randint(0, 16), '04b'))
    
    counts = {x: outcomes.count(x) for x in set(outcomes)}
    return {state: count / shots for state, count in counts.items()}

def simulate_eve_leakage(K_real: str, n_sessions: int, rounds_per_session: int = 500):
    """
    Stage 5: Transcript accumulation for N_max(ε) derivation.
    Measures how Eve's ability to guess K improves as she watches the public transcripts.
    """
    print(f"--- Simulating Leakage over {n_sessions} Sessions ---")
    
    # Alice's offline prediction based on the true secret K
    alice_dist = get_theoretical_distribution(K_real)
    
    transcript = []
    
    for session in range(n_sessions):
        # Eve guesses a random K and intercepts/resends
        K_eve = format(random.randint(0, (1 << len(K_real)) - 1), f'0{len(K_real)}b')
        eve_dist = get_theoretical_distribution(K_eve, shots=rounds_per_session)
        
        # Simulate Bob measuring Eve's tampered states
        bob_outcomes = random.choices(list(eve_dist.keys()), weights=list(eve_dist.values()), k=rounds_per_session)
        
        # Public verification
        passed, tv_dist, bound = verify_session(alice_dist, bob_outcomes)
        transcript.append({'session': session, 'passed': passed, 'eve_guess': K_eve, 'tv_dist': tv_dist})
        
        if passed and K_eve != K_real:
            print(f"🚨 FALSE NEGATIVE at Session {session}: Eve guessed {K_eve} and bypassed the bound!")
            
    return transcript

# Example Run
if __name__ == "__main__":
    SECRET_K = "101"
    
    # Run the distinguishability metric and leakage simulator
    log = simulate_eve_leakage(SECRET_K, n_sessions=50)
    print("Simulation complete. Transcript generated for analysis.")
import numpy as np

def calculate_tv_distance(predicted: dict, observed: dict) -> float:
    """Calculates the Total Variation (TV) distance between distributions."""
    all_states = set(predicted.keys()).union(set(observed.keys()))
    tv_dist = 0.5 * sum(abs(predicted.get(state, 0) - observed.get(state, 0)) for state in all_states)
    return tv_dist

def verify_session(predicted_dist: dict, bob_outcomes: list, confidence_level: float = 0.05) -> tuple:
    """
    Uses Hoeffding's inequality to determine if the channel is clean.
    Returns (Passed: bool, TV_Distance: float, Bound: float)
    """
    n_rounds = len(bob_outcomes)
    if n_rounds == 0:
        return False, 1.0, 0.0
        
    observed_counts = {}
    for outcome in bob_outcomes:
        observed_counts[outcome] = observed_counts.get(outcome, 0) + 1
    observed_dist = {state: count / n_rounds for state, count in observed_counts.items()}
    
    tv_distance = calculate_tv_distance(predicted_dist, observed_dist)
    epsilon_bound = np.sqrt(np.log(2 / confidence_level) / (2 * n_rounds))
    
    passed = tv_distance <= epsilon_bound
    return passed, tv_distance, epsilon_bound
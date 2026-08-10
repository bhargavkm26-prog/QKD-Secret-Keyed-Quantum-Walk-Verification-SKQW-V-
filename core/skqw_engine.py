import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

THETA0 = np.pi / 2   
THETA1 = np.pi / 3   

def build_skqw_circuit(K: str) -> QuantumCircuit:
    """
    Constructs a multi-qubit walk where K selects the public coin rotations.
    """
    steps = len(K)
    pos_qubits = 2 * steps + 1
    qc = QuantumCircuit(1 + pos_qubits, 1 + pos_qubits)

    coin = 0
    pos = list(range(1, 1 + pos_qubits))
    mid = pos[len(pos) // 2]
    qc.x(mid)  # Walker starts centered

    for step in range(steps):
        # K dictates the coin rotation
        theta = THETA0 if K[step] == '0' else THETA1
        qc.ry(theta, coin)                      

        # Shift Operators
        for i in range(len(pos) - 1, 0, -1):     
            qc.ccx(coin, pos[i - 1], pos[i])
        qc.x(coin)
        for i in range(0, len(pos) - 1):         
            qc.ccx(coin, pos[i + 1], pos[i])
        qc.x(coin)

    # Measure BOTH coin and position to capture interference
    qc.measure(coin, 0)
    qc.measure(pos, range(1, 1 + pos_qubits))    
    return qc

def get_theoretical_distribution(K: str, shots: int = 10000):
    """Alice's offline prediction of the spatial interference histogram."""
    qc = build_skqw_circuit(K)
    
    # Restrict threads to prevent heavy CPU throttling during batch runs
    backend = AerSimulator(max_parallel_threads=4)
    counts = backend.run(qc, shots=shots).result().get_counts()
    
    total = sum(counts.values())
    return {state: count / total for state, count in counts.items()}
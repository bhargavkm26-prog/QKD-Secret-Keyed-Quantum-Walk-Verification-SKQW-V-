import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def quantum_walk_basis(shots=1):
    """
    True Quantum Walk random generator.
    Measures the coin AND the position register, and folds ALL of them
    together to decide the basis — so the walk's spread actually
    contributes to the randomness, instead of only the coin mattering.
    """
    # qubit 0 = coin, qubit 1 = LSB, qubit 2 = MSB
    qc = QuantumCircuit(3, 3)

    # Initialize position to |1⟩ = |01⟩
    qc.x(1)

    # ── WALK STEP 1 ──────────────────────────────────────────────────────
    qc.h(0)
    qc.ccx(0, 1, 2)       # Increment logic
    qc.cx(0, 1)

    qc.x(0)               # Decrement logic
    qc.x(1)
    qc.ccx(0, 1, 2)
    qc.x(1)
    qc.cx(0, 1)
    qc.x(0)

    # ── WALK STEP 2 ──────────────────────────────────────────────────────
    qc.h(0)
    qc.ccx(0, 1, 2)
    qc.cx(0, 1)

    qc.x(0)
    qc.x(1)
    qc.ccx(0, 1, 2)
    qc.x(1)
    qc.cx(0, 1)
    qc.x(0)

    # ── Measure the coin AND the position register ─────────────────────
    qc.measure([0, 1, 2], [0, 1, 2])

    backend = AerSimulator()
    job = backend.run(qc, shots=shots)
    counts = job.result().get_counts()

    chosen = list(counts.keys())[0]
    coin_bit = int(chosen[-1])            # qubit 0
    position_bits = chosen[:-1]           # qubits 1, 2

    # ── NEW: fold coin + both position qubits together ─────────────────
    parity = coin_bit ^ int(position_bits[0]) ^ int(position_bits[1])

    # Cryptographic Mapping Vector: parity 0 = '+', parity 1 = 'X'
    basis = '+' if parity == 0 else 'X'
    return basis, chosen


def get_quantum_random_basis(shots=1):
    basis, _ = quantum_walk_basis(shots=shots)
    return basis

from qiskit import QuantumCircuit
import qiskit.qasm2 as qasm2
from core import quantum_walk_rng 
from core.skqw_engine import build_skqw_circuit
import random

SECRET_K = "101" # Alice's private secret for the check rounds

def prepare_photons(num_photons=300):
    print("\n--- Tx NODE: PREPARING SKQW-V QUANTUM STATES ---")
    
    tx_bits = []
    tx_bases = []
    round_types = []  # 'D' = Data (BB84), 'C' = Check (SKQW)
    qasm_payloads = []

    for i in range(num_photons):
        # 30% chance to inject a verification Check round
        is_check_round = random.random() < 0.3 
        
        if is_check_round:
            round_types.append('C')
            tx_bits.append(None)  
            tx_bases.append(None)
            
            qc = build_skqw_circuit(SECRET_K)
            qasm_payloads.append(qasm2.dumps(qc))
            
        else:
            round_types.append('D')
            
            bit_choice = quantum_walk_rng.get_quantum_random_basis()
            bit = 1 if bit_choice == 'X' else 0
            basis = quantum_walk_rng.get_quantum_random_basis()
            
            tx_bits.append(bit)
            tx_bases.append(basis)

            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.x(0)
            if basis == 'X':
                qc.h(0)

            qasm_payloads.append(qasm2.dumps(qc))

    print(f"Photons successfully converted to QASM strings. (Total: {num_photons})")
    return qasm_payloads, tx_bits, tx_bases, round_types
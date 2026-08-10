from qiskit import QuantumCircuit
import qiskit.qasm2 as qasm2
from qiskit_aer import AerSimulator
from qiskit.primitives import StatevectorSampler as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from core import quantum_walk_rng

backend = AerSimulator(max_parallel_threads=4)

def measure_photons(qasm_payloads):
    print("\n--- Rx NODE: MEASURING PHOTONS LOCALLY ---")
    rx_bases = []
    circuits_to_run = []
    
    for qasm_string in qasm_payloads:
        qc = qasm2.loads(qasm_string)
        
        # If the circuit is single-qubit, it's BB84 data. Apply basis guess.
        if qc.num_qubits == 1:
            basis = quantum_walk_rng.get_quantum_random_basis()
            rx_bases.append(basis)
            if basis == 'X':
                qc.h(0)
            qc.measure_all()
        else:
            # It's a check round (already contains measurement instructions)
            rx_bases.append(None) 
            
        circuits_to_run.append(qc)

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuits = pm.run(circuits_to_run)

    sampler = Sampler()
    job = sampler.run(isa_circuits)
    result = job.result()

    measured_outcomes = []
    for pub_result in result:
        counts = pub_result.data.meas.get_counts() if hasattr(pub_result.data, 'meas') else pub_result.data.c.get_counts()
        measured_outcomes.append(list(counts.keys())[0])

    return rx_bases, measured_outcomes

def sift_keys(tx_bases, rx_bases, measured_outcomes, round_types):
    final_key = []
    for i in range(len(round_types)):
        if round_types[i] == 'D':
            if tx_bases[i] == rx_bases[i]:
                # Extract the single bit integer for data rounds
                final_key.append(int(measured_outcomes[i]))
    return final_key
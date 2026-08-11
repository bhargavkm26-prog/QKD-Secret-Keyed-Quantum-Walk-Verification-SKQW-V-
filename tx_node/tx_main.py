import socket
import json
import time
import sys
from tx_node import qiskit_sender   
from crypto import aes_encryption     
from core.skqw_engine import get_theoretical_distribution
from tx_node.qiskit_sender import SECRET_K

IP_ADDRESS = "127.0.0.1"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5002

def start_transmitter():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((IP_ADDRESS, PORT))
        print("[Tx NODE] Network Connection Established!")
        
        # 1. Generate REAL & CHECK quantum circuits (Minimum 300 to beat shot noise)
        qasm_payloads, tx_bits, tx_bases, round_types = qiskit_sender.prepare_photons(num_photons=300)
        
        # 2. Send Quantum Payload
        client_socket.send(json.dumps(qasm_payloads).encode('utf-8'))
        time.sleep(1)
        
        # 3. Receive Rx's Bases
        rx_bases = json.loads(client_socket.recv(8192).decode('utf-8'))
        
        # 4. Reveal Round Types and Tx Bases
        revelation = {"tx_bases": tx_bases, "round_types": round_types}
        client_socket.send(json.dumps(revelation).encode('utf-8'))
        
        # 5. Send Theoretical Distribution for the Hoeffding Check
        theoretical_dist = get_theoretical_distribution(SECRET_K)
        client_socket.send(json.dumps(theoretical_dist).encode('utf-8'))

        # Sift the key locally
        final_key = [tx_bits[i] for i in range(len(tx_bases)) if round_types[i] == 'D' and tx_bases[i] == rx_bases[i]]
        
       # Wait for Bob's Hoeffding security report
        status = client_socket.recv(1024).decode('utf-8')
        
        print("\n=======================================================")
        print(" 📡 VERIFICATION VERDICT RECEIVED FROM BOB")
        print("=======================================================")
        
        if status == "BREACH":
            print("🚨 VERDICT: EAVESDROPPER DETECTED!")
            print("🚨 ACTION : Aborting AES Encryption. Discarding compromised key.")
            print("=======================================================\n")
            sys.exit(1)

        else:
            print("✅ VERDICT: Channel Secure (Hoeffding Bound Satisfied).")
            print("✅ ACTION : Proceeding to AES-256 Data Encryption.")
            print("=======================================================\n")
            
        
            
        # AES Encryption[cite: 1]
        aes_key = aes_encryption.generate_aes_key(final_key)
        ciphertext = aes_encryption.encrypt_file(aes_key, "data/secret_data.txt")
        client_socket.send(ciphertext)

    finally:
        client_socket.close()

if __name__ == "__main__":
    start_transmitter()
# import socket
# import json
# import time
# import sys
# from tx_node import qiskit_sender   
# from crypto import aes_encryption     
# from core.skqw_engine import get_theoretical_distribution
# from tx_node.qiskit_sender import SECRET_K

# IP_ADDRESS = "127.0.0.1"
# PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5002

# def start_transmitter():
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         client_socket.connect((IP_ADDRESS, PORT))
#         print("[Tx NODE] Network Connection Established!")
        
#         # 1. Generate REAL & CHECK quantum circuits (Minimum 300 to beat shot noise)
#         qasm_payloads, tx_bits, tx_bases, round_types = qiskit_sender.prepare_photons(num_photons=300)
        
#         # 2. Send Quantum Payload
#         client_socket.send(json.dumps(qasm_payloads).encode('utf-8'))
#         time.sleep(1)
        
#         # 3. Receive Rx's Bases
#         rx_bases = json.loads(client_socket.recv(8192).decode('utf-8'))
        
#         # 4. Reveal Round Types and Tx Bases
#         revelation = {"tx_bases": tx_bases, "round_types": round_types}
#         client_socket.send(json.dumps(revelation).encode('utf-8'))
        
#         # 5. Send Theoretical Distribution for the Hoeffding Check
#         theoretical_dist = get_theoretical_distribution(SECRET_K)
#         client_socket.send(json.dumps(theoretical_dist).encode('utf-8'))

#         # Sift the key locally
#         final_key = [tx_bits[i] for i in range(len(tx_bases)) if round_types[i] == 'D' and tx_bases[i] == rx_bases[i]]
        
#        # Wait for Bob's Hoeffding security report
#         status = client_socket.recv(1024).decode('utf-8')
        
#         print("\n=======================================================")
#         print(" 📡 VERIFICATION VERDICT RECEIVED FROM BOB")
#         print("=======================================================")
        
#         if status == "BREACH":
#             print("🚨 VERDICT: EAVESDROPPER DETECTED!")
#             print("🚨 ACTION : Aborting AES Encryption. Discarding compromised key.")
#             print("=======================================================\n")
#             sys.exit(1)

#         else:
#             print("✅ VERDICT: Channel Secure (Hoeffding Bound Satisfied).")
#             print("✅ ACTION : Proceeding to AES-256 Data Encryption.")
#             print("=======================================================\n")
            
        
            
#         # AES Encryption[cite: 1]
#         aes_key = aes_encryption.generate_aes_key(final_key)
#         ciphertext = aes_encryption.encrypt_file(aes_key, "data/secret_data.txt")
#         client_socket.send(ciphertext)

#     finally:
#         client_socket.close()

# if __name__ == "__main__":
#     start_transmitter()


import socket
import json
import time
import sys
from tx_node import qiskit_sender   
from crypto import aes_encryption     
from core.skqw_engine import get_theoretical_distribution
from rx_node.verification_layer import verify_session
from tx_node.qiskit_sender import SECRET_K

IP_ADDRESS = "127.0.0.1"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5002

def start_transmitter():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((IP_ADDRESS, PORT))
        print("[Tx NODE] Network Connection Established!")
        
        # 1. Generate REAL & CHECK quantum circuits
        qasm_payloads, tx_bits, tx_bases, round_types = qiskit_sender.prepare_photons(num_photons=300)
        
        # 2. Send Quantum Payload
        client_socket.send(json.dumps(qasm_payloads).encode('utf-8'))
        time.sleep(1)
        
        # 3. Receive Rx's Bases
        rx_bases = json.loads(client_socket.recv(8192).decode('utf-8'))
        
        # 4. Reveal Round Types and Tx Bases
        revelation = {"tx_bases": tx_bases, "round_types": round_types}
        client_socket.send(json.dumps(revelation).encode('utf-8'))
        
        # 5. SECURITY FIX: K and its predicted distribution NEVER leave
        # Alice's machine. Compute the prediction privately here.
        theoretical_dist = get_theoretical_distribution(SECRET_K)

        # Sift the key locally
        final_key = [tx_bits[i] for i in range(len(tx_bases)) if round_types[i] == 'D' and tx_bases[i] == rx_bases[i]]

        # 6. Receive Bob's raw check-round outcomes (not a prediction)
        check_data = client_socket.recv(16384).decode('utf-8')
        check_outcomes = json.loads(check_data)

        print("\n=======================================================")
        print(" 🔍 SECURITY CHECK: LIVE STATISTICAL VERIFICATION (Alice-side)")
        print("=======================================================")
        print(f"[+] Received {len(check_outcomes)} raw check-round outcomes from Bob.")

        passed, tv_dist, bound = verify_session(theoretical_dist, check_outcomes)

        print("\n[+] Calculating Total Variation (TV) Distance...")
        print(f"    Result : {tv_dist:.4f}")
        print("\n[+] Calculating Hoeffding Bound (Epsilon)...")
        print(f"    Result : {bound:.4f}")
        
        print("\n-------------------------------------------------------")
        if not passed:
            print(f"🚨 [CRITICAL ALERT] HOEFFDING BOUND BREACHED ({tv_dist:.4f} > {bound:.4f})")
            print("🚨 Aborting: sending BREACH verdict to Bob.")
            print("=======================================================\n")
            client_socket.send("BREACH".encode('utf-8'))
            sys.exit(1)
        else:
            print(f"✅ [VERIFIED] TV Distance ({tv_dist:.4f}) is strictly <= Bound ({bound:.4f})")
            print("✅ Sending SAFE verdict to Bob.")
            print("=======================================================\n")
            client_socket.send("SAFE".encode('utf-8'))
            
        # AES Encryption
        aes_key = aes_encryption.generate_aes_key(final_key)
        ciphertext = aes_encryption.encrypt_file(aes_key, "data/secret_data.txt")
        client_socket.send(ciphertext)

    finally:
        client_socket.close()

if __name__ == "__main__":
    start_transmitter()
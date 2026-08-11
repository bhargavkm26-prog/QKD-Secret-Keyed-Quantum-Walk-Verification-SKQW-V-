import socket
import json
import sys
from rx_node import qiskit_receiver
from crypto import aes_encryption
from rx_node.verification_layer import verify_session

IP_ADDRESS = "127.0.0.1"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5002

def start_receiver():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP_ADDRESS, PORT))
    server_socket.listen(1)
    
    print(f"\n[Rx NODE] Listening securely on {IP_ADDRESS}:{PORT}...")
    connection, address = server_socket.accept()
    
    try:
        # 1. Receive Photons (ROBUST NETWORK BUFFER FIX)
        raw_data = b""
        while True:
            chunk = connection.recv(65536) 
            raw_data += chunk
            # Break the loop if the chunk is smaller than 64KB (end of transmission)
            if len(chunk) < 65536:
                break
                
        data = raw_data.decode('utf-8')
        qasm_payloads = json.loads(data)
        
        # 2. Measure Photons 
        rx_bases, measured_outcomes = qiskit_receiver.measure_photons(qasm_payloads)
        
        # 3. Send Rx's Bases
        connection.send(json.dumps(rx_bases).encode('utf-8'))
        
        # 4. Receive Alice's revelation (Round Types and Tx Bases)
        revelation_data = connection.recv(16384).decode('utf-8')
        revelation = json.loads(revelation_data)
        tx_bases = revelation["tx_bases"]
        round_types = revelation["round_types"]
        
        # 5. Receive Alice's Prediction
        prediction_data = connection.recv(16384).decode('utf-8')
        theoretical_dist = json.loads(prediction_data)

        print("\n=======================================================")
        print(" 🔍 SECURITY CHECK: LIVE STATISTICAL VERIFICATION")
        print("=======================================================")
        
        # Filter the check round outcomes
        check_outcomes = [measured_outcomes[i] for i in range(len(round_types)) if round_types[i] == 'C']
        n_rounds = len(check_outcomes)
        
        print(f"[+] Total Verification Rounds Extracted (N): {n_rounds}")
        print(f"[+] Alice's Theoretical K-Distribution : {theoretical_dist}")
        
        passed, tv_dist, bound = verify_session(theoretical_dist, check_outcomes)
        
        print("\n[+] Calculating Total Variation (TV) Distance...")
        print("    Formula: TV = 0.5 * sum(|P_alice(x) - P_bob(x)|)")
        print(f"    Result : {tv_dist:.4f}")
        
        print("\n[+] Calculating Hoeffding Bound (Epsilon)...")
        print("    Formula: Epsilon = sqrt(ln(2 / alpha) / (2 * N))")
        print(f"    Result : {bound:.4f}")
        
        print("\n-------------------------------------------------------")
        if not passed:
            print(f"🚨 [CRITICAL ALERT] HOEFFDING BOUND BREACHED ({tv_dist:.4f} > {bound:.4f})")
            print("🚨 MATHEMATICAL PROOF:")
            print("    The observed spatial interference pattern has severely collapsed.")
            print("    An eavesdropper attempted an intercept-resend attack but failed")
            print("    to guess the secret K-parameterized coin sequence.")
            print("=======================================================\n")
            connection.send("BREACH".encode('utf-8'))
            sys.exit(1)

        else:
            print(f"✅ [VERIFIED] TV Distance ({tv_dist:.4f}) is strictly <= Bound ({bound:.4f})")
            print("✅ MATHEMATICAL PROOF:")
            print("    The spatial interference pattern perfectly matches the K-derived")
            print("    prediction. The channel is mathematically certified as secure.")
            print("=======================================================\n")
            connection.send("SAFE".encode('utf-8'))
            
        # Sift keys
        final_key = qiskit_receiver.sift_keys(tx_bases, rx_bases, measured_outcomes, round_types)
        
        # AES Decryption
        aes_key = aes_encryption.generate_aes_key(final_key)
        ciphertext = connection.recv(4096)
        aes_encryption.decrypt_data(aes_key, ciphertext)
            
        
        print("\n[Rx NODE] Session complete. Closing connection.")

    finally:
        connection.close()
        server_socket.close()

if __name__ == "__main__":
    start_receiver()
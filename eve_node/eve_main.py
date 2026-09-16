import socket
import json
import random
import qiskit.qasm2 as qasm2
from core.skqw_engine import build_skqw_circuit

TX_PORT = 5002  # Eve listens here for Alice
RX_PORT = 5003  # Eve secretly forwards to Bob here
IP_ADDRESS = "127.0.0.1"

def start_eve():
    # 1. Setup server to intercept Alice
    eve_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    eve_server.bind((IP_ADDRESS, TX_PORT))
    eve_server.listen(1)
    
    print(f"🦹 [EVE NODE] Online. Intercepting traffic on {IP_ADDRESS}:{TX_PORT}...")
    alice_conn, _ = eve_server.accept()
    print("🦹 [EVE NODE] Alice connected! Hijacking transmission...")

    # 2. Secretly connect to Bob
    bob_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bob_conn.connect((IP_ADDRESS, RX_PORT))
    print("🦹 [EVE NODE] Secretly connected to Bob!")

    try:
        # 3. Intercept Photons from Alice
        raw_data = b""
        while True:
            chunk = alice_conn.recv(65536) 
            raw_data += chunk
            if len(chunk) < 65536:
                break
        
        qasm_payloads = json.loads(raw_data.decode('utf-8'))
        print(f"🦹 [EVE NODE] Intercepted {len(qasm_payloads)} quantum circuits!")
        
        # ==========================================
        # 😈 THE ATTACK (INTERCEPT-RESEND)
        # ==========================================
        print("\n=======================================================")
        print(" 😈 INITIATING INTERCEPT-RESEND ATTACK")
        print("=======================================================")
        print("🦹 [!] BLIND SPOT: Eve does not possess the secret bitstring K.")
        print("🦹 [!] Eve cannot distinguish BB84 data from SKQW verification rounds.")
        
        FAKE_K = "000"
        print(f"🦹 [!] Guessing K = '{FAKE_K}' to blindly forge quantum walk states...")
        
        attacked_count = 0
        for i in range(len(qasm_payloads)):
            if random.random() < 0.5:
                fake_qc = build_skqw_circuit(FAKE_K)
                qasm_payloads[i] = qasm2.dumps(fake_qc)
                attacked_count += 1
                
        print(f"🦹 Attack complete! Forged {attacked_count} states with the wrong K.")
        print("🦹 Forwarding tampered states to Bob...\n")
        
        # 4. Forward tampered states to Bob
        bob_conn.send(json.dumps(qasm_payloads).encode('utf-8'))
        
        # 5. Act as a transparent bridge for the classical verification
        # Bob sends bases -> Eve forwards to Alice
        alice_conn.send(bob_conn.recv(65536))

        # Alice sends Revelation (tx_bases, round_types) -> Eve forwards to Bob
        bob_conn.send(alice_conn.recv(65536))

        # Bob sends RAW check-round outcomes -> Eve forwards to Alice
        # K and its distribution never cross the wire — Eve only sees measurements
        check_data = bob_conn.recv(65536)
        print(f"🦹 [EVE NODE] Intercepted Bob's raw check-round outcomes ({len(check_data)} bytes)")
        alice_conn.send(check_data)

        # Alice sends her verdict ("SAFE" or "BREACH") -> Eve forwards to Bob
        verdict = alice_conn.recv(1024)
        print(f"🦹 [EVE NODE] Intercepted Alice's verdict: {verdict.decode('utf-8')}")
        bob_conn.send(verdict)

        # If safe, Alice sends AES ciphertext -> Eve forwards to Bob
        if verdict.decode('utf-8') != "BREACH":
            bob_conn.send(alice_conn.recv(65536))

    except Exception as e:
        print(f"🦹 [EVE NODE] Error: {e}")
    finally:
        alice_conn.close()
        bob_conn.close()
        eve_server.close()
        print("🦹 [EVE NODE] Shutting down.")

if __name__ == "__main__":
    start_eve()
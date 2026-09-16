import sys
import subprocess
import time
import json
import os

NUM_SESSIONS = 10
TRANSCRIPT_FILE = "data/session_transcript.json"

print("=======================================================")
print(f" 📂 STAGE 3: GENERATING PERSISTENT-K TRANSCRIPT T_n")
print(f"    Target Sessions (n): {NUM_SESSIONS}")
print("=======================================================")

transcript = {
    "secret_k_reused": "101",
    "total_sessions": NUM_SESSIONS,
    "sessions": []
}

for session_id in range(1, NUM_SESSIONS + 1):
    print(f"\n[Session {session_id}/{NUM_SESSIONS}] Launching secure handshake...")
    
    # Start Bob (Receiver) in the background on port 5002
    rx_process = subprocess.Popen([sys.executable, '-m', 'rx_node.rx_main', '5002'])
    time.sleep(1.5)  # Allow socket to bind
    
    # Start Alice (Transmitter) in the background on port 5002
    tx_process = subprocess.Popen([sys.executable, '-m', 'tx_node.tx_main', '5002'])
    
    # Wait for both nodes to finish execution
    tx_process.wait()
    rx_process.wait()
    
    # Read the ACTUAL exit code from Bob (rx_main)
    # rx_main exits with sys.exit(1) on BREACH, sys.exit(0) on success
    rx_exit_code = rx_process.returncode
    verdict = "BREACH" if rx_exit_code != 0 else "PASS"

    transcript["sessions"].append({
        "session_id": session_id,
        "verdict": verdict,
        "rx_exit_code": rx_exit_code,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    print(f"[Session {session_id}] Result Recorded -> {verdict} (exit code: {rx_exit_code})")

    time.sleep(1)

# Ensure data directory exists and save transcript T_n
os.makedirs("data", exist_ok=True)
with open(TRANSCRIPT_FILE, "w") as f:
    json.dump(transcript, f, indent=4)

print("\n=======================================================")
print(f"✅ TRANSCRIPT T_n GENERATED SUCCESSFULLY")
print(f"📂 Saved to: {TRANSCRIPT_FILE}")
print("=======================================================\n")
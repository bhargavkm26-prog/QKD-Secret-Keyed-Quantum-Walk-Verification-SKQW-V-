import subprocess
import time

print("========================================")
print("  SKQW-V Quantum Security Simulator")
print("========================================")

# The Switch
attack = input("Turn Eve Attack ON? (y/n): ").strip().lower()

if attack == 'y':
    print("\n[+] Eve is ON. Launching 3 terminals automatically...")
    
    # 1. Start Bob on port 5003
    subprocess.Popen('start "Rx Node (Bob)" cmd /k "py -m rx_node.rx_main 5003"', shell=True)
    time.sleep(4)
    
    # 2. Start Eve (Listens on 5002, intercepts, and forwards to Bob on 5003)
    subprocess.Popen('start "Eve Node (Attacker)" cmd /k "py -m eve_node.eve_main"', shell=True)
    time.sleep(4)
    
    # 3. Start Alice (Dials 5002, walking straight into Eve's trap)
    subprocess.Popen('start "Tx Node (Alice)" cmd /k "py -m tx_node.tx_main 5002"', shell=True)

else:
    print("\n[+] Eve is OFF. Launching secure 2-way channel...")
    
    # 1. Start Bob on port 5002
    subprocess.Popen('start "Rx Node (Bob)" cmd /k "py -m rx_node.rx_main 5002"', shell=True)
    time.sleep(4)
    
    # 2. Start Alice (Dials Bob directly on 5002)
    subprocess.Popen('start "Tx Node (Alice)" cmd /k "py -m tx_node.tx_main 5002"', shell=True)

print("\n[!] Execution handed over to the popup terminals. You can close this window when done.")
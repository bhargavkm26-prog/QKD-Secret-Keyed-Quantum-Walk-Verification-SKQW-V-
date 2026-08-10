import hashlib
import base64
from cryptography.fernet import Fernet

def generate_aes_key(quantum_bits):
    """
    Takes the final matching quantum bits (0s and 1s) from the BB84 protocol
    and mathematically hashes them into a perfect 256-bit AES key.
    """
    print("\n--- CRYPTOGRAPHY: HASHING QUANTUM KEY ---")
    
    # 1. Convert the list of integers [0, 1, 1, 0...] into a single string "0110..."
    bit_string = "".join(str(bit) for bit in quantum_bits)
    print(f"Raw Quantum Bit String: {bit_string}")
    
    # 2. Use SHA-256 to hash the string into a secure, uniform byte signature
    hashed_bytes = hashlib.sha256(bit_string.encode()).digest()
    
    # 3. Fernet (AES) requires the key to be Base64 encoded, so we format it
    aes_key = base64.urlsafe_b64encode(hashed_bytes)
    print(f"Generated 256-bit AES Key: {aes_key.decode()}")
    
    return aes_key

def encrypt_file(aes_key, filename):
    """
    Reads a plaintext file and encrypts it using the AES key.
    """
    print(f"\n--- CRYPTOGRAPHY: ENCRYPTING {filename} ---")
    cipher_suite = Fernet(aes_key)
    
    # Read the secret data
    with open(filename, 'rb') as file:
        plaintext = file.read()
        
    # Encrypt it
    ciphertext = cipher_suite.encrypt(plaintext)
    print("\n--- 🔐 SENDER CRYPTOGRAPHY LOG ---")
    print(f"Generated AES Key : {aes_key}")
    print(f"Ciphertext Sent   : {ciphertext}")
    print("----------------------------------\n")
    
    return ciphertext

def decrypt_data(aes_key, ciphertext):
    """
    Takes the incoming scrambled Ciphertext and unlocks it with the AES key.
    """
    # print("\n--- CRYPTOGRAPHY: DECRYPTING DATA ---")
    cipher_suite = Fernet(aes_key)
    
    try:
        # Decrypt the data
        plaintext_bytes = cipher_suite.decrypt(ciphertext)
        # print(f"Decrypted Bytes: {plaintext_bytes}")
        plaintext = plaintext_bytes.decode('utf-8')
        
        
        print("\n--- 🔓 RECEIVER CRYPTOGRAPHY LOG ---")
        print(f"Received Ciphertext : {ciphertext}")
        print(f"Derived AES Key     : {aes_key}")
        print(f"Decoded Message     : {plaintext}")
        print("------------------------------------\n") 
        return plaintext
        
    except Exception as e:
        print("\n[CRITICAL ERROR] Decryption failed! The Quantum Keys do not match. Eavesdropper detected!")
        return None
import os
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class KMS:
    """
    Key Management Service (KMS).
    Responsible for generating, storing, and providing the master AES-256 key
    and generating HMAC-SHA256 tokens for authentication.
    """
    def __init__(self, key_file="master.key"):
        self.key_file = key_file
        self.key = self._load_or_generate_key()

    def _load_or_generate_key(self):
        """Loads an existing 256-bit key or generates a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            # Generate a 256-bit (32 bytes) random key for AES-256
            new_key = os.urandom(32)
            with open(self.key_file, "wb") as f:
                f.write(new_key)
            return new_key

    def get_key(self):
        """Returns the AES-256 master key."""
        return self.key

    def generate_mac(self, file_id: str, operation: str, timestamp: str) -> str:
        """
        Generates a Message Authentication Code (MAC) using HMAC-SHA256.
        Formula: MAC = H(Key || File_ID || Operation || Timestamp)
        """
        # Concatenate the message components
        message = f"{file_id}|{operation}|{timestamp}".encode('utf-8')
        
        # Create HMAC using SHA-256
        mac = hmac.new(self.key, message, hashlib.sha256).hexdigest()
        return mac

    def verify_mac(self, file_id: str, operation: str, timestamp: str, provided_mac: str) -> bool:
        """
        Verifies if the provided MAC is valid for the given parameters.
        """
        expected_mac = self.generate_mac(file_id, operation, timestamp)
        # Use hmac.compare_digest to prevent timing attacks
        return hmac.compare_digest(expected_mac, provided_mac)


class CryptoEngine:
    """
    Cryptographic Engine for file encryption and decryption using AES-256 in CBC mode.
    """
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Invalid key length. AES-256 requires a 32-byte key.")
        self.key = key
        self.backend = default_backend()

    def encrypt(self, data: bytes) -> bytes:
        """Encrypts data using AES-256-CBC with PKCS7 padding."""
        # Generate a random 16-byte Initialization Vector (IV)
        iv = os.urandom(16)
        
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        # Apply PKCS7 padding to ensure the data is a multiple of the block size (128 bits / 16 bytes)
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt the padded data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Prepend the IV to the ciphertext so it can be extracted during decryption
        return iv + ciphertext

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypts AES-256-CBC encrypted data."""
        if len(encrypted_data) < 16:
            raise ValueError("Encrypted data is too short to contain an IV.")
            
        # Extract the 16-byte IV from the beginning
        iv = encrypted_data[:16]
        actual_ciphertext = encrypted_data[16:]
        
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        
        # Decrypt the data
        padded_data = decryptor.update(actual_ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data

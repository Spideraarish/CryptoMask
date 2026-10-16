import os
import time
from kms_core import KMS, CryptoEngine
from access_controller import AccessController

def create_dummy_files(target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for i in range(1, 6):
        with open(os.path.join(target_dir, f"document_{i}.txt"), "w") as f:
            f.write(f"CONFIDENTIAL DATA PAYLOAD {i}\n" * 50)

def legitimate_process(controller: AccessController) -> dict:
    target_dir = controller.watch_dir
    kms = KMS()
    engine = CryptoEngine(kms.get_key())
    
    file_id = "document_1.txt"
    filepath = os.path.join(target_dir, file_id)
    
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            data = f.read()
    else:
        data = b"Legitimate data payload"
        
    encrypted_data = engine.encrypt(data)
    
    operation = "WRITE_ENCRYPTED"
    timestamp = str(int(time.time()))
    mac = kms.generate_mac(file_id, operation, timestamp)
    
    # Request write and capture response
    result = controller.request_write(filepath, encrypted_data, operation, timestamp, mac)
    
    return {
        "process_name": "Legitimate Application",
        "file_target": file_id,
        "mac_generated": mac,
        "interceptor_result": result
    }

def ransomware_simulator(controller: AccessController) -> dict:
    target_dir = controller.watch_dir
    
    # Attacker uses own key
    rogue_key = os.urandom(32)
    rogue_engine = CryptoEngine(rogue_key)
    
    file_id = "document_2.txt"
    filepath = os.path.join(target_dir, file_id)
    
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            data = f.read()
    else:
        data = b"Target data payload"
        
    encrypted_data = rogue_engine.encrypt(data)
    
    operation = "WRITE_ENCRYPTED"
    timestamp = str(int(time.time()))
    fake_mac = "4a1d4b6e" + "0" * 56 # Invalid MAC structure
    
    result = controller.request_write(filepath, encrypted_data, operation, timestamp, fake_mac)
    
    return {
        "process_name": "Ransomware.exe",
        "file_target": file_id,
        "mac_generated": fake_mac,
        "interceptor_result": result
    }

# 🔐 CryptoMask : Cryptographic Access-Control Framework

> **A research-grade cybersecurity simulator** that demonstrates how cryptographic authentication can detect and block ransomware attacks at the file-system level in real time.

---

## 📌 Overview

**CryptoMask** is a Python-based security framework that simulates a cryptographic access-control layer between processes and the file system. It uses **AES-256 encryption** and **HMAC-SHA256 message authentication** to verify the legitimacy of any write request before it is allowed to reach protected files.

The project includes:
- A **Flask web app** for interactive simulation via browser
- A **Tkinter desktop dashboard** with live event logging
- A **Shannon Entropy Engine** to mathematically distinguish encrypted ransomware payloads from normal files
- A **cryptographic benchmarking tool** to prove real-time feasibility

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| 🔑 **Key Management Service (KMS)** | Generates and persists a 256-bit AES master key; issues HMAC-SHA256 tokens |
| 🛡️ **Access Controller** | OS-level file system interceptor that validates MAC before allowing writes |
| 🔒 **AES-256-CBC Encryption** | All authorized writes are encrypted with a random IV per operation |
| 📊 **Shannon Entropy Engine** | Calculates byte-level entropy to detect ransomware encryption (H > 7.5 threshold) |
| 🌐 **Web Dashboard (Flask)** | Browser-based simulation of legitimate vs. ransomware write attempts |
| 🖥️ **Desktop Dashboard (Tkinter)** | Real-time GUI with live terminal logs, watchdog integration, and attack alerts |
| ⚡ **Performance Benchmark** | Measures AES-256 + HMAC throughput to prove negligible overhead |

---

## 🏗️ Architecture

```
CryptoMask/
├── app.py               # Flask web server (browser UI)
├── dashboard.py         # Tkinter desktop dashboard (GUI)
├── kms_core.py          # Key Management Service + CryptoEngine (AES-256-CBC)
├── access_controller.py # File system interceptor with HMAC validation
├── entropy_engine.py    # Shannon entropy calculator and threshold proof
├── simulators.py        # Legitimate process & ransomware simulators
├── benchmark.py         # AES-256 + HMAC throughput benchmarking
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html       # Web UI template
├── static/              # CSS / JS assets for web UI
└── Dummy_Files/         # Protected directory watched by AccessController
```

---

## 🔬 How It Works

### 1. Key Management Service (KMS)
The KMS generates (or loads) a persistent **256-bit master key** stored in `master.key`. For every authorized write, it produces a **HMAC-SHA256 token** derived from:

```
MAC = HMAC-SHA256(MasterKey, FileID | Operation | Timestamp)
```

### 2. Access Controller (File System Interceptor)
Before any write reaches a protected file, the `AccessController` intercepts the request and:
1. Independently computes the **expected MAC** using the master key
2. Compares it against the **provided MAC** using `hmac.compare_digest()` (timing-safe)
3. **Allows** the write if they match ✅ — **Blocks** the write if they don't ❌

### 3. Ransomware Simulation
A ransomware process uses its **own random key** to encrypt files and presents a **forged MAC**. Because it cannot access the master key, its MAC never matches — the write is blocked and the payload is discarded.

```
Legitimate Process  →  Valid HMAC   →  ✅ Write ALLOWED
Ransomware.exe      →  Forged HMAC  →  ❌ Write BLOCKED
```

### 4. Shannon Entropy Detection
The entropy engine proves mathematically why `H > 7.5` reliably flags ransomware:

| File Type | Entropy Score |
|---|---|
| Plain text | ~3.5 – 4.5 bits/byte |
| Compressed (ZIP) | ~7.0 – 7.5 bits/byte |
| AES-256 Encrypted | **~7.9 – 8.0 bits/byte** |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Spideraarish/CryptoMask.git
cd CryptoMask

# Create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the Web App (Recommended)

```bash
python app.py
```

Open your browser at **http://127.0.0.1:5001**

Choose a simulation context:
- **Legitimate** — Authorized process with valid HMAC → write is allowed
- **Ransomware** — Rogue process with forged HMAC → write is blocked

### Run the Desktop Dashboard

```bash
python dashboard.py
```

A dark-themed Tkinter GUI will open with three interactive buttons:
- ✅ Simulate Legitimate Process
- ⚠️ Simulate Ransomware Attack
- 📊 Run Entropy Benchmark Tests

### Run the Entropy Engine

```bash
python entropy_engine.py
```

Outputs entropy scores for text, compressed, and AES-encrypted data to prove the H > 7.5 detection threshold.

### Run the Performance Benchmark

```bash
python benchmark.py
```

Processes 1 GB of data in chunks, reporting AES-256 + HMAC throughput in MB/s to demonstrate real-time feasibility.

---

## 🔒 Security Design Decisions

- **`hmac.compare_digest()`** is used for MAC comparison to prevent timing-based side-channel attacks
- **Random IV per encryption** (prepended to ciphertext) ensures identical plaintexts produce different ciphertexts
- **PKCS7 padding** is applied before AES-CBC encryption to handle arbitrary-length inputs
- The master key is stored in binary form (`master.key`) — in production, this would reside in a hardware security module (HSM)

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `cryptography` | 42.0.5 | AES-256-CBC encryption & PKCS7 padding |
| `watchdog` | 4.0.0 | Real-time file system monitoring |
| `flask` | 3.0.0 | Web server for browser-based simulation |

---

## ⚠️ Disclaimer

This project is built **strictly for educational and research purposes**. The ransomware simulator does not cause any real harm — it only demonstrates how a cryptographic access-control layer can detect and neutralize such attacks. Do not use any part of this codebase for malicious purposes.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the **MIT License**.

---

*Built with 🔐 and Python — CryptoMask*

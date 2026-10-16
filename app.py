from flask import Flask, render_template, request, jsonify
from kms_core import KMS, CryptoEngine
from access_controller import AccessController
import os, time

app = Flask(__name__)
controller = AccessController()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process():
    context = request.form.get('context', 'legitimate')

    # Use uploaded file or fall back to a demo payload
    if 'file' in request.files and request.files['file'].filename != '':
        f = request.files['file']
        filename = f.filename
        data = f.read()
    else:
        filename  = "demo_document.txt"
        data      = b"This is a protected corporate document. Confidential."

    operation = "WRITE_ENCRYPTED"
    timestamp = str(int(time.time()))

    if context == 'legitimate':
        kms            = KMS()
        engine         = CryptoEngine(kms.get_key())
        encrypted      = engine.encrypt(data)
        mac_provided   = kms.generate_mac(filename, operation, timestamp)
        process_name   = "Authorized_Backup.exe"
    else:
        rogue_key      = os.urandom(32)
        engine         = CryptoEngine(rogue_key)
        encrypted      = engine.encrypt(data)
        # Ransomware uses a fake / guessed MAC
        mac_provided   = "4a1d4b6e" + "0" * 56
        process_name   = "RANSOM_CRYPT.exe"

    filepath = os.path.join(controller.watch_dir, filename)
    result   = controller.request_write(
        filepath=filepath,
        data=encrypted,
        operation=operation,
        timestamp=timestamp,
        provided_mac=mac_provided
    )

    return jsonify({
        "process_name":  process_name,
        "filename":      filename,
        "file_size":     len(data),
        "enc_size":      len(encrypted),
        "operation":     operation,
        "timestamp":     timestamp,
        "mac_provided":  mac_provided,
        "expected_mac":  result["expected_mac"],
        "status":        result["status"],
        "message":       result["message"],
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)

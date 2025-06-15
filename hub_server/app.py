import os
import time
import platform
import subprocess
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

ROOT_PASSWORD = "PASSWORD_HERE"
UPLOAD_CONFIG_PATH = "./uploads"

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return {"error": result.stderr.strip()}
        return {"output": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}

def get_current_ssid():
    system = platform.system()
    if system == "Linux":
        cmd = "nmcli -t -f active,ssid dev wifi | egrep '^yes' | cut -d\":\" -f2"
    else:
        return {"error": "Unsupported OS"}
    return run_command(cmd)

def scan_networks():
    system = platform.system()
    if system == "Linux":
        # Force a rescan and wait for results
        run_command("echo {} | nmcli device wifi rescan".format(ROOT_PASSWORD))
        time.sleep(2)  # Wait for scan to complete
        result = run_command("echo {} | sudo -S nmcli -t -f SSID dev wifi".format(ROOT_PASSWORD))
        if "output" in result:
            ssids = [ssid.strip() for ssid in result["output"].split('\n') if ssid and ssid.strip() != "--"]
            return {"ssids": sorted(list(set(ssids)))}
        else:
            return result
    else:
        return {"error": "Unsupported OS"}

def connect_to_wifi(ssid, password):
    system = platform.system()
    ssid = ssid.strip()  # Ensure no leading/trailing whitespace
    if system == "Linux":
        cmd = f"echo {ROOT_PASSWORD} | sudo -S nmcli dev wifi connect '{ssid}' password '{password}'"
    else:
        return {"error": "Unsupported OS"}
    return run_command(cmd)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/current_ssid")
def current_ssid():
    result = get_current_ssid()
    return jsonify(result)

@app.route("/scan")
def scan():
    result = scan_networks()
    return jsonify(result)

@app.route("/connect", methods=["POST"])
def connect():
    data = request.get_json()
    ssid = data.get("ssid")
    password = data.get("password")
    if not ssid or not password:
        return jsonify({"error": "SSID and password are required"})
    result = connect_to_wifi(ssid, password)
    return jsonify(result)

@app.route('/upload_config', methods=['POST'])
def upload_config():
    print(request)
    print("request.files:", request.files)
    print("request.form:", request.form)
    if 'config-file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['config-file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    os.makedirs(UPLOAD_CONFIG_PATH, exist_ok=True)
    save_path = os.path.join(UPLOAD_CONFIG_PATH, file.filename)
    try:
        file.save(save_path)
        return jsonify({"success": True, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

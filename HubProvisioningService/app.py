"""
Hub+ Server Application
This Flask application provides a web interface for managing Wi-Fi connections,
uploading configuration files, and displaying the current SSID.
It is intended to be a connect 1 equivalent to the Hub+ device's functionality.
"""
import os
import time
import platform
import subprocess
import argparse
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

ROOT_PASSWORD = "PASSWORD_HERE"
UPLOAD_CONFIG_PATH = "./uploads"

def run_command(command):
    """
    Run a shell command and return the output or error.
    :param command: The shell command to run.
    :return: A dictionary with 'output' or 'error'."""
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Check if the command was successful
        # and return the output or error.
        if result.returncode != 0:
            return {"error": result.stderr.strip()}
        return {"output": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}

def get_current_ssid():
    """
    Get the current connected SSID.
    """
    system = platform.system()
    # Check the operating system and run the appropriate command.
    # For Linux, we use nmcli to get the current SSID.
    # For other systems, we return an error. Do not need to support Windows or macOS since
    # this is intended for a Linux-based Hub+ device.
    if system == "Linux":
        cmd = "nmcli -t -f active,ssid dev wifi | egrep '^yes' | cut -d\":\" -f2"
    else:
        return {"error": "Unsupported OS"}
    return run_command(cmd)

def scan_networks():
    """
    Scan for available Wi-Fi networks and return a list of SSIDs.
    """
    system = platform.system()
    if system == "Linux":
        # Force a rescan and wait for results
        run_command("echo {} | nmcli device wifi rescan".format(ROOT_PASSWORD))
        time.sleep(2)  # Wait for scan to complete
        # Get the list of SSIDs
        result = run_command("echo {} | sudo -S nmcli -t -f SSID dev wifi".format(ROOT_PASSWORD))
        # Process the output to remove empty lines and duplicates
        if "output" in result:
            ssids = [ssid.strip() for ssid in result["output"].split('\n') if ssid and ssid.strip() != "--"]
            return {"ssids": sorted(list(set(ssids)))}
        else:
            return result
    else:
        return {"error": "Unsupported OS"}

def connect_to_wifi(ssid, password):
    """
    Connect to a Wi-Fi network using the provided SSID and password.
    """
    system = platform.system()
    ssid = ssid.strip()  # Ensure no leading/trailing whitespace
    if system == "Linux":
        cmd = f"echo {ROOT_PASSWORD} | sudo -S nmcli dev wifi connect '{ssid}' password '{password}' ifname wlan0"
    else:
        return {"error": "Unsupported OS"}
    return run_command(cmd)

@app.route("/")
def index():
    """
    Render the main index page."""
    return render_template("index.html")

@app.route("/current_ssid")
def current_ssid():
    """
    Get the current connected SSID and return it as JSON.
    """
    result = get_current_ssid()
    return jsonify(result)

@app.route("/scan")
def scan():
    """
    Scan for available Wi-Fi networks and return the list of SSIDs as JSON.
    """
    result = scan_networks()
    return jsonify(result)

@app.route("/connect", methods=["POST"])
def connect():
    """
    Connect to a Wi-Fi network using the provided SSID and password.
    Expects a JSON payload with 'ssid' and 'password'.
    """
    data = request.get_json()
    ssid = data.get("ssid")
    password = data.get("password")
    # Check if SSID and password are provided
    # Return error if both are not provided.
    if not ssid or not password:
        return jsonify({"error": "SSID and password are required"})
    result = connect_to_wifi(ssid, password)
    return jsonify(result)

@app.route('/upload_config', methods=['POST'])
def upload_config():
    """
    Upload a configuration file.
    Expects a file upload with the key 'config-file'.
    """
    # Check if the request contains a file part
    if 'config-file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['config-file']
    # Check if the file is selected
    # and return an error if no file is selected.
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Ensure the upload directory exists
    os.makedirs(UPLOAD_CONFIG_PATH, exist_ok=True)
    # Save the file to the specified path, return success or error.
    save_path = os.path.join(UPLOAD_CONFIG_PATH, file.filename)
    try:
        file.save(save_path)
        return jsonify({"success": True, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hub+ Server Application')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind to (default: 5001)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    app.run(host=args.host, port=args.port, debug=args.debug or False)

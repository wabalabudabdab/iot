from flask import Flask, request, jsonify
import subprocess
import json
import os
import re

app = Flask(__name__)

@app.route("/pulse", methods=["POST"])
def receive_pulse():
    data = request.get_json()
    if not data or "pulse" not in data:
        return jsonify({"error": "Missing 'pulse' value"}), 400

    try:
        pulse = int(data["pulse"])
    except (ValueError, TypeError):
        return jsonify({"error": "'pulse' must be an integer"}), 400

    threshold = 80
    alert = 1 if pulse > threshold else 0

    input_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../circom/input.json"))
    with open(input_path, "w") as f:
        json.dump({
            "pulse": int(pulse),
            "threshold": int(threshold),
            "alert": int(alert)
        }, f, indent=0)

    result = subprocess.run(
        ["bash", "generate_proof.sh"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "../circom")),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        return jsonify({
            "error": "ZK proof generation failed",
            "details": str(result.stderr)
        }), 500
    
    print("---------------------------------------------------")
    print({
        "status": "proof generated",
        "pulse": pulse,
        "details": re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', result.stdout),
        "threshold": threshold,
        "alert": alert
    })
    print("---------------------------------------------------")
    return jsonify({
        "status": "proof generated",
        "pulse": pulse,
        "threshold": threshold,
        "alert": alert
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

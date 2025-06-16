from flask import Flask, request, jsonify
import subprocess, json, os, time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT_ADDRESS = Web3.to_checksum_address(os.getenv("ACCOUNT_ADDRESS"))
CONTRACT_ADDRESS = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))

ABI = [
    {
        "inputs": [
            {"internalType": "uint256[2]", "name": "a", "type": "uint256[2]"},
            {"internalType": "uint256[2][2]", "name": "b", "type": "uint256[2][2]"},
            {"internalType": "uint256[2]", "name": "c", "type": "uint256[2]"},
            {"internalType": "uint256[1]", "name": "input", "type": "uint256[1]"}
        ],
        "name": "submitProof",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

PA_ABI = [
  {
    "inputs": [],
    "name": "verifier",
    "outputs":[{"internalType":"address","name":"","type":"address"}],
    "stateMutability":"view","type":"function"
  },
  {
    "inputs":[
      {"internalType":"uint256[2]","name":"a","type":"uint256[2]"},
      {"internalType":"uint256[2][2]","name":"b","type":"uint256[2][2]"},
      {"internalType":"uint256[2]","name":"c","type":"uint256[2]"},
      {"internalType":"uint256[1]","name":"input","type":"uint256[1]"}
    ],
    "name":"submitProof","outputs":[],"stateMutability":"nonpayable","type":"function"
  }
]

V_ABI = [
  {
    "inputs":[
      {"internalType":"uint256[2]","name":"a","type":"uint256[2]"},
      {"internalType":"uint256[2][2]","name":"b","type":"uint256[2][2]"},
      {"internalType":"uint256[2]","name":"c","type":"uint256[2]"},
      {"internalType":"uint256[1]","name":"input","type":"uint256[1]"}
    ],
    "name":"verifyProof",
    "outputs":[{"internalType":"bool","name":"","type":"bool"}],
    "stateMutability":"view","type":"function"
  }
]


w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

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
    circom_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../circom"))

    with open(input_path, "w") as f:
        json.dump({
            "pulse": int(pulse),
            "threshold": int(threshold),
            "alert": int(alert)
        }, f, indent=0)

    print("enviroments:", CONTRACT_ADDRESS, ACCOUNT_ADDRESS, PRIVATE_KEY)

    print("Sleeping for 1 seconds...")
    time.sleep(1)  # пауза 1 секунд

    result = subprocess.run(
        ["bash", "generate_proof.sh"],
        cwd=circom_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print("proof gen failed")
        return jsonify({"error": "proof gen failed", "details": result.stderr}), 500

    with open(os.path.join(circom_dir, "proof.json")) as f:
        proof = json.load(f)
    with open(os.path.join(circom_dir, "public.json")) as f:
        public_signals = json.load(f)
    with open(os.path.join(circom_dir, "input.json")) as f:
        data = json.load(f)    
    print("---------------EXTRACT FROM FILES-----------------")
    print("proof:", proof)
    print("public_signals:", public_signals)
    print("data:", data)
    print("---------------------------------------------------")

    a = [int(proof["pi_a"][0]), int(proof["pi_a"][1])]
    b = [
        [int(proof["pi_b"][0][0]), int(proof["pi_b"][0][1])],
        [int(proof["pi_b"][1][0]), int(proof["pi_b"][1][1])]
    ]
    c = [int(proof["pi_c"][0]), int(proof["pi_c"][1])]
    inp = [int(public_signals[0])]

    print("a:", a)
    print("b:", b)
    print("c:", c)
    print("inp:", inp)

    # test contract
    pa = w3.eth.contract(address=CONTRACT_ADDRESS, abi=PA_ABI)
    verifier_addr = pa.functions.verifier().call()

    verifier = w3.eth.contract(address=verifier_addr, abi=V_ABI)
    ok = verifier.functions.verifyProof(a, b, c, inp).call()
    print("verifyProof:", ok)

    if ok == True:
        return jsonify({
        "status":      "proof ready",
        "alert":       alert
    }), 200
    else:
        return jsonify({
            "status": "proof failed",
            "alert": alert
        }), 500

#    Собираем и отправляем транзакцию
#     try:
#         nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS, "pending")
#         gas_price = w3.to_wei("10", "gwei")
#         print("a:", a)
#         print("b:", b)
#         print("c:", c)
#         print("inp:", inp)
#         print("nonce:", nonce)
#         print("gas_price:", gas_price)
#         tx = contract.functions.submitProof(a, b, c, inp).build_transaction({
#             "from": ACCOUNT_ADDRESS,
#             "nonce": nonce,
#             "gas": 300000,
#             "gasPrice": gas_price
#         })
#         signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
#         tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
#         try:
#             receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
#             print("RECEIPT:", receipt)
#             print("RECEIPT STATUS:", getattr(receipt, "status", "NO STATUS"))
#             if receipt.status == 1:
#                 print("tx_hash:", tx_hash.hex())
#                 print("receipt:", receipt)
#                 return jsonify({
#                     "status": "on-chain",
#                     # "tx_hash": tx_hash.hex(),
#                     "pulse": pulse,
#                     "threshold": threshold,
#                     "alert": alert
#                 }), 200
#             else:
#                 print("RETURN: tx failed!")
#                 return jsonify({
#                     "error": "tx failed!",
#                     "tx_hash": tx_hash.hex()
#                 }), 500
#         except Exception as e:
#             print("EXCEPTION IN RECEIPT BLOCK:", e)
#             import traceback
#             traceback.print_exc()
#             return jsonify({"error": "exception in receipt block", "details": str(e)}), 500
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return jsonify({"error": "contract call failed", "details": str(e)}), 500

def hexbytes_to_str(obj):
    if isinstance(obj, bytes):
        return obj.hex()
    if hasattr(obj, "hex"):
        return obj.hex()
    if isinstance(obj, dict):
        return {k: hexbytes_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [hexbytes_to_str(i) for i in obj]
    return obj

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


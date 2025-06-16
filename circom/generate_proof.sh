#!/bin/bash
set -e

cd "$(dirname "$0")"

# # 1. Компиляция схемы
# circom pulse_check.circom --r1cs --wasm --sym

# # 2. Trusted setup
# if [ ! -f pot12_final.ptau ]; then
#   snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
#   snarkjs powersoftau contribute pot12_0000.ptau pot12_final.ptau --name="First contributor" -v
# fi

# # 3. Генерация proving/verifying ключей
# snarkjs groth16 setup pulse_check.r1cs pot12_final.ptau pulse_check_0000.zkey
# cp pulse_check_0000.zkey pulse_check.zkey
# snarkjs zkey export verificationkey pulse_check.zkey verification_key.json

node pulse_check_js/generate_witness.js pulse_check_js/pulse_check.wasm input.json witness.wtns

# 4. Генерация доказательства
snarkjs groth16 prove pulse_check.zkey witness.wtns proof.json public.json


# 5. Проверка доказательства
snarkjs groth16 verify verification_key.json public.json proof.json




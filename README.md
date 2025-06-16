# zk-snark-iot (Sepolia)

## Описание

Проект для генерации и проверки zkSNARK-доказательств (Groth16) с использованием circom, snarkjs, Python (Flask) и смарт-контрактов на Ethereum Sepolia.

---

## Деплой смарт-контрактов

1. Перейдите в папку с контрактами:
   ```bash
   cd hardhat
   ```
2. Скомпилируйте контракты:
   ```bash
   npx hardhat compile
   ```
3. Задеплойте Verifier:
   ```bash
   npx hardhat run scripts/deploy-verifier.js --network sepolia
   ```
   - Скопируйте адрес Verifier в .env как `VERIFIER_ADDRESS`.
4. Задеплойте PulseAlert:
   ```bash
   npx hardhat run scripts/deploy.js --network sepolia
   ```
   - Скопируйте адрес PulseAlert в .env как `CONTRACT_ADDRESS`.

---

## Генерация proof (на хосте, без Docker)

1. Перейдите в папку circom:
   ```bash
   cd ../circom
   ```
2. Скомпилируйте схему (если менялась):
   ```bash
   circom pulse_check.circom --r1cs --wasm --sym
   ```
3. Скачайте ptau (если ещё не скачан):
   ```bash
   curl -L -o pot12_final.ptau [источник пока не нашла где]
   ```
4. Сгенерируйте zkey и Verifier.sol (только один раз для деплоя!):
   ```bash
   snarkjs groth16 setup pulse_check.r1cs pot12_final.ptau pulse_check.zkey
   snarkjs zkey export verificationkey pulse_check.zkey verification_key.json
   snarkjs zkey export solidityverifier pulse_check.zkey Verifier.sol
   ```
5. Для каждого нового input.json:
   ```bash
   node pulse_check_js/generate_witness.js pulse_check_js/pulse_check.wasm input.json witness.wtns
   snarkjs groth16 prove pulse_check.zkey witness.wtns proof.json public.json
   snarkjs groth16 verify verification_key.json public.json proof.json
   ```

---

## Запуск backend (Flask)

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запустите сервер:
   ```bash
   python api/app.py
   ```

---

## Примечания
- Все переменные окружения должны быть прописаны в .env.
- Для корректной работы используйте одну и ту же версию zkey для генерации proof и деплоя Verifier.sol.
- Для тестов используйте Sepolia ETH (можно получить в кранах).

---

## Быстрый старт

```bash
cd hardhat
npx hardhat compile
npx hardhat run scripts/deploy-verifier.js --network sepolia
npx hardhat run scripts/deploy.js --network sepolia
cd ../circom
circom pulse_check.circom --r1cs --wasm --sym
curl -L -o pot12_final.ptau https://storage.googleapis.com/zkevm/ptau/powersOfTau28_hez_final_12.ptau
snarkjs groth16 setup pulse_check.r1cs pot12_final.ptau pulse_check.zkey
snarkjs zkey export verificationkey pulse_check.zkey verification_key.json
snarkjs zkey export solidityverifier pulse_check.zkey Verifier.sol
node pulse_check_js/generate_witness.js pulse_check_js/pulse_check.wasm input.json witness.wtns
snarkjs groth16 prove pulse_check.zkey witness.wtns proof.json public.json
snarkjs groth16 verify verification_key.json public.json proof.json
cd ../api
pip install -r requirements.txt
python app.py
```

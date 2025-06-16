const hre = require("hardhat");
require("dotenv").config();

async function main() {
  console.log("Начинаем деплой PulseAlert...");

  // Проверяем наличие .env
  if (!process.env.PRIVATE_KEY) {
    throw new Error("PRIVATE_KEY не указан в .env файле");
  }
  if (!process.env.SEPOLIA_RPC_URL) {
    throw new Error("SEPOLIA_RPC_URL не указан в .env файле");
  }

  // Проверяем адрес верификатора
  const verifierAddress = process.env.VERIFIER_ADDRESS;
  if (!verifierAddress) {
    throw new Error("VERIFIER_ADDRESS не указан в .env файле");
  }
  console.log("Адрес верификатора:", verifierAddress);

  // Получаем аккаунт
  const [deployer] = await hre.ethers.getSigners();
  console.log("Деплоим с адреса:", deployer.address);

  // Деплой PulseAlert
  console.log("Деплоим PulseAlert...");
  const PulseAlert = await hre.ethers.getContractFactory("PulseAlert");
  const pulseAlert = await PulseAlert.deploy(verifierAddress);

  console.log("Ожидаем подтверждения транзакции...");
  await pulseAlert.waitForDeployment();

  const pulseAlertAddress = await pulseAlert.getAddress();
  console.log("PulseAlert успешно развернут по адресу:", pulseAlertAddress);

  // Проверяем, что контракт работает
  console.log("Проверяем контракт...");
  const verifier = await pulseAlert.verifier();
  console.log("Адрес верификатора в контракте:", verifier);
  
  if (verifier.toLowerCase() !== verifierAddress.toLowerCase()) {
    throw new Error("Адрес верификатора в контракте не совпадает с указанным");
  }

  console.log("Деплой успешно завершен!");
}

main().catch((error) => {
  console.error("Ошибка при деплое:", error);
  process.exitCode = 1;
}); 
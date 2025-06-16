FROM node:18

# Установим snarkjs глобально
RUN npm install -g snarkjs

# Установим необходимые утилиты
RUN apt-get update && apt-get install -y build-essential

WORKDIR /app

# Команда по умолчанию — открыть bash
CMD ["/bin/bash"]

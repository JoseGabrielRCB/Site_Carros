# Usa apenas o Node para rodar o servidor de desenvolvimento
FROM node:20-alpine

WORKDIR /app

# Copia os arquivos de dependências e instala
COPY package*.json ./
RUN npm install

# Copia o restante do código
COPY . .

# Expõe a porta que configuramos no Vite
EXPOSE 8080

# Liga o motor do Vite em modo de desenvolvimento!
CMD ["npm", "run", "dev"]
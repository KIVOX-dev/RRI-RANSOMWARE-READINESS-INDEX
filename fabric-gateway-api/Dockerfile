FROM node:20-slim AS builder
WORKDIR /usr/src/app
COPY package.json ./
RUN npm install
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

FROM node:20-slim
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app/dist ./dist
COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY package.json ./

EXPOSE 3001
CMD ["node", "dist/server.js"]

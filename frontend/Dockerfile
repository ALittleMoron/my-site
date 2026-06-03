FROM node:24.16.0-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:24.16.0-alpine AS runtime
WORKDIR /app

ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=builder /app/dist/my-site-frontend ./dist/my-site-frontend

EXPOSE 4000
CMD ["node", "dist/my-site-frontend/server/server.mjs"]

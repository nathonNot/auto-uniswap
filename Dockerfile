# 使用官方Node.js镜像作为基础镜像，这里以Node.js 14版本为例
FROM node:20-alpine

WORKDIR /app

COPY . .

RUN sh init.sh

CMD ["node"]
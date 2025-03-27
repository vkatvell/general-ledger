# frontend.Dockerfile
FROM node:22.13.0-slim


WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci
RUN npm install --platform=linux --arch=x64 @tailwindcss/postcss
RUN npm install lightningcss
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
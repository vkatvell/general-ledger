# frontend.Dockerfile
FROM node:18

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy frontend source code
COPY . .

# Expose default Next.js port
EXPOSE 3000

# Run Next.js development server
CMD ["npm", "run", "dev"]

FROM node:18-alpine

WORKDIR /app

# Copy only package.json
COPY package.json ./

# Install dependencies
RUN npm install --silent

# Copy frontend source code
COPY . .

# Build-time environment variable
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the app
RUN npm run build

# Optional: debug built files
RUN ls -la dist/

# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package.json ./
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Copy built app
COPY --from=build /app/dist ./dist

# Install serve as a local dependency
RUN npm install -g serve

EXPOSE 3000

# Start the server
CMD ["serve", "-s", "dist", "-l", "3000"]
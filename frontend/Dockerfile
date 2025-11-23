# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files first
COPY package.json ./
RUN npm install

# Copy source code
COPY . .

ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN VITE_API_URL=$VITE_API_URL


# Build the app
RUN npm run build

# Debug: List built files
RUN ls -la dist/

# Production stage
FROM nginx:alpine

# Copy built app to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
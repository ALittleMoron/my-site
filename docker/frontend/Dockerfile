# Build stage
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package.json ./

# Install dependencies
RUN yarn install

# Copy project files
COPY frontend/ .

# Build the application
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy nginx configuration
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 
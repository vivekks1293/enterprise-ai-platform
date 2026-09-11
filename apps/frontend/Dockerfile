# ==========================================
# Stage 1: Build Angular Application
# ==========================================
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first for Docker caching
COPY package*.json ./
RUN npm ci

# Copy source and build production bundle
COPY . .
RUN npm run build:prod

# ==========================================
# Stage 2: Serve with Nginx
# ==========================================
FROM nginx:alpine

# Copy built static files from Angular 18 output
COPY --from=builder /app/dist/enterprise-ai-platform/browser /usr/share/nginx/html

# Copy custom Nginx configuration with SSE and connection limiting
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]


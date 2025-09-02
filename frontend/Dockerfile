# syntax=docker/dockerfile:1

########################
# 1) Build Stage
########################
FROM node:20-alpine AS builder
WORKDIR /app

# Faster, repeatable installs
COPY package*.json ./
RUN npm ci --no-audit --no-fund

# Copy source and build
COPY frontend/ .
# Set build-time API base if you use REACT_APP_* vars
# (you can also pass them via build args in compose)
ARG REACT_APP_API_BASE=""
ENV REACT_APP_API_BASE=${REACT_APP_API_BASE}

# Ensure production build
ENV NODE_ENV=production
RUN npm run build

########################
# 2) Serve via Nginx
########################
FROM nginx:1.27-alpine
RUN rm -f /etc/nginx/conf.d/default.conf
COPY frontend/nginx.conf /etc/nginx/conf.d/react.conf
COPY --from=builder /app/build /usr/share/nginx/html


# Expose HTTP
EXPOSE 80


CMD ["nginx", "-g", "daemon off;"]

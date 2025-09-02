# frontend/Dockerfile

# ===== Build stage =====
FROM node:20-bookworm-slim AS builder
WORKDIR /app

# Tools for native deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 make g++ && rm -rf /var/lib/apt/lists/*

COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ .
ENV NODE_ENV=production

# reduce memory & speed up build
ENV NODE_OPTIONS=--max_old_space_size=1024
ENV GENERATE_SOURCEMAP=false


RUN npm run build

# ===== Serve stage =====
FROM nginx:1.27-alpine
RUN rm -f /etc/nginx/conf.d/default.conf
COPY frontend/nginx.conf /etc/nginx/conf.d/react.conf
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost/healthz || exit 1
CMD ["nginx","-g","daemon off;"]

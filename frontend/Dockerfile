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
COPY . .
# Set build-time API base if you use REACT_APP_* vars
# (you can also pass them via build args in compose)
ARG REACT_APP_API_BASE=""
ENV REACT_APP_API_BASE=${REACT_APP_API_BASE}

# Ensure production build
ENV NODE_ENV=production
RUN npm run build

########################
# 2) Serve Stage
########################
FROM nginx:1.27-alpine

# Remove default conf and add ours
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/react.conf

# Copy the built static files
COPY --from=builder /app/build /usr/share/nginx/html

# Optional: drop a simple robots.txt (remove if you have your own)
# RUN printf "User-agent: *\nDisallow:\n" > /usr/share/nginx/html/robots.txt

# Expose HTTP
EXPOSE 80

# Healthcheck (container-level)
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]

# ---- Stage 1: Build ----
FROM node:22-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build
RUN ls -R /app/dist

# ---- Stage 2: Serve with nginx ----
FROM nginx:1.27-alpine

# Install openssl for self-signed certificate generation
RUN apk add --no-cache openssl

# Generate self-signed SSL certificate
RUN mkdir -p /etc/nginx/ssl &&     openssl req -x509 -nodes -days 365 -newkey rsa:2048     -keyout /etc/nginx/ssl/server.key     -out /etc/nginx/ssl/server.crt     -subj "/C=CN/ST=Shanghai/L=Shanghai/O=HWT Blog/CN=localhost"     -addext "subjectAltName=DNS:localhost,DNS:hwt-blog.local"

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]

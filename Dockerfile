# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/dashboard
COPY dashboard/package*.json ./
RUN npm ci --legacy-peer-deps
COPY dashboard/ .
# Inject production API URL if needed during build
ENV VITE_API_URL=/api/v1/dashboard
RUN npm run build

# Stage 2: Backend and Production Image
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Copiar frontend construido desde el Stage 1
COPY --from=frontend-builder /app/dashboard/dist ./dashboard/dist

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 flyuser && chown -R flyuser:flyuser /app
USER flyuser

# Variables de entorno por defecto
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Comando de inicio
CMD ["sh", "-c", "python src/main.py"]

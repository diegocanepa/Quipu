# Etapa 1: Build con Rust y Python
FROM python:3.12-alpine AS builder

# Instalar dependencias del sistema
RUN apk add --no-cache gcc musl-dev libffi-dev rust cargo

# Crear ambiente virtual
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 2: Imagen final sin Rust
FROM python:3.12-alpine

# Variables de entorno
ENV PATH="/opt/venv/bin:$PATH"

# Copiar el virtualenv con paquetes ya compilados
COPY --from=builder /opt/venv /opt/venv

# Crear usuario no root por seguridad
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Definir directorio de trabajo
WORKDIR /app
COPY . .

# Exponer puerto y comando de ejecución
EXPOSE 8080
CMD ["flask", "run"]

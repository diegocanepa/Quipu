# Quipu Multi-Service Financial Bot

[![Version](https://img.shields.io/badge/version-0.0.0-blue.svg)](https://github.com/original-repo/Quipu/releases/tag/v0.0.0)
[![Status](https://img.shields.io/badge/status-stable-green.svg)]()
[![Deploy](https://img.shields.io/badge/deploy-automated-green.svg)]()

## v0.0.0

Bot financiero multi-servicio que procesa transacciones a través de Telegram y WhatsApp, con integración a Supabase y Google Sheets.

## 🚀 Características

### Plataformas Soportadas
- **Telegram Bot** - Procesamiento de mensajes de texto y audio
- **WhatsApp Bot** - Integración completa con Meta Business API
- **Web API** - Endpoints RESTful para integraciones

### Procesamiento Inteligente
- **Audio a Texto** - Transcripción automática de mensajes de voz
- **Análisis LLM** - Procesamiento inteligente de transacciones financieras
- **Categorización** - Clasificación automática de gastos e ingresos

### Almacenamiento
- **Supabase** - Base de datos principal
- **Google Sheets** - Exportación automática de datos

## 🛠️ Instalación y Deploy

### Requisitos
- Python 3.11+
- Servidor Ubuntu/Debian
- Mínimo 1GB RAM (optimizado para AWS t2.micro)

### Deploy Automático
```bash
# El deploy es completamente automático via GitHub Actions
git push origin main
```

### Verificación Post-Deploy
```bash
# Estado del servicio
sudo systemctl status quipu.service

# Logs en tiempo real
sudo tail -f /var/log/quipu/quipu.log

# Health check
curl http://localhost:8080/healthcheck
```

## 📋 Configuración

### Variables de Entorno Requeridas
```bash
# API Keys
TELEGRAM_BOT_TOKEN=your_telegram_token
AKASH_API_KEY=your_llm_api_keys
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Google Services
GOOGLE_CREDENTIALS=your_google_credentials
GOOGLE_SHEET_TEMPLATE_URL=your_sheet_template

# WhatsApp (si se usa)
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_ID=your_phone_id
```

## 🔧 Scripts de Utilidad

```bash
# Monitoreo de logs
sudo journalctl -u quipu.service -f
```

## 📊 Monitoreo

### Health Checks
- **Endpoint**: `GET /healthcheck`
- **Telegram**: `GET /telegram/healthcheck`  
- **WhatsApp**: `GET /whatsapp/healthcheck`

### Logs
- **Archivo**: `/var/log/quipu/quipu.log`
- **SystemD**: `journalctl -u quipu.service`
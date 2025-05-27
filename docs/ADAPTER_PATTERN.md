# Patrón Adapter para Plataformas de Mensajería

Este documento explica cómo usar el patrón Adapter implementado para desacoplar la lógica de negocio de las plataformas de mensajería específicas.

## Arquitectura

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Lógica de         │    │   Servicio de        │    │   Adaptador         │
│   Negocio           │───▶│   Mensajería         │───▶│   Específico        │
│   (Core Services)   │    │   (Platform Agnostic)│    │   (Telegram/Discord)│
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## Componentes Principales

### 1. Interfaz de Plataforma (`MessagingPlatformInterface`)
Define los métodos que debe implementar cualquier adaptador de plataforma:
- `send_message()`: Envía mensajes de texto
- `send_message_with_keyboard()`: Envía mensajes con botones
- `edit_message()`: Edita mensajes existentes
- `answer_callback_query()`: Responde a interacciones
- `get_voice_file_data()`: Obtiene datos de archivos de voz
- `convert_to_platform_update()`: Convierte actualizaciones específicas a formato agnóstico

### 2. Modelos Agnósticos
- `PlatformUser`: Representa un usuario independiente de la plataforma
- `PlatformMessage`: Representa un mensaje independiente de la plataforma
- `PlatformUpdate`: Representa una actualización independiente de la plataforma

### 3. Servicio de Mensajería (`MessageService`)
Capa intermedia que usa el adaptador y proporciona métodos convenientes:
- `reply_to_current_message()`: Responde al mensaje actual
- `reply_with_keyboard()`: Responde con teclado al mensaje actual
- `get_current_user()`: Obtiene el usuario actual del contexto

### 4. Adaptadores Específicos
- `TelegramAdapter`: Implementación para Telegram
- `DiscordAdapter`: Ejemplo de implementación para Discord

## Cómo Agregar una Nueva Plataforma

### Paso 1: Crear el Adaptador
```python
from core.interfaces.messaging_platform import MessagingPlatformInterface

class WhatsAppAdapter(MessagingPlatformInterface):
    def __init__(self, whatsapp_client):
        self.client = whatsapp_client
    
    async def send_message(self, user_id: str, text: str, **kwargs):
        # Implementar envío de mensaje para WhatsApp
        return await self.client.send_text_message(user_id, text)
    
    # Implementar otros métodos...
```

### Paso 2: Configurar el Servicio
```python
from core.platforms.whatsapp_adapter import WhatsAppAdapter
from core.services.message_service import MessageService

# Crear adaptador
whatsapp_adapter = WhatsAppAdapter(whatsapp_client)

# Crear servicio de mensajería
message_service = MessageService(whatsapp_adapter)
```

### Paso 3: Usar en Handlers
```python
async def handle_whatsapp_message(whatsapp_update):
    # Configurar contexto
    platform_update = whatsapp_adapter.convert_to_platform_update(whatsapp_update)
    message_service.set_current_update_context(platform_update)
    
    # Usar métodos agnósticos
    await message_service.reply_to_current_message("¡Hola desde WhatsApp!")
```

## Beneficios del Patrón Adapter

1. **Desacoplamiento**: La lógica de negocio no depende de APIs específicas
2. **Extensibilidad**: Fácil agregar nuevas plataformas
3. **Mantenibilidad**: Cambios en una plataforma no afectan otras
4. **Testabilidad**: Se puede crear un adaptador mock para pruebas
5. **Reutilización**: Los servicios de negocio funcionan con cualquier plataforma

## Ejemplo de Uso Completo

```python
# En un handler
async def handle_financial_command(update, context):
    # Configurar adaptador
    telegram_adapter.set_bot_context(context.bot, context)
    platform_update = telegram_adapter.convert_to_platform_update(update)
    message_service.set_current_update_context(platform_update, context)
    
    # Usar servicio de onboarding (funciona con cualquier plataforma)
    user = message_service.get_current_user()
    await onboarding_service.handle_start_onboarding(user)
```

## Migración Gradual

Para migrar gradualmente:

1. **Fase 1**: Implementar adaptadores para funcionalidades críticas
2. **Fase 2**: Migrar handlers uno por uno
3. **Fase 3**: Agregar nuevas plataformas usando el patrón
4. **Fase 4**: Deprecar código específico de plataforma

## Testing

```python
# Crear adaptador mock para pruebas
class MockAdapter(MessagingPlatformInterface):
    def __init__(self):
        self.sent_messages = []
    
    async def send_message(self, user_id: str, text: str, **kwargs):
        self.sent_messages.append((user_id, text))
        return {"message_id": "test_123"}

# Usar en pruebas
mock_adapter = MockAdapter()
message_service = MessageService(mock_adapter)
# ... ejecutar lógica ...
assert len(mock_adapter.sent_messages) == 1
```
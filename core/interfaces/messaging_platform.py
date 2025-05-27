from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PlatformUser:
    """Representa un usuario agnóstico de plataforma"""

    platform_user_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    platform_type: str = None


@dataclass
class PlatformMessage:
    """Representa un mensaje agnóstico de plataforma"""

    text: Optional[str] = None
    user: Optional[PlatformUser] = None
    message_id: Optional[str] = None
    is_voice: bool = False
    voice_file_data: Optional[bytes] = None


@dataclass
class PlatformUpdate:
    """Representa una actualización agnóstica de plataforma"""

    message: Optional[PlatformMessage] = None
    callback_query: Optional[Dict[str, Any]] = None
    user: Optional[PlatformUser] = None


class MessagingPlatformInterface(ABC):
    """Interfaz para adaptadores de plataformas de mensajería"""

    @abstractmethod
    async def send_message(self, user_id: str, text: str, **kwargs) -> Any:
        """Envía un mensaje de texto al usuario"""
        pass

    @abstractmethod
    async def send_message_with_keyboard(
        self, user_id: str, text: str, buttons: List[tuple], **kwargs
    ) -> Any:
        """Envía un mensaje con teclado inline"""
        pass

    @abstractmethod
    async def edit_message(self, message_id: str, text: str, **kwargs) -> Any:
        """Edita un mensaje existente"""
        pass

    @abstractmethod
    async def answer_callback_query(
        self, callback_query_id: str, text: Optional[str] = None
    ) -> Any:
        """Responde a una consulta de callback"""
        pass

    @abstractmethod
    async def get_voice_file_data(self, voice_message_data: Any) -> Optional[bytes]:
        """Obtiene los datos de un archivo de voz"""
        pass

    @abstractmethod
    def convert_to_platform_update(
        self, platform_specific_update: Any
    ) -> PlatformUpdate:
        """Convierte una actualización específica de la plataforma a formato agnóstico"""
        pass

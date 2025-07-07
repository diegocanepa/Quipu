"""
Configuración centralizada de logging con soporte para CloudWatch y estructura agrupada.
Versión actualizada con 4 grupos principales para operaciones simplificadas.
"""
import logging
import os
import boto3
import watchtower
import time
import socket
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

class CloudWatchGroupedConfig:
    """Configuración singleton para CloudWatch logging con estructura agrupada"""
    _configured = False
    _cloudwatch_enabled = False
    _active_handlers = {}  # Cache de handlers por grupo
    
    # Definición de la estructura agrupada
    GROUP_MAPPING = {
        # PLATFORMS - Todo lo relacionado con Telegram y WhatsApp
        'api.telegram': 'platforms',
        'api.whatsapp': 'platforms', 
        'integrations.platforms.telegram_adapter': 'platforms',
        'integrations.platforms.whatsapp_adapter': 'platforms',
        'telegram_bot': 'platforms',
        'whatsapp_bot': 'platforms',
        
        # BUSINESS-LOGIC - Core, procesadores, managers, services
        'core.message_processor': 'business-logic',
        'core.llm_processor': 'business-logic',
        'core.audio_processor': 'business-logic',
        'core.data_server': 'business-logic',
        'core.user_data_manager': 'business-logic',
        'core.onboarding_manager': 'business-logic',
        'core.services': 'business-logic',
        'core.': 'business-logic',  # Fallback para todo core.*
        
        # INTEGRATIONS - Servicios externos (LLM, DB, Cache, etc.)
        'integrations.providers': 'integrations',
        'integrations.supabase': 'integrations',
        'integrations.spreadsheet': 'integrations', 
        'integrations.cache': 'integrations',
        'integrations.transcriptor': 'integrations',
        'integrations.': 'integrations',  # Fallback para todo integrations.*
        
        # INFRASTRUCTURE - App principal, config, logging
        'app': 'infrastructure',
        'config': 'infrastructure',
        'logging_config': 'infrastructure',
        '__main__': 'infrastructure',
    }
    
    @classmethod
    def setup_global_cloudwatch(cls):
        """Configurar CloudWatch una sola vez para toda la aplicación"""
        if cls._configured:
            return cls._cloudwatch_enabled
            
        try:
            # Cargar variables de entorno
            cls._load_env_vars()
            
            use_cloudwatch = os.getenv('USE_CLOUDWATCH', 'false').lower() == 'true'
            if not use_cloudwatch:
                print("☁️ CloudWatch logging deshabilitado por configuración")
                cls._configured = True
                cls._cloudwatch_enabled = False
                return False
                
            # Verificar credenciales
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            
            if not aws_access_key or not aws_secret_key:
                print("⚠️ CloudWatch: Credenciales AWS no configuradas")
                cls._configured = True
                cls._cloudwatch_enabled = False
                return False
            
            # Configuración básica
            environment = cls._normalize_environment()
            region_name = os.getenv('AWS_REGION', 'us-east-2')
            
            print(f"🔧 Configurando CloudWatch con estructura agrupada:")
            print(f"   - Región: {region_name}")
            print(f"   - Entorno: {environment}")
            print(f"   - Grupos: 4 (platforms, business-logic, integrations, infrastructure)")
            
            # Crear sesión de boto3
            session = boto3.Session(
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region_name
            )
            
            # Verificar conectividad
            if not cls._test_aws_connectivity(session):
                cls._configured = True
                cls._cloudwatch_enabled = False
                return False
            
            # Configurar grupos de logs
            cls._setup_log_groups(session, environment)
            
            cls._cloudwatch_enabled = True
            cls._configured = True
            print("✅ CloudWatch logging con estructura agrupada configurado exitosamente")
            return True
            
        except Exception as e:
            print(f"⚠️ Error inesperado configurando CloudWatch: {e}")
            cls._configured = True
            cls._cloudwatch_enabled = False
            return False
    
    @classmethod
    def _setup_log_groups(cls, session, environment):
        """Configurar los 4 grupos principales de logs"""
        groups = ['platforms', 'business-logic', 'integrations', 'infrastructure']
        
        for group in groups:
            log_group_name = f"/quipu/{environment}/{group}"
            
            # Asegurar que el grupo existe
            if cls._ensure_log_group_exists(session, log_group_name):
                print(f"📁 Grupo configurado: {log_group_name}")
            else:
                print(f"❌ Error configurando grupo: {log_group_name}")
    
    @classmethod 
    def get_log_group_for_module(cls, module_name: str) -> str:
        """
        Determina el grupo de logs apropiado para un módulo específico
        
        Args:
            module_name: Nombre del módulo (ej: 'core.message_processor')
            
        Returns:
            Nombre del grupo ('platforms', 'business-logic', 'integrations', 'infrastructure')
        """
        # Buscar coincidencia más específica primero
        for prefix, group in sorted(cls.GROUP_MAPPING.items(), key=len, reverse=True):
            if module_name.startswith(prefix):
                return group
        
        # Fallback a business-logic para módulos desconocidos
        return 'business-logic'
    
    @classmethod
    def get_cloudwatch_handler(cls, module_name: str):
        """
        Obtiene o crea un handler de CloudWatch para el módulo específico
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Handler de CloudWatch configurado para el grupo apropiado
        """
        if not cls._cloudwatch_enabled:
            return None
            
        # Determinar grupo
        group = cls.get_log_group_for_module(module_name)
        
        # Verificar si ya tenemos un handler para este grupo
        if group in cls._active_handlers:
            return cls._active_handlers[group]
        
        try:
            # Configuración
            environment = cls._normalize_environment()
            log_group_name = f"/quipu/{environment}/{group}"
            region_name = os.getenv('AWS_REGION', 'us-east-2')
            
            # Crear sesión
            session = boto3.Session(
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=region_name
            )
            
            # Crear nombre único para el stream
            hostname = socket.gethostname()
            stream_name = f"quipu-{group}-{hostname}-{int(time.time())}"
            
            # Crear cliente de logs
            logs_client = session.client('logs')
            
            # Crear handler
            handler = watchtower.CloudWatchLogHandler(
                log_group=log_group_name,
                stream_name=stream_name,
                boto3_client=logs_client,
                create_log_group=True,
                create_log_stream=True,
                use_queues=False,
                send_interval=5,
                max_batch_size=50
            )
            
            # Configurar formato
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            handler.setLevel(logging.INFO)
            
            # Guardar en cache
            cls._active_handlers[group] = handler
            
            print(f"📝 Handler CloudWatch creado para grupo '{group}': {stream_name}")
            return handler
            
        except Exception as e:
            print(f"❌ Error creando handler CloudWatch para grupo '{group}': {e}")
            return None
    
    @classmethod
    def _normalize_environment(cls):
        """Normalizar el nombre del entorno"""
        environment = os.getenv('ENVIRONMENT', 'development').lower().strip()
        
        env_mapping = {
            'prod': 'production',
            'dev': 'development',
            'test': 'testing',
            'stage': 'staging',
            'staging': 'staging'
        }
        
        return env_mapping.get(environment, environment)
    
    @classmethod
    def _test_aws_connectivity(cls, session):
        """Probar conectividad con AWS CloudWatch"""
        try:
            logs_client = session.client('logs')
            logs_client.describe_log_groups(limit=1)
            print("✅ Conectividad AWS verificada")
            return True
        except NoCredentialsError:
            print("❌ Credenciales AWS inválidas")
            return False
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            print(f"❌ Error de AWS ({error_code}): {e}")
            return False
        except Exception as e:
            print(f"❌ Error de conectividad AWS: {e}")
            return False
    
    @classmethod
    def _ensure_log_group_exists(cls, session, log_group_name):
        """Asegurar que el grupo de logs existe"""
        try:
            logs_client = session.client('logs')
            
            # Verificar si el grupo existe
            response = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
            exists = any(group['logGroupName'] == log_group_name 
                        for group in response.get('logGroups', []))
            
            if exists:
                return True
            
            # Crear el grupo de logs
            print(f"📁 Creando grupo de logs: {log_group_name}")
            logs_client.create_log_group(logGroupName=log_group_name)
            time.sleep(2)  # Esperar propagación
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'ResourceAlreadyExistsException':
                return True
            else:
                print(f"❌ Error creando grupo de logs ({error_code}): {e}")
                return False
        except Exception as e:
            print(f"❌ Error inesperado creando grupo de logs: {e}")
            return False
    
    @classmethod
    def _load_env_vars(cls):
        """Cargar variables de entorno desde archivos .env"""
        project_root = Path(__file__).parent
        env_file = None
        
        environment = os.getenv('ENVIRONMENT', 'development').lower()
        if environment in ['prod', 'production']:
            env_file = project_root / '.env.production'
        
        if not env_file or not env_file.exists():
            env_file = project_root / '.env'
        
        if env_file and env_file.exists():
            print(f"📋 Cargando variables desde: {env_file}")
            with open(env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if key not in os.environ:
                                os.environ[key] = value
                        except ValueError:
                            print(f"⚠️ Línea {line_num} ignorada en {env_file}: formato inválido")

def get_logger(name: str) -> logging.Logger:
    """
    Obtener un logger configurado con CloudWatch agrupado.
    
    Args:
        name: Nombre del logger (generalmente __name__)
    
    Returns:
        Logger configurado con el grupo CloudWatch apropiado
    """
    # Configurar CloudWatch si no se ha hecho
    CloudWatchGroupedConfig.setup_global_cloudwatch()
    
    # Obtener logger
    logger = logging.getLogger(name)
    
    # Verificar si ya tiene handler de CloudWatch para este grupo
    group = CloudWatchGroupedConfig.get_log_group_for_module(name)
    has_cw_handler = any(
        isinstance(h, watchtower.CloudWatchLogHandler) and 
        hasattr(h, 'log_group') and group in str(h.log_group)
        for h in logger.handlers
    )
    
    if not has_cw_handler and CloudWatchGroupedConfig._cloudwatch_enabled:
        # Agregar handler específico para este grupo
        cw_handler = CloudWatchGroupedConfig.get_cloudwatch_handler(name)
        if cw_handler:
            logger.addHandler(cw_handler)
            
            # Log de confirmación
            logger.info(f"✅ Logger configurado para grupo '{group}' - Módulo: {name}")
    
    # Asegurar nivel apropiado
    if logger.level > logging.INFO:
        logger.setLevel(logging.INFO)
    
    return logger

def show_log_groups_mapping():
    """Muestra el mapeo de módulos a grupos de logs"""
    print("\n=== MAPEO DE GRUPOS DE LOGS ===")
    
    environment = CloudWatchGroupedConfig._normalize_environment()
    
    groups = {
        'platforms': [],
        'business-logic': [],
        'integrations': [],
        'infrastructure': []
    }
    
    # Agrupar módulos por grupo
    for module, group in CloudWatchGroupedConfig.GROUP_MAPPING.items():
        groups[group].append(module)
    
    # Mostrar cada grupo
    for group_name, modules in groups.items():
        log_group_path = f"/quipu/{environment}/{group_name}"
        print(f"\n📁 {log_group_path}")
        for module in sorted(modules):
            print(f"   └── {module}")
    
    print(f"\n🎯 Total: 4 grupos de logs configurados")

def test_grouped_logging():
    """Función de test para verificar la estructura agrupada"""
    print("\n=== PRUEBA DE LOGGING AGRUPADO ===")
    
    # Mostrar mapeo
    show_log_groups_mapping()
    
    # Test de cada grupo
    test_modules = [
        'api.telegram.bot',           # -> platforms
        'core.message_processor',     # -> business-logic  
        'integrations.supabase.client', # -> integrations
        'app.main'                    # -> infrastructure
    ]
    
    print(f"\n🧪 Probando {len(test_modules)} módulos...")
    
    for module_name in test_modules:
        logger = get_logger(module_name)
        group = CloudWatchGroupedConfig.get_log_group_for_module(module_name)
        
        print(f"\n📝 Módulo: {module_name}")
        print(f"   └── Grupo: {group}")
        
        # Enviar logs de prueba
        logger.info(f"🧪 TEST INFO: {module_name} funcionando correctamente")
        logger.warning(f"🧪 TEST WARNING: Mensaje de advertencia desde {module_name}")
        logger.error(f"🧪 TEST ERROR: Mensaje de error desde {module_name}")
    
    print("\n=== PRUEBA COMPLETADA ===")
    print("Verifica los logs en AWS CloudWatch Console:")
    
    environment = CloudWatchGroupedConfig._normalize_environment() 
    region = os.getenv('AWS_REGION', 'us-east-2')
    
    groups = ['platforms', 'business-logic', 'integrations', 'infrastructure']
    for group in groups:
        log_group = f"/quipu/{environment}/{group}"
        import urllib.parse
        encoded_group = urllib.parse.quote(log_group, safe='')
        url = f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{encoded_group}"
        print(f"🔗 {group}: {url}")

def force_cloudwatch_flush():
    """Forzar el envío inmediato de logs a CloudWatch"""
    try:
        for handler in CloudWatchGroupedConfig._active_handlers.values():
            if handler:
                handler.flush()
        print("🚀 Logs enviados a CloudWatch")
    except Exception as e:
        print(f"⚠️ Error enviando logs: {e}")

if __name__ == "__main__":
    # Script de test directo
    test_grouped_logging()

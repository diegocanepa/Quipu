"""
Configuración centralizada de logging con soporte para CloudWatch.
"""
import logging
import os
import boto3
import watchtower
import time
import socket
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

class CloudWatchConfig:
    """Configuración singleton para CloudWatch logging"""
    _configured = False
    _cloudwatch_enabled = False
    
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
            
            # Configuración de CloudWatch
            environment = cls._normalize_environment()
            log_group_name = f"/quipu/{environment}"
            region_name = os.getenv('AWS_REGION', 'us-east-2')
            
            print(f"🔧 Configurando CloudWatch:")
            print(f"   - Región: {region_name}")
            print(f"   - Grupo de logs: {log_group_name}")
            print(f"   - Entorno: {environment}")
            
            # Crear sesión de boto3
            session = boto3.Session(
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region_name
            )
            
            # Verificar conectividad y permisos
            if not cls._test_aws_connectivity(session):
                cls._configured = True
                cls._cloudwatch_enabled = False
                return False
            
            # Asegurar que el grupo de logs existe
            if not cls._ensure_log_group_exists(session, log_group_name):
                cls._configured = True
                cls._cloudwatch_enabled = False
                return False
            
            # Configurar el handler de CloudWatch
            if cls._setup_cloudwatch_handler(session, log_group_name):
                cls._cloudwatch_enabled = True
                print("✅ CloudWatch logging configurado exitosamente")
            else:
                cls._cloudwatch_enabled = False
                print("❌ Error configurando CloudWatch handler")
            
            cls._configured = True
            return cls._cloudwatch_enabled
            
        except Exception as e:
            print(f"⚠️ Error inesperado configurando CloudWatch: {e}")
            cls._configured = True
            cls._cloudwatch_enabled = False
            return False
    
    @classmethod
    def _normalize_environment(cls):
        """Normalizar el nombre del entorno"""
        environment = os.getenv('ENVIRONMENT', 'development').lower().strip()
        
        # Mapear variaciones comunes
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
            # Hacer una llamada simple para verificar conectividad
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
                print(f"📁 Grupo de logs ya existe: {log_group_name}")
                return True
            
            # Crear el grupo de logs
            print(f"📁 Creando grupo de logs: {log_group_name}")
            logs_client.create_log_group(logGroupName=log_group_name)
            
            # Esperar un momento para que se propague
            time.sleep(2)
            
            print(f"✅ Grupo de logs creado: {log_group_name}")
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'ResourceAlreadyExistsException':
                print(f"📁 Grupo de logs ya existe: {log_group_name}")
                return True
            else:
                print(f"❌ Error creando grupo de logs ({error_code}): {e}")
                return False
        except Exception as e:
            print(f"❌ Error inesperado creando grupo de logs: {e}")
            return False
    
    @classmethod
    def _setup_cloudwatch_handler(cls, session, log_group_name):
        """Configurar el handler de CloudWatch en el root logger"""
        try:
            root_logger = logging.getLogger()
            
            # Verificar si ya tiene un handler de CloudWatch
            has_cw_handler = any(isinstance(h, watchtower.CloudWatchLogHandler) 
                               for h in root_logger.handlers)
            
            if has_cw_handler:
                print("📝 Handler de CloudWatch ya configurado")
                return True
            
            # Crear nombre único para el stream
            hostname = socket.gethostname()
            stream_name = f"quipu-{hostname}-{int(time.time())}"
            
            # Configurar handler usando la sintaxis que funciona (boto3_client)
            print("📝 Configurando CloudWatch handler...")
            
            # Crear cliente de logs
            logs_client = session.client('logs')
            
            # Crear handler con la sintaxis correcta
            handler = watchtower.CloudWatchLogHandler(
                log_group=log_group_name,
                stream_name=stream_name,
                boto3_client=logs_client,
                create_log_group=True,
                create_log_stream=True,
                use_queues=False,  # Para logging inmediato
                send_interval=5,   # Enviar cada 5 segundos
                max_batch_size=50  # Tamaño de lote
            )
            
            print("✅ Handler CloudWatch creado exitosamente")
            
            # Configurar formato
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            handler.setLevel(logging.INFO)
            
            # Agregar al root logger
            root_logger.addHandler(handler)
            
            # Asegurar que el nivel del root logger permite INFO
            if root_logger.level > logging.INFO:
                root_logger.setLevel(logging.INFO)
            
            print(f"📝 Handler CloudWatch agregado: {stream_name}")
            
            # Test inmediato
            test_logger = logging.getLogger('cloudwatch.setup')
            test_logger.info("✅ CloudWatch handler configurado y funcionando")
            
            # Forzar flush inmediato
            if hasattr(handler, 'flush'):
                handler.flush()
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando handler CloudWatch: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @classmethod
    def _load_env_vars(cls):
        """Cargar variables de entorno desde archivos .env"""
        project_root = Path(__file__).parent
        env_file = None
        
        # Determinar qué archivo usar
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
                            
                            # Solo establecer si no está ya configurada
                            if key not in os.environ:
                                os.environ[key] = value
                        except ValueError:
                            print(f"⚠️ Línea {line_num} ignorada en {env_file}: formato inválido")

def get_logger(name: str) -> logging.Logger:
    """
    Obtener un logger configurado con CloudWatch (si está habilitado).
    
    Args:
        name: Nombre del logger (generalmente __name__)
    
    Returns:
        Logger configurado
    """
    # Configurar CloudWatch si no se ha hecho
    CloudWatchConfig.setup_global_cloudwatch()
    
    # Retornar el logger
    logger = logging.getLogger(name)
    
    # Asegurar que el logger hereda la configuración del root
    logger.setLevel(logging.NOTSET)  # Usar el nivel del parent
    
    return logger

def force_cloudwatch_flush():
    """Forzar el envío inmediato de logs a CloudWatch"""
    try:
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, watchtower.CloudWatchLogHandler):
                handler.flush()
        print("🚀 Logs enviados a CloudWatch")
    except Exception as e:
        print(f"⚠️ Error enviando logs: {e}")

def test_cloudwatch_logging():
    """Función de test para verificar que CloudWatch funciona"""
    logger = get_logger('cloudwatch.test')
    
    print("\n=== INICIANDO PRUEBA DE CLOUDWATCH ===")
    
    logger.info("🧪 TEST: Mensaje de información")
    logger.warning("🧪 TEST: Mensaje de advertencia")
    logger.error("🧪 TEST: Mensaje de error")
    
    # Forzar envío
    force_cloudwatch_flush()
    
    print("=== PRUEBA COMPLETADA ===")
    print("Verifica los logs en AWS CloudWatch Console")
    
    # Mostrar URL directa si es posible
    try:
        environment = CloudWatchConfig._normalize_environment()
        region = os.getenv('AWS_REGION', 'us-east-2')
        log_group = f"/quipu/{environment}"
        
        # URL de CloudWatch (encoded)
        import urllib.parse
        encoded_group = urllib.parse.quote(log_group, safe='')
        url = f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{encoded_group}"
        print(f"🔗 URL CloudWatch: {url}")
    except:
        pass

if __name__ == "__main__":
    # Script de test directo
    test_cloudwatch_logging()

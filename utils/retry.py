import time
from functools import wraps

def retry(max_retries, delay, exceptions=(Exception,)):
    """
    Decorador para reintentar la ejecución de una función en caso de error.
    :param max_retries: Número máximo de reintentos.
    :param delay: Tiempo de espera entre reintentos en segundos.
    :param exceptions: Excepciones que activarán un reintento.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    print(f"Error: {e}. Reintentando {attempts}/{max_retries} en {delay} segundos...")
                    time.sleep(delay)
            raise Exception(f"Función {func.__name__} falló después de {max_retries} intentos.")
        return wrapper
    return decorator

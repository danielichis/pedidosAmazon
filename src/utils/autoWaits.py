import functools
import time
def retry_on_exception(max_retries):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    print("intentando...con decorador...")
                    #validar que el tamaño de ordersCardList sea 10
                    if len(args[0].orderCards_list)==10:
                        return func(*args, **kwargs)
                    else:
                        raise Exception("No se cargaron las 10 tarjetas")
                except Exception as e:
                    last_exception = e
                    print(e)
                    print("reintentando...con decorador...")
                    time.sleep(1)
                    
            raise last_exception
        return wrapper
    return decorator
from functools import lru_cache

# maxsize=128 - int, максимальный размер кеша (128 по умолчанию)
@lru_cache(maxsize=16)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

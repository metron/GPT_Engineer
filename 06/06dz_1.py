from functools import reduce
from time import time


def execution_timer(func):
    def wrapper(*args):
        start_time = time()
        res = func(*args)
        end_time = time()
        print(f"Время выполнения функции '{func.__name__}': {(end_time - start_time):.4f} секунд")
        print(f"Результат: {res}")
        return res
    return wrapper


@execution_timer
def calculate_sum_of_squares(num_list):
    res = reduce(
        lambda x, y: x + y**2,
        num_list,
        0
    )
    return res


calculate_sum_of_squares(range(1, 1000001))

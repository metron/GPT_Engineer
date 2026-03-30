def info_kwargs1(**kwargs):
    return info_kwargs(**kwargs)


def info_kwargs(**kwargs):
    for k in sorted(kwargs.keys()):
        print(k, kwargs[k])

info_kwargs1(first_name='Михаил', last_name='Деркунов', age=36, job='Учитель')

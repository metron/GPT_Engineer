def func_outer():
    a = 1
    b = 'line'
    c = [1, 2, 3]

    def func_inner():
        return a, b, c

    return func_inner


call_func = func_outer()

print(call_func)

cfc = call_func.__closure__
print(cfc)
for item in cfc:
    print(item, " - ", item.cell_contents)

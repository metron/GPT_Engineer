def func():
    return "Привет, VSC!"

with open ("result.txt", "w") as f:
    f.write(func())

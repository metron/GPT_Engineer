

def f():
    try:
        print("111")
        return "try"
    finally:
        return "finally"
print(f())


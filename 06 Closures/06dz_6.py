def sig(num):
    return "-" if num<0 else "+"


def quadratic_solver(a, b, c):
    def calculate(x):
        D = b ** 2 - 4 * a * c
        if D < 0:
            print(f"При данном x={x} исходное выражение {a}x^2 {sig(b)} {abs(b)}x {sig(c)} {abs(c)} = {a * x**2 + b*x + c}")
            return f"Результата не будет, потому что D = {D}"
        else:
            # Вычисляем корни уравнения
            x1 = (-b + D ** 0.5) / (2 * a)
            x2 = (-b - D ** 0.5) / (2 * a)
            return f"Корни уравнения {a}x^2 {sig(b)} {abs(b)}x {sig(c)} {abs(c)} = 0: x1 = {x1}, x2 = {x2}"

    return calculate


# Пример использования
solver = quadratic_solver(1, -3, 2)  # a=1, b=-3, c=2
result = solver(0)
print(result)

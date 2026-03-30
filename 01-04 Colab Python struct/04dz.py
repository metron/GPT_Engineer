lst = [
    ["id1", [["name", "Петя"], ["age", 22]]],
    ["id2", [["name", "Вася"], ["age", 23]]],
    ["id3", [["name", "Оля"], ["age", 21]]],
    ["id4", [["name", "Вика"], ["age", 23]]],
    ["id5", [["name", "Ксения"], ["age", 22]]],
]
students_data = {k: dict(v) for k, v in lst}

print(*[data["name"] for data in students_data.values()])
sum_age = 0
for data in students_data.values():
    sum_age += data["age"]
avg_age = sum_age / len(students_data)
print(f"Средний возраст студентов: {avg_age}")

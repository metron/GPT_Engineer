import re


text = "Контакты: alice@mail.com, bob@gmail.com, support@company.org"
emails = re.findall(r"\w+[@]\w+.\w+", text)
print(f"Найденные email-адреса: {emails}")

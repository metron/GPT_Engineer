"""
Создаёт архив example.zip и добавляет в него файлы file1.txt и file2.txt (создайте эти файлы вручную в Colab).
Извлекает содержимое архива в папку unzipped_folder

Результат выпонения может быть примерно такой:

Архив 'example.zip' создан.
Архив извлечён в папку 'unzipped_folder'.
"""
from zipfile import ZipFile


arc_name = "example.zip"
# Создаём файлы
with ZipFile(arc_name, "w") as zip_f:
    for i in range(1, 3):
        f_name = f"file{i}.txt"
        with open(f_name, "w") as f:
            f.write(f"{i}")
            print(f"Файл {f_name} создан")
        zip_f.write(f_name)

print(f"Архив {arc_name} создан")

with ZipFile(arc_name, "r") as f:
    f.extractall("unzipped_folder")
print("Архив извлечён в папку 'unzipped_folder'.")

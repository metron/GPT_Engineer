import shutil
from pathlib import Path


Path("test_folder").mkdir(exist_ok=True)
print("Создана папка 'test_folder'.")
with open("example.txt", "w") as f:
    f.write("")
print("Создан файл 'example.txt'.")
shutil.copy("example.txt", "test_folder/")
print("Файл 'example.txt' скопирован в папку 'test_folder'.")
shutil.move("test_folder/example.txt", "test_folder/copied_example.txt")
print("Файл переименован в 'test_folder/copied_example.txt'.")
shutil.rmtree("test_folder/")
print("Папка 'test_folder' удалена.")

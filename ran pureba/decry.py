from cryptography.fernet import Fernet
import os

def retornarKey():
    return open("key.key", "rb").read()

def decrypt(items, key):
    i = Fernet(key)
    for x in items:
        with open(x, "rb") as file:
            file_data = file.read()
        data = i.decrypt(file_data)
        with open(x, "wb") as file:
            file.write(data)

if __name__ == "__main__":
    archivos = "c:\\Users\\Julieta\\Documents\\encryptar"
    items = os.listdir(archivos)
    archivos_2 = [archivos + "\\" + x for x in items if x != "readme.txt" and x != "key.key"]

    key = retornarKey()
    decrypt(archivos_2, key)

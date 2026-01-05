import yt_dlp
import os
import shutil

def generate_token():
    print("--- GENERADOR DE TOKEN OAUTH2 PARA YOUTUBE ---")
    print("Este script iniciará el proceso de login de 'YouTube on TV'.")
    print("Sigue las instrucciones que aparecerán en pantalla (ir a google.com/device e introducir el código).")
    print("------------------------------------------------")

    # Carpeta local para guardar el token
    cache_dir = "oauth2_cache"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)

    ydl_opts = {
        'username': 'oauth2',
        'password': '', # Contraseña vacía activa el flujo OAuth2
        'cachedir': cache_dir, # Guardar tokens aquí
        'quiet': False,
        'no_warnings': False,
        'logger': CustomLogger(),
    }

    # Intentamos acceder a un vídeo cualquiera para forzar el login
    test_video = "https://www.youtube.com/watch?v=jNQXAC9IVRw" # Me at the zoo

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(test_video, download=False)
        
        print("\n\n[EXITO] ¡Token generado correctamente!")
        print(f"Los datos se han guardado en la carpeta: {cache_dir}")
        print("Ahora debes subir esta carpeta 'oauth2_cache' junto con tu lambda.")
        
    except Exception as e:
        print(f"\n[INFO] El proceso terminó (posiblemente éxito si ya te autenticaste): {e}")
        # A veces lanza error tras autenticar si no puede procesar el video, pero el token se guarda.
        if os.path.exists(os.path.join(cache_dir, 'yt-dlp')):
             print("[EXITO] Se detectaron archivos de caché. El token debería estar listo.")

class CustomLogger:
    def debug(self, msg):
        if "google.com/device" in msg:
            print(f"\n📢 {msg}\n")
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)
    def info(self, msg):
        if "google.com/device" in msg or "code" in msg:
            print(f"\n🔴 ACCION REQUERIDA: {msg}\n")
        pass

if __name__ == "__main__":
    generate_token()

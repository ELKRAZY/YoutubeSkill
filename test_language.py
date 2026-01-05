import urllib.request
import json
import ssl

def test_language():
    # Video Multi-Lenguaje (MrBeast) -> Tiene pistas en ES, EN, etc.
    video_id = "QdBfYzE0Fac" 
    
    # Instance Piped y Invidious
    piped_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
    inv_url = f"https://inv.nadeko.net/api/v1/videos/{video_id}?hl=es"
    
    print(f"--- TESTING LANGUAGES for {video_id} ---")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {'User-Agent': 'Mozilla/5.0'}

    # 1. Test PIPED
    try:
        print("\nChecking PIPED...")
        req = urllib.request.Request(piped_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for s in data.get('audioStreams', []):
                # Imprimir keys interesantes
                print(f"  [STREAM] Mime: {s.get('mimeType')} | Lang: {s.get('language', 'N/A')} | Default: {s.get('videoOnly', 'N/A')}")
    except Exception as e:
        print(f"  Piped Error: {e}")

    # 2. Test INVIDIOUS
    try:
        print("\nChecking INVIDIOUS (?hl=es)...")
        req = urllib.request.Request(inv_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for s in data.get('adaptiveFormats', []):
                if 'audio' in s.get('type', ''):
                    print(f"  [STREAM] Type: {s.get('type')} | AudioQuality: {s.get('audioQuality')} | Container: {s.get('container')}")
                    # Invidious no suele documentar 'language' aquí, pero buscamos propiedades ocultas
                    print(f"           Keys: {list(s.keys())}")
    except Exception as e:
        print(f"  Invidious Error: {e}")

if __name__ == "__main__":
    test_language()

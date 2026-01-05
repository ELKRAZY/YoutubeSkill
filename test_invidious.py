import urllib.request
import json
import time

def test_invidious():
    video_id = "jNQXAC9IVRw" # Me at the zoo
    # Lista de instancias públicas estables
    instances = [
        "https://inv.nadeko.net",
        "https://invidious.privacyredirect.com",
        "https://invidious.nerdvpn.de",
        "https://invidious.jing.rocks"
    ]
    
    print(f"--- TESTING INVIDIOUS API for {video_id} ---")

    for base_url in instances:
        api_url = f"{base_url}/api/v1/videos/{video_id}"
        print(f"\nTrying: {base_url} ...")
        
        try:
            req = urllib.request.Request(
                api_url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # Buscar adaptiveFormats (audio)
                    formats = data.get('adaptiveFormats', [])
                    audio_url = None
                    
                    for f in formats:
                        # Priorizar audio/mp4 o audio/webm
                        mime = f.get('type', '')
                        if 'audio' in mime:
                            print(f"  [FOUND] {mime} | itag: {f.get('itag')}")
                            audio_url = f.get('url')
                            break # Nos quedamos con el primero que sirva
                    
                    if audio_url:
                        print(f"  [SUCCESS] URL: {audio_url[:50]}...")
                        return # Éxito, terminamos
                    else:
                        print("  [WARN] Video data found, but no audio streams?")
                else:
                    print(f"  [FAIL] HTTP {response.getcode()}")
                    
        except Exception as e:
            print(f"  [ERROR] {e}")

if __name__ == "__main__":
    test_invidious()

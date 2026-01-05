import urllib.request
import json
import time

def test_instances():
    video_id = "jNQXAC9IVRw" # Me at the zoo
    
    # MIX de Piped (API) e Invidious (API)
    # Formato: (URL_BASE, TIPO)
    targets = [
        ("https://vid.puffyan.us", "invidious"),
        ("https://invidious.drgns.space", "invidious"),
        ("https://inv.tux.pizza", "invidious"),
        ("https://invidious.lunar.icu", "invidious"),
        ("https://inv.nadeko.net", "invidious"), 
        ("https://pipedapi.systemless.xyz", "piped"),
        ("https://pipedapi.smnz.de", "piped"),
        ("https://pipedapi.kavin.rocks", "piped"),
        ("https://api.piped.privacy.com.de", "piped")
    ]
    
    print(f"--- TESTING EXTENSIVE LIST for {video_id} ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    for base_url, type_ in targets:
        print(f"\nChecking {type_}: {base_url} ...")
        
        url = ""
        if type_ == "invidious":
            url = f"{base_url}/api/v1/videos/{video_id}"
        else: # piped
            url = f"{base_url}/streams/{video_id}"
            
        try:
            req = urllib.request.Request(url, headers=headers)
            # Timeout corto para no eternizar
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # Verificación rápida
                    found_audio = False
                    if type_ == "invidious":
                        for f in data.get('adaptiveFormats', []):
                            if 'audio' in f.get('type', ''): found_audio = True; break
                    else: # piped
                        for f in data.get('audioStreams', []):
                            if 'audio' in f.get('mimeType', ''): found_audio = True; break
                    
                    if found_audio:
                        print(f"  ✅ [ALIVE & WORKING] -> {base_url}")
                        # Si encontramos uno, paramos y lo reportamos como candidato
                        return 
                    else:
                         print("  [WARN] 200 OK but no audio streams?")
                else:
                    print(f"  [FAIL] HTTP {response.getcode()}")

        except Exception as e:
            print(f"  [ERROR] {e}")

if __name__ == "__main__":
    test_instances()

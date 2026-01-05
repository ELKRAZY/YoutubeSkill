import urllib.request
import json

def test_cobalt():
    video_id = "jNQXAC9IVRw" # Me at the zoo
    url = "https://api.cobalt.tools/api/json"
    
    # Payload v7/standard for Cobalt
    data = {
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "aFormat": "mp3",
        "isAudioOnly": True
    }
    
    print(f"Testing Cobalt API with data: {data}")
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Content-Type': 'application/json', 
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            resp_content = response.read().decode('utf-8')
            print("\n[SUCCESS] Response:")
            print(resp_content)
            
    except urllib.error.HTTPError as e:
        print(f"\n[ERROR] HTTP {e.code}: {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    test_cobalt()

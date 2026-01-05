"""
Helper module para interactuar con YouTube Data API v3
"""
import os
import json
import shutil
import logging
import yt_dlp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class YouTubeHelper:
    """Clase para manejar búsquedas en YouTube"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        
        if not self.api_key:
            try:
                current_dir_secrets = os.path.join(os.path.dirname(__file__), 'secrets.json')
                parent_dir_secrets = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'secrets.json')
                
                secrets_path = None
                if os.path.exists(current_dir_secrets):
                    secrets_path = current_dir_secrets
                elif os.path.exists(parent_dir_secrets):
                    secrets_path = parent_dir_secrets

                if secrets_path:
                    with open(secrets_path, 'r') as f:
                        secrets = json.load(f)
                        self.api_key = secrets.get('youtube', {}).get('api_key') or secrets.get('YOUTUBE_API_KEY')
            except Exception as e:
                logger.error(f"No se pudo leer secrets.json: {e}")

        if not self.api_key:
            self.api_key = os.environ.get('YOUTUBE_API_KEY')

        if not self.api_key:
            raise ValueError("YouTube API key no encontrada.")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def search_videos(self, query, max_results=1):
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='relevance'
            ).execute()
            
            videos = []
            for search_result in search_response.get('items', []):
                if search_result['id']['kind'] == 'youtube#video':
                    video_info = {
                        'video_id': search_result['id']['videoId'],
                        'title': search_result['snippet']['title'],
                        'description': search_result['snippet']['description'],
                        'channel': search_result['snippet']['channelTitle'],
                        'url': f"https://www.youtube.com/watch?v={search_result['id']['videoId']}"
                    }
                    videos.append(video_info)
            return videos
        except HttpError as e:
            logger.error(f'Error en la búsqueda de YouTube: {e}')
            return []
    
    def get_channel_latest_video(self, channel_id):
        try:
            search_response = self.youtube.search().list(
                channelId=channel_id,
                part='id,snippet',
                maxResults=1,
                order='date',
                type='video'
            ).execute()
            
            if search_response.get('items'):
                video = search_response['items'][0]
                return {
                    'video_id': video['id']['videoId'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'url': f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                }
            return None
        except HttpError as e:
            logger.error(f'Error obteniendo último video: {e}')
            return None

    def get_channel_id_by_name(self, channel_name):
        try:
            search_response = self.youtube.search().list(
                q=channel_name,
                type='channel',
                part='id',
                maxResults=1
            ).execute()
            if search_response.get('items'):
                return search_response['items'][0]['id']['channelId']
            return None
        except HttpError as e:
            logger.error(f'Error buscando canal: {e}')
            return None

    def get_audio_url(self, video_id):
        """
        Extracción HÍBRIDA V8 (Local + Remote Fallback):
        1. Intenta extracción local V7 (TV/Android).
        2. Si falla (bloqueo Lambda), usa Cobalt API (Remote Resolver).
        """
        logger.info(f"--- INICIO EXTRACCION V8 (Hybrid): {video_id} ---")
        
        # --- FASE 1: Intento Local (V7) ---
        local_url = self._get_local_url(video_id)
        if local_url:
            return local_url
            
        # --- FASE 2: Remote Fallback (Multi-Instance) ---
        logger.warning(f"FALLO LOCAL V7. Iniciando FASE 2: Remote Resolver (Redundante)...")
        return self._get_remote_fallback(video_id)

    def _get_local_url(self, video_id):
        """Lógica V7 original para intento local (con preferencia de idioma)"""
        temp_cookies_path = '/tmp/yt_cookies.txt'
        local_cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
        cookiefile = None
        if os.path.exists(local_cookies_path):
            try:
                shutil.copy2(local_cookies_path, temp_cookies_path)
            except Exception:
                pass

        strategies = [
            {'name': 'TV-Embedded', 'args': {'player_client': ['tv']}},
            {'name': 'Android-Native', 'args': {'player_client': ['android', 'android_creator']}}
        ]

        for s in strategies:
            logger.info(f"TRYING LOCAL: {s['name']}...")
            ydl_opts = {
                'cookiefile': cookiefile,
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'youtube_include_dash_manifest': True,
                'check_formats': False,
                # Preferencia de Idioma: Español > Inglés > Original > Mejor Calidad
                # Evita pistas 'translated' si es posible.
                'format_sort': ['lang:es', 'lang:en', 'ext'], 
                'format': 'bestaudio[format_note!*=translated]/bestaudio', 
                'extractor_args': {'youtube': s['args']}
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_id, download=False)
                    if info:
                        if 'url' in info: return info['url']
                        for f in info.get('formats', []):
                            if f.get('vcodec') == 'none' and f.get('url'): return f['url']
            except Exception as e:
                logger.warning(f"FAIL LOCAL {s['name']}: {str(e)[:50]}")
        return None

    def _get_remote_fallback(self, video_id):
        """
        Sistema de Respaldo Redundante (Multi-Instance) Refinado 2026:
        Itera sobre una lista de instancias públicas (Piped/Invidious)
        hasta encontrar una que responda con audio.
        Incluye fix SSL para Lambda y Preferencia de Idioma (?hl=es).
        """
        # Lista de instancias Frescas (Enero 2026)
        instances = [
            # Invidious (API v1)
            ("https://inv.nadeko.net", "invidious"), 
            ("https://yewtu.be", "invidious"), 
            ("https://invidious.flokinet.to", "invidious"),
            ("https://invidious.f5.si", "invidious"),
            ("https://inv.perditum.com", "invidious"),
            ("https://invidious.nerdvpn.de", "invidious"),
            # Piped (Streams)
            ("https://pipedapi.kavin.rocks", "piped"),
            ("https://api.piped.privacy.com.de", "piped"),
        ]
        
        import urllib.request
        import json
        import ssl

        logger.info(f"INICIANDO FALLBACK REMOTO CON {len(instances)} INSTANCIAS...")

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        for base_url, api_type in instances:
            try:
                # Construir URL según tipo de API
                if api_type == "invidious":
                    # ?hl=es fuerza la localización de la instancia a Español
                    req_url = f"{base_url}/api/v1/videos/{video_id}?hl=es"
                else: # piped
                    req_url = f"{base_url}/streams/{video_id}"
                
                logger.info(f"Probando Remote ({api_type}): {base_url} ...")
                
                req = urllib.request.Request(
                    req_url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                )
                
                with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                    if response.getcode() == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        audio_url = None
                        
                        # Extraer URL según el formato de la API
                        if api_type == "invidious":
                            for f in data.get('adaptiveFormats', []):
                                mime = f.get('type', '')
                                if 'audio' in mime:
                                    audio_url = f.get('url')
                                    break
                        else: # piped
                            for f in data.get('audioStreams', []):
                                mime = f.get('mimeType', '')
                                if 'audio' in mime:
                                    audio_url = f.get('url')
                                    break
                        
                        if audio_url:
                            logger.info(f"EXITO REMOTE: Audio encontrado en {base_url}")
                            return audio_url
                        else:
                            logger.warning(f"FALLO PARCIAL: {base_url} respondió OK pero sin streams de audio adecuados.")
                    else:
                        logger.warning(f"FALLO HTTP {response.getcode()} en {base_url}")
                        
            except Exception as e:
                logger.warning(f"ERROR Conexión {base_url}: {str(e)[:100]}")
                continue 
        
        logger.error("FALLO TOTAL REMOTE: Ninguna instancia respondió.")
        return None

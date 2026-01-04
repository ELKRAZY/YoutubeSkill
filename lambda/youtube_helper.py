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
        Extracción de audio DEEP-SEARCH: Extraemos todos los formatos y elegimos manualmente.
        """
        logger.info(f"--- INICIO EXTRACCION DEEP-SEARCH: {video_id} ---")
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Gestion de COOKIES
        temp_cookies_path = '/tmp/yt_cookies.txt'
        local_cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
        cookiefile = None
        if os.path.exists(local_cookies_path):
            try:
                shutil.copy2(local_cookies_path, temp_cookies_path)
                cookiefile = temp_cookies_path
                logger.info("LOG: Cookies cargadas.")
            except Exception as e:
                logger.error(f"LOG ERROR Cookies: {e}")

        # Estrategias optimizadas SÓLO para pasar el login
        # NO ponemos 'format' AQUÍ para evitar que yt-dlp falle prematuramente
        strategies = [
            {
                'name': 'iOS-Headers',
                'client': ['ios'],
                'skip': ['web', 'tv'],
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
                    'Referer': 'https://www.youtube.com/',
                    'Origin': 'https://www.youtube.com'
                }
            },
            {
                'name': 'TV-Clean',
                'client': ['tv'],
                'skip': ['web', 'ios', 'android'],
                'headers': {'Referer': 'https://www.youtube.com/'}
            },
            {
                'name': 'MWeb-Fallback',
                'client': ['mweb', 'android'],
                'skip': ['web'],
                'headers': {'Referer': 'https://www.youtube.com/'}
            }
        ]

        for s in strategies:
            logger.info(f"TRYing strategy: {s['name']}")
            ydl_opts = {
                # IMPORTANTE: No ponemos 'format' para que nos devuelva TODO
                'cookiefile': cookiefile,
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'http_headers': s['headers'],
                'youtube_include_dash_manifest': True,
                'youtube_include_hls_manifest': True,
                'check_formats': False, 
                'extractor_args': {
                    'youtube': {
                        'player_client': s['client'],
                        'player_skip': s['skip']
                    }
                }
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    
                    if not info or 'formats' not in info:
                        logger.warning(f"No formats found for {s['name']}")
                        continue
                    
                    # BUSQUEDA MANUAL DE URL
                    # Prioridad: 1. Audio m4a/mp3, 2. Cualquier Audio, 3. Cualquier Stream con URL
                    formats = info['formats']
                    logger.info(f"Found {len(formats)} potential formats for {s['name']}")
                    
                    # Candidatos
                    audio_urls = []
                    mixed_urls = []
                    
                    for f in formats:
                        url = f.get('url')
                        if not url: continue
                        
                        acodec = f.get('acodec', 'none')
                        vcodec = f.get('vcodec', 'none')
                        
                        if acodec != 'none' and vcodec == 'none':
                            # Es audio puro
                            # Preferir m4a (que suele ser aceptado por Alexa)
                            prio = 10 if f.get('ext') == 'm4a' else 5
                            audio_urls.append((prio, url))
                        elif url:
                            mixed_urls.append(url)
                            
                    if audio_urls:
                        # Ordenar por prioridad y devolver la mejor
                        audio_urls.sort(key=lambda x: x[0], reverse=True)
                        logger.info(f"SUCCESS: Found AUDIO URL via {s['name']}!")
                        return audio_urls[0][1]
                        
                    if mixed_urls:
                        logger.info(f"SUCCESS: Found MIXED URL via {s['name']}!")
                        return mixed_urls[0]

            except Exception as e:
                logger.warning(f"FAIL {s['name']}: {str(e)[:150]}")
            
        logger.error(f"--- FIN EXTRACCION (FALLO TOTAL) ---")
        return None

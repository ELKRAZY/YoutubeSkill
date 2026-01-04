"""
Helper module para interactuar con YouTube Data API v3
"""
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeHelper:
    """Clase para manejar búsquedas en YouTube"""
    
    def __init__(self, api_key=None):
        """
        Inicializa el helper de YouTube
        
        Args:
            api_key: API key de YouTube Data API v3
                    Prioridad: 
                    1. Argumento api_key
                    2. secrets.json (si existe)
                    3. Variable de entorno YOUTUBE_API_KEY
        """
        self.api_key = api_key
        
        # Si no se pasó como argumento, intentar leer de secrets.json
        if not self.api_key:
            try:
                import json
                # Intentar primero en el directorio actual (para Lambda)
                current_dir_secrets = os.path.join(os.path.dirname(__file__), 'secrets.json')
                # Intentar luego en el directorio padre (para desarrollo local)
                parent_dir_secrets = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'secrets.json')
                
                secrets_path = None
                if os.path.exists(current_dir_secrets):
                    secrets_path = current_dir_secrets
                elif os.path.exists(parent_dir_secrets):
                    secrets_path = parent_dir_secrets

                if secrets_path:
                    with open(secrets_path, 'r') as f:
                        secrets = json.load(f)
                        # Busca en secrets['youtube']['api_key'] o en secrets['YOUTUBE_API_KEY']
                        self.api_key = secrets.get('youtube', {}).get('api_key') or secrets.get('YOUTUBE_API_KEY')
            except Exception as e:
                print(f"No se pudo leer secrets.json: {e}")

        # Si aún no tenemos key, intentar variable de entorno
        if not self.api_key:
            self.api_key = os.environ.get('YOUTUBE_API_KEY')

        if not self.api_key:
            raise ValueError("YouTube API key no encontrada. Configúrala en secrets.json o variable de entorno YOUTUBE_API_KEY")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def search_videos(self, query, max_results=1):
        """
        Busca videos en YouTube
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados (default: 1)
            
        Returns:
            Lista de diccionarios con información de videos
        """
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
            print(f'Error en la búsqueda de YouTube: {e}')
            return []
    
    def get_channel_latest_video(self, channel_id):
        """
        Obtiene el último video de un canal
        
        Args:
            channel_id: ID del canal de YouTube
            
        Returns:
            Diccionario con información del video más reciente
        """
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
            print(f'Error obteniendo último video: {e}')
            return None

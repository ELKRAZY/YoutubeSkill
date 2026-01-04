import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# Importar helper de YouTube
from youtube_helper import YouTubeHelper
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler para cuando el usuario abre la skill"""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Bienvenido a YouTube. ¿Qué quieres escuchar o ver?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class SearchIntentHandler(AbstractRequestHandler):
    """Handler para búsquedas generales (SearchIntent)"""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SearchIntent")(handler_input)

    def handle(self, handler_input):
        # Obtener el término de búsqueda del slot "query"
        slots = handler_input.request_envelope.request.intent.slots
        query = slots.get("query", {}).get("value", None)
        
        if not query:
            speak_output = "¿Qué quieres buscar en YouTube?"
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response

        try:
            # Inicializar YouTube Helper
            # NOTA: Asegúrate de tener YOUTUBE_API_KEY en las variables de entorno
            yt = YouTubeHelper()
            videos = yt.search_videos(query, max_results=1)
            
            if videos:
                video = videos[0]
                # Por ahora solo decimos el título. Para reproducir video se requiere APL o VideoApp
                speak_output = f"He encontrado {video['title']} del canal {video['channel']}."
                
                # TODO: Implementar directiva de VideoApp o APL para reproducir
            else:
                speak_output = f"No encontré videos para {query}."
                
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            speak_output = "Hubo un problema contactando con YouTube."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class PlayOneIntentHandler(AbstractRequestHandler):
    """Handler para reproducir una canción/video específico (PlayOneIntent)"""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("PlayOneIntent")(handler_input)

    def handle(self, handler_input):
        # Similar Logic a SearchIntent
        slots = handler_input.request_envelope.request.intent.slots
        query = slots.get("query", {}).get("value", None)
        
        if not query:
             speak_output = "¿Qué canción quieres escuchar?"
             return handler_input.response_builder.speak(speak_output).ask(speak_output).response
             
        try:
            yt = YouTubeHelper()
            videos = yt.search_videos(query, max_results=1)
            
            if videos:
                video = videos[0]
                speak_output = f"Reproduciendo {video['title']}."
            else:
                speak_output = f"No encontré la canción {query}."
                
        except Exception as e:
            logger.error(f"Error: {e}")
            speak_output = "Error al buscar la canción."

        return handler_input.response_builder.speak(speak_output).response


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Puedes pedirme que busque videos, ponga música o busque listas de reproducción."
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Adiós!"
        return handler_input.response_builder.speak(speak_output).response


class DefaultExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = "Lo siento, hubo un error. Intenta de nuevo."
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SearchIntentHandler())
sb.add_request_handler(PlayOneIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(DefaultExceptionHandler())

lambda_handler = sb.lambda_handler()

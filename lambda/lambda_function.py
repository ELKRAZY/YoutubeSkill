import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, StopDirective
)

# Importar helper de YouTube
from youtube_helper import YouTubeHelper
import os

# Configuración de LOGS para AWS Lambda
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("LAMBDA: Iniciando carga del modulo lambda_function.py")


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler para cuando el usuario abre la skill"""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("HANDLER: LaunchRequestHandler invocado.")
        speak_output = "Bienvenido a YouTube. ¿Qué quieres escuchar?"
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
        logger.info("HANDLER: SearchIntentHandler invocado.")
        # Obtener el término de búsqueda del slot "query"
        slots = handler_input.request_envelope.request.intent.slots
        query = None
        if slots and "query" in slots and slots["query"].value:
            query = slots["query"].value
        
        if not query:
            speak_output = "¿Qué quieres buscar en YouTube?"
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response

        try:
            yt = YouTubeHelper()
            videos = yt.search_videos(query, max_results=1)
            
            if videos:
                video = videos[0]
                # Obtener URL de audio
                audio_url = yt.get_audio_url(video['video_id'])
                
                if audio_url:
                    speak_output = f"Reproduciendo {video['title']} del canal {video['channel']}."
                    return (
                        handler_input.response_builder
                            .speak(speak_output)
                            .add_directive(
                                PlayDirective(
                                    play_behavior=PlayBehavior.REPLACE_ALL,
                                    audio_item=AudioItem(
                                        stream=Stream(
                                            token=video['video_id'],
                                            url=audio_url,
                                            offset_in_milliseconds=0,
                                            expected_previous_token=None),
                                        metadata=None))
                            )
                            .response
                    )
                else:
                    speak_output = f"Lo siento, no pude extraer el audio de {video['title']}."
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



class SearchLastIntentHandler(AbstractRequestHandler):
    """Handler para buscar el último video de un canal (SearchLastIntent)"""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SearchLastIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("HANDLER: SearchLastIntentHandler invocado.")
        slots = handler_input.request_envelope.request.intent.slots
        query = None
        if slots and "query" in slots and slots["query"].value:
            query = slots["query"].value
            
        if not query:
            speak_output = "¿De qué canal quieres buscar el último video?"
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response

        try:
            yt = YouTubeHelper()
            # 1. Buscar ID del canal
            channel_id = yt.get_channel_id_by_name(query)
            
            if channel_id:
                # 2. Buscar último video del canal
                video = yt.get_channel_latest_video(channel_id)
                if video:
                    audio_url = yt.get_audio_url(video['video_id'])
                    
                    if audio_url:
                        speak_output = f"Reproduciendo el último video de {query}: {video['title']}."
                        return (
                            handler_input.response_builder
                                .speak(speak_output)
                                .add_directive(
                                    PlayDirective(
                                        play_behavior=PlayBehavior.REPLACE_ALL,
                                        audio_item=AudioItem(
                                            stream=Stream(
                                                token=video['video_id'],
                                                url=audio_url,
                                                offset_in_milliseconds=0,
                                                expected_previous_token=None),
                                            metadata=None))
                                )
                                .response
                        )
                    else:
                        speak_output = f"Encontré el video {video['title']} pero no pude obtener el audio."
                else:
                    speak_output = f"No encontré videos recientes en el canal {query}."
            else:
                speak_output = f"No encontré ningún canal llamado {query}."

        except Exception as e:
            logger.error(f"Error en SearchLastIntent: {e}")
            speak_output = "Hubo un problema contactando con YouTube."

        return handler_input.response_builder.speak(speak_output).response


class PlayOneIntentHandler(AbstractRequestHandler):
    """Handler para reproducir una canción/video específico (PlayOneIntent)"""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("PlayOneIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("HANDLER: PlayOneIntentHandler invocado.")
        # Similar Logic a SearchIntent
        slots = handler_input.request_envelope.request.intent.slots
        query = None
        if slots and "query" in slots and slots["query"].value:
            query = slots["query"].value
        
        if not query:
             speak_output = "¿Qué canción quieres escuchar?"
             return handler_input.response_builder.speak(speak_output).ask(speak_output).response
             
        try:
            yt = YouTubeHelper()
            videos = yt.search_videos(query, max_results=1)
            
            if videos:
                video = videos[0]
                audio_url = yt.get_audio_url(video['video_id'])
                
                if audio_url:
                    speak_output = f"Reproduciendo {video['title']}."
                    return (
                        handler_input.response_builder
                            .speak(speak_output)
                            .add_directive(
                                PlayDirective(
                                    play_behavior=PlayBehavior.REPLACE_ALL,
                                    audio_item=AudioItem(
                                        stream=Stream(
                                            token=video['video_id'],
                                            url=audio_url,
                                            offset_in_milliseconds=0,
                                            expected_previous_token=None),
                                        metadata=None))
                            )
                            .response
                    )
                else:
                    speak_output = "No pude obtener el audio."
            else:
                speak_output = f"No encontré la canción {query}."
                
        except Exception as e:
            logger.error(f"Error: {e}")
            speak_output = "Error al buscar la canción."

        return handler_input.response_builder.speak(speak_output).response


# AudioPlayer Handlers (Events)
class AudioPlayerEventHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_request_type("AudioPlayer.PlaybackStarted")(handler_input) or
                ask_utils.is_request_type("AudioPlayer.PlaybackFinished")(handler_input) or
                ask_utils.is_request_type("AudioPlayer.PlaybackStopped")(handler_input) or
                ask_utils.is_request_type("AudioPlayer.PlaybackNearlyFinished")(handler_input) or
                ask_utils.is_request_type("AudioPlayer.PlaybackFailed")(handler_input))

    def handle(self, handler_input):
        # No responder nada, solo aceptar el evento
        return handler_input.response_builder.response

class PauseIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.PauseIntent")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.add_directive(
            StopDirective()
        ).response

class ResumeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Lo siento, no puedo reanudar la reproducción aún."
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
    """Handler para el cierre de sesión"""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class CatchAllRequestHandler(AbstractRequestHandler):
    """Handler para capturar cualquier petición no manejada"""
    def can_handle(self, handler_input):
        return True

    def handle(self, handler_input):
        logger.info(f"CATCH ALL: Peticion de tipo {handler_input.request_envelope.request.object_type} no manejada.")
        return handler_input.response_builder.response


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SearchIntentHandler())
sb.add_request_handler(SearchLastIntentHandler())
sb.add_request_handler(PlayOneIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Add AudioPlayer handlers
sb.add_request_handler(AudioPlayerEventHandler())
sb.add_request_handler(PauseIntentHandler())
sb.add_request_handler(ResumeIntentHandler())

# EL ÚLTIMO: Catch All
sb.add_request_handler(CatchAllRequestHandler())

sb.add_exception_handler(DefaultExceptionHandler())

lambda_handler = sb.lambda_handler()

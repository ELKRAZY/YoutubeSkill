import logging
import os
import sys

# Simular entorno Lambda añadiendo lambda_pkg y directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'lambda_pkg'))
sys.path.append(current_dir)

from lambda_function import lambda_handler

# Mock del evento de Alexa SearchIntent
fake_event = {
    "version": "1.0",
    "session": {
        "new": True,
        "sessionId": "amzn1.echo-api.session.1234",
        "application": {
            "applicationId": "amzn1.ask.skill.9bfc9c99-587c-4c7d-8811-7fb824470224"
        },
        "user": {
            "userId": "amzn1.ask.account.TEST"
        }
    },
    "context": {
        "System": {
            "application": {
                "applicationId": "amzn1.ask.skill.9bfc9c99-587c-4c7d-8811-7fb824470224"
            },
            "user": {
                "userId": "amzn1.ask.account.TEST"
            },
            "device": {
                "supportedInterfaces": {}
            }
        }
    },
    "request": {
        "type": "IntentRequest",
        "requestId": "amzn1.echo-api.request.1234",
        "timestamp": "2024-01-01T00:00:00Z",
        "locale": "es-ES",
        "intent": {
            "name": "SearchIntent",
            "confirmationStatus": "NONE",
            "slots": {
                "query": {
                    "name": "query",
                    "value": "musica de queen",
                    "confirmationStatus": "NONE"
                }
            }
        }
    }
}

print("--- Iniciando Prueba Local ---")
try:
    response = lambda_handler(fake_event, None)
    print("Respuesta de Lambda:")
    print(response)
except Exception as e:
    print("CRASH en Lambda:")
    print(e)
    import traceback
    traceback.print_exc()

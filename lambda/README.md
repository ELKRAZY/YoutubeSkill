# Lambda Function - YouTube Alexa Skill

Esta carpeta contiene el código de la función Lambda para la Alexa Skill de YouTube.

## Estructura

- `lambda_function.py`: Punto de entrada principal de la Lambda function
- `youtube_helper.py`: Módulo helper para interactuar con YouTube Data API v3
- `requirements.txt`: Dependencias de Python

## Configuración

### 1. Obtener YouTube API Key

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita **YouTube Data API v3**
4. Ve a "Credenciales" y crea una **API Key**
5. Copia la API key

### 2. Configurar Variables de Entorno en Lambda

Cuando subas esta función a AWS Lambda, necesitas configurar:

- **Variable de entorno**: `YOUTUBE_API_KEY`
- **Valor**: Tu API key de YouTube

## Instalación Local (para pruebas)

```bash
cd lambda
pip install -r requirements.txt
```

## Próximos Pasos

1. **Mejorar el modelo de interacción**: Agregar slots para capturar términos de búsqueda
2. **Implementar la búsqueda**: Integrar `youtube_helper.py` en `YoutubeIntentHandler`
3. **Manejar respuestas**: Formatear las respuestas de Alexa con información de videos
4. **Probar localmente**: Usar ASK CLI para pruebas locales
5. **Desplegar**: Subir a AWS Lambda y conectar con tu Alexa Skill

## Despliegue

### Opción 1: ASK CLI (Recomendado)
```bash
ask deploy
```

### Opción 2: Manual
1. Comprimir la carpeta `lambda/` con todas las dependencias
2. Subir el ZIP a AWS Lambda
3. Configurar el handler: `lambda_function.lambda_handler`
4. Agregar la variable de entorno `YOUTUBE_API_KEY`
5. Conectar el ARN de Lambda con tu Alexa Skill

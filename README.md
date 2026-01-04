# YouTube Alexa Skill

Skill de Alexa para reproducir contenido de YouTube mediante comandos de voz.

## Configuración

### 1. Secrets
Antes de desplegar el skill, necesitas configurar tus credenciales:

1. Copia el archivo de ejemplo:
   ```bash
   cp secrets.example.json secrets.json
   ```

2. Edita `secrets.json` con tus valores reales:
   - **Lambda ARN**: El ARN de tu función Lambda en AWS
   - **YouTube API Key**: Tu clave de API de YouTube Data API v3
   - **AWS Account ID**: Tu ID de cuenta de AWS

### 2. YouTube API Key
Para obtener tu API key de YouTube:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **YouTube Data API v3**
4. Ve a "Credenciales" y crea una **API Key**
5. Copia la clave en `secrets.json`

### 3. AWS Lambda
Necesitas crear una función Lambda para el backend del skill:

1. Ve a [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Crea una nueva función
3. Configura el trigger de Alexa Skills Kit
4. Copia el ARN de la función en `secrets.json`

## Estructura del Proyecto

```
YoutubeSkill/
├── skill-package/
│   ├── interactionModels/
│   │   └── custom/
│   │       └── es-ES.json          # Modelo de interacción en español
│   └── skill.json                   # Configuración del skill
├── lambda/                          # (Próximamente) Código Lambda
├── secrets.json                     # Configuración sensible (NO SUBIR A GIT)
├── secrets.example.json             # Plantilla de configuración
└── ask-resources.json               # Recursos ASK CLI

```

## Comandos Disponibles

El skill soporta los siguientes tipos de comandos:

- **Búsqueda**: "Alexa, pídele a YouTube que busque [consulta]"
- **Reproducción**: "Alexa, pídele a YouTube que ponga [canción/video]"
- **Control**: "Alexa, pausa", "Alexa, siguiente", "Alexa, anterior"
- **Playlists**: "Alexa, pídele a YouTube que ponga la playlist [nombre]"
- **Canales**: "Alexa, pídele a YouTube que abra el canal [nombre]"

## Próximos Pasos

1. ✅ Configurar modelo de interacción
2. ✅ Configurar secrets
3. ⏳ Implementar código Lambda
4. ⏳ Integrar YouTube Data API
5. ⏳ Implementar AudioPlayer
6. ⏳ Probar el skill

## Despliegue

### Opción 1: Usando npm scripts (Recomendado)

```bash
# Actualizar configuración y desplegar todo
npm run deploy

# Solo desplegar metadata del skill
npm run deploy-skill

# Solo desplegar infraestructura
npm run deploy-model
```

### Opción 2: Manual

```bash
# 1. Actualizar skill.json con valores de secrets.json
node update-skill-config.js

# 2. Desplegar con ASK CLI
ask deploy
```

## Seguridad

⚠️ **IMPORTANTE**: Nunca subas el archivo `secrets.json` a Git. Este archivo contiene información sensible y está incluido en `.gitignore`.

"""Configuración de la pasarela.

Todo se lee de variables de entorno (o de un fichero .env que cargas tú),
para no meter claves ni precios en el código.
"""
import os

# --- Modelo local (Ollama expone una API compatible con OpenAI) ---
LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL", "http://localhost:11434/v1")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "llama3.2:3b")

# --- Modelo de pago (cualquier proveedor compatible con la API de OpenAI) ---
PAGO_BASE_URL = os.getenv("PAGO_BASE_URL", "https://api.mistral.ai/v1")
PAGO_MODEL = os.getenv("PAGO_MODEL", "mistral-small-latest")
PAGO_API_KEY = os.getenv("PAGO_API_KEY", "")

# --- Precios en euros por cada millón de tokens ---
# Pon los precios ACTUALES de tu proveedor: cambian a menudo.
PRECIOS = {
    LOCAL_MODEL: {"entrada": 0.0, "salida": 0.0},
    PAGO_MODEL: {
        "entrada": float(os.getenv("PAGO_PRECIO_ENTRADA", "0.0")),
        "salida": float(os.getenv("PAGO_PRECIO_SALIDA", "0.0")),
    },
}

# --- Reglas del enrutador ---
# Por encima de este número de tokens estimados, la tarea se considera compleja.
UMBRAL_TOKENS_COMPLEJO = int(os.getenv("UMBRAL_TOKENS_COMPLEJO", "1500"))

# Palabras que suelen indicar una tarea compleja (ajústalas con lo que veas).
PALABRAS_COMPLEJAS = [
    "analiza", "compara", "redacta un informe", "razona", "evalúa",
    "resume este documento", "plan detallado", "código",
]

# Departamentos cuyos datos NUNCA salen del servidor local.
DEPARTAMENTOS_SOLO_LOCAL = {"padron", "servicios_sociales", "recursos_humanos"}

# --- Registro ---
RUTA_BD = os.getenv("RUTA_BD", "registro.db")

"""Configuración central de Livy.

Todo se lee del entorno para que la clave de la API nunca viva en el repositorio.
En local se toma de `backend/.env`; en Render, de las variables del servicio.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")


def _bandera(nombre: str, por_defecto: str = "0") -> bool:
    return os.getenv(nombre, por_defecto).strip().lower() in {"1", "true", "si", "sí", "yes"}


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Gemma 4 hospedado en la Gemini API. Acepta texto, imagen y video —no audio—,
# por eso la transcripción en vivo la resuelve el navegador.
GEMMA_MODELO = os.getenv("GEMMA_MODELO", "gemma-4-31b-it").strip()
GEMMA_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"

# Sin clave no hay forma de llamar al modelo: caemos a respuestas simuladas para
# que el frontend siga siendo desarrollable.
MODO_SIMULADO = _bandera("LIVY_FAKE_GEMMA") or not GEMINI_API_KEY

# El tier gratuito son 15 solicitudes por minuto. Dejamos margen deliberado.
LIMITE_POR_MINUTO = int(os.getenv("LIVY_LIMITE_RPM", "13"))

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(RAIZ / 'livy.db').as_posix()}")

CORS_ORIGENES = [o.strip() for o in os.getenv("CORS_ORIGENES", "*").split(",") if o.strip()]

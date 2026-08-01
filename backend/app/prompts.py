"""Prompts de Livy.

Se mantienen juntos y en español a propósito: son la interfaz real con Gemma 4 y
la parte del proyecto que más se itera durante el sprint. Tenerlos en un solo
archivo hace auditable, para el jurado y para nosotros, qué se le pide al modelo
en cada función del producto.
"""

from __future__ import annotations

import json
from typing import Any

SISTEMA = (
    "Eres Livy, el asistente de continuidad de un profesor de nivel medio superior "
    "y superior en México. Tu trabajo es convertir lo que ocurre en clase en memoria "
    "estructurada y llevar el avance de cada grupo contra su plan de estudios.\n"
    "Reglas que nunca rompes:\n"
    "- El profesor es el autor y el validador. Tú propones, nunca decides por él.\n"
    "- Te apegas a la evidencia: si algo no aparece en la transcripción, no lo inventas.\n"
    "- Respondes en español de México, con lenguaje claro y sin adornos.\n"
    "- Cuando se te pide JSON, devuelves JSON válido y nada más."
)


def _temas_como_lista(temas: list[dict]) -> str:
    return "\n".join(
        f"  [{t['id']}] {t['orden']}. {t['titulo']}"
        + (f" — subtemas: {', '.join(t['subtemas'])}" if t.get("subtemas") else "")
        for t in temas
    )


def leer_temario(nombre_materia: str, texto_fuente: str | None) -> str:
    """Extrae el plan de estudios de una foto o un PDF."""
    origen = (
        f"El documento viene como texto extraído de un PDF:\n---\n{texto_fuente}\n---"
        if texto_fuente
        else "El documento viene como imagen adjunta. Léela con cuidado, incluso si "
        "está fotografiada en ángulo o tiene anotaciones a mano."
    )
    return f"""Extrae el plan de estudios de la materia "{nombre_materia}" a partir del documento.

{origen}

Devuelve JSON con esta forma exacta:
{{
  "temas": [
    {{"orden": 1, "unidad": "Unidad 1. Números reales", "titulo": "Desigualdades y valor absoluto",
      "subtemas": ["Intervalos", "Propiedades del valor absoluto"]}}
  ]
}}

Criterios:
- Un elemento por tema enseñable, en el orden en que se imparte.
- Si el documento agrupa por unidades, conserva el nombre de la unidad en cada tema.
- No inventes temas que no aparezcan. Si el documento está incompleto, extrae solo lo legible.
- Si un título viene en mayúsculas o abreviado, normalízalo a capitalización normal."""


def resumir_sesion(
    materia: str,
    grupo: str,
    temas: list[dict],
    transcripcion: str,
    contexto_previo: str,
) -> str:
    """Convierte la transcripción cruda en memoria estructurada y mapea cobertura."""
    return f"""Acaba de terminar una sesión de "{materia}" con el grupo {grupo}.

Plan de estudios de la materia (usa estos identificadores tal cual):
{_temas_como_lista(temas)}

Dónde venía este grupo antes de la sesión:
{contexto_previo or "Es la primera sesión registrada del grupo."}

Transcripción de la sesión (dictada en vivo, puede traer errores de reconocimiento
de voz, muletillas y frases cortadas; interprétala con criterio):
---
{transcripcion}
---

Devuelve JSON con esta forma exacta:
{{
  "titulo": "Título breve de la sesión, máximo 8 palabras",
  "resumen": "Dos o tres párrafos de lo que ocurrió, en las ideas del profesor",
  "puntos_clave": ["Ideas centrales que un alumno debería llevarse"],
  "donde_quedo": "Frase precisa del punto exacto donde terminó la clase",
  "temas": [{{"tema_id": 5, "nivel": "cubierto", "evidencia": "cita breve de la transcripción"}}],
  "pendientes": ["Lo que quedó anunciado o prometido para la próxima sesión"],
  "dudas_detectadas": ["Puntos donde se nota confusión o preguntas repetidas del grupo"]
}}

Criterios para "temas":
- Solo temas del plan de arriba, referenciados por su identificador numérico.
- "introducido" si apenas se mencionó o se abrió el tema sin desarrollarlo.
- "cubierto" si se explicó de forma completa en esta sesión.
- "reforzado" si se repasó algo que ya se había cubierto antes.
- La "evidencia" es una cita literal y corta de la transcripción. Sin cita, no marques el tema.
- Si la clase no avanzó en el plan (por ejemplo fue examen o repaso), devuelve la lista vacía."""


def recomendar_siguiente(materia: str, estados: list[dict], sesiones_restantes: int) -> str:
    """Compara lo cubierto contra lo pendiente y sugiere el siguiente paso por sección."""
    detalle = json.dumps(estados, ensure_ascii=False, indent=2)
    return f"""Eres el copiloto del profesor de "{materia}", que imparte la misma materia a
varios grupos con avances distintos. Quedan aproximadamente {sesiones_restantes} sesiones del ciclo.

Estado real de cada grupo:
{detalle}

Devuelve JSON con esta forma exacta:
{{
  "recomendaciones": [
    {{"grupo_id": 1,
      "siguiente_tema_id": 8,
      "justificacion": "Una o dos frases apoyadas en lo que ya cubrió este grupo",
      "riesgo": "al_dia",
      "ajuste_sugerido": "Acción concreta y realista para el profesor"}}
  ]
}}

Criterios:
- Una recomendación por grupo, sin excepción.
- "riesgo" es exactamente uno de: "al_dia", "atencion", "rezagado".
- Compara el avance del grupo contra las sesiones que quedan, no contra los otros grupos.
- Si un grupo dejó un tema solo "introducido", considera cerrarlo antes de avanzar.
- El "ajuste_sugerido" debe caber en una clase real: nada de "dar tres temas en una sesión"."""


def responder_alumno(
    materia: str, grupo: str, historial: str, pregunta: str, conversacion: str
) -> str:
    """Chat anclado exclusivamente a lo que el profesor enseñó en ese grupo."""
    return f"""Un alumno del grupo {grupo} de "{materia}" tiene una duda.

Tu única fuente son las clases que su profesor impartió a ESTE grupo:
---
{historial}
---

{f"Conversación previa:{chr(10)}{conversacion}{chr(10)}" if conversacion else ""}
Pregunta del alumno:
{pregunta}

Cómo respondes:
- Explica apoyándote en cómo lo explicó su profesor, citando la sesión cuando ayude
  ("en la clase del 14 de marzo tu profesor lo planteó así...").
- Si la duda es sobre algo que todavía no se ve en su grupo, dilo con claridad y señala
  en qué sesión quedaron; no te adelantes al temario de su sección.
- Si el tema simplemente no aparece en las clases, admítelo y sugiere preguntarle al profesor.
- Tono cercano y directo, sin tratarlo como niño. Máximo cuatro párrafos.
- No uses JSON: responde en texto con formato Markdown ligero."""


def generar_guia(materia: str, grupo: str, historial: str, enfoque: str) -> str:
    """Guía de estudio construida sobre las clases reales del grupo."""
    return f"""Arma una guía de estudio para el grupo {grupo} de "{materia}".

Material de origen — las clases que este grupo realmente recibió:
---
{historial}
---

Enfoque pedido por el profesor: {enfoque or "repaso general de lo visto hasta ahora"}

Estructura la guía en Markdown:
- Un párrafo inicial que sitúe qué abarca y hasta dónde llegó el grupo.
- Secciones por tema, con las ideas clave tal como se explicaron en clase.
- Al menos cinco ejercicios o preguntas de autoevaluación coherentes con el nivel visto.
- Una sección final "Si te perdiste" con los puntos donde el grupo mostró más dudas.

No incluyas temas que este grupo no haya visto todavía. Es material de repaso, no de adelanto."""


def simulacion(clave: str) -> Any:
    """Respuestas de relleno para `LIVY_FAKE_GEMMA=1`.

    Permiten construir y demostrar la interfaz sin gastar cuota de la API.
    """
    canned: dict[str, Any] = {
        "temario": {
            "temas": [
                {"orden": 1, "unidad": "Unidad 1", "titulo": "Tema de ejemplo", "subtemas": []}
            ]
        },
        "resumen": {
            "titulo": "Sesión simulada",
            "resumen": "Respuesta simulada: la clave de Gemma no está configurada.",
            "puntos_clave": ["Configura GEMINI_API_KEY para ver el resultado real"],
            "donde_quedo": "Sin datos reales",
            "temas": [],
            "pendientes": [],
            "dudas_detectadas": [],
        },
        "recomendaciones": {"recomendaciones": []},
        "texto": "Respuesta simulada: configura GEMINI_API_KEY para hablar con Gemma 4.",
    }
    return canned.get(clave, {})

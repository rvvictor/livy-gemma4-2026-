"""Único punto de contacto con Gemma 4.

Toda la inteligencia de Livy pasa por aquí: lectura del temario por visión,
resumen estructurado de la clase, mapeo de cobertura contra el plan de estudios,
recomendación del siguiente tema por sección, chat del alumno y guías de estudio.

Concentrar las llamadas en un solo módulo permite tres cosas que importan en un
sprint de un día:

1. Respetar el límite de 15 solicitudes por minuto del tier gratuito desde un
   único lugar, con ráfagas cortas para que la interfaz no se sienta lenta.
2. Degradar con elegancia: si el endpoint de Gemma rechaza `system_instruction`
   o la salida JSON nativa, se reintenta sin esa opción y se recuerda la
   decisión para no volver a pagar el error.
3. Trabajar el frontend sin quemar cuota mediante `LIVY_FAKE_GEMMA=1`.
"""

from __future__ import annotations

import asyncio
import base64
import json
import time
from collections import deque
from typing import Any

import httpx

from .config import (
    GEMINI_API_KEY,
    GEMMA_ENDPOINT,
    GEMMA_MODELO,
    LIMITE_POR_MINUTO,
    MODO_SIMULADO,
)


class ErrorGemma(RuntimeError):
    """Falla al obtener una respuesta utilizable del modelo."""


# El endpoint hospedado no documenta con claridad estas capacidades para los
# modelos Gemma. En vez de asumir, se prueban una vez y se recuerda el resultado.
_soporta_instruccion_sistema = True
_soporta_json_nativo = True
_soporta_nivel_pensamiento = True


class _Limitador:
    """Ventana deslizante de 60 segundos.

    Permite ráfagas cortas —importante para que la demo se sienta ágil— sin
    rebasar nunca el límite del tier gratuito.
    """

    def __init__(self, maximo: int) -> None:
        self._maximo = max(1, maximo)
        self._marcas: deque[float] = deque()
        self._candado = asyncio.Lock()

    async def esperar_turno(self) -> None:
        async with self._candado:
            while True:
                ahora = time.monotonic()
                while self._marcas and ahora - self._marcas[0] > 60:
                    self._marcas.popleft()
                if len(self._marcas) < self._maximo:
                    self._marcas.append(ahora)
                    return
                espera = 60 - (ahora - self._marcas[0]) + 0.05
                await asyncio.sleep(espera)


_limitador = _Limitador(LIMITE_POR_MINUTO)


def _bloques_balanceados(texto: str, apertura: str, cierre: str) -> list[str]:
    """Devuelve todos los fragmentos con llaves balanceadas del texto.

    Se ignoran las llaves que aparecen dentro de cadenas para no confundir un
    `"{"` literal con el inicio de un objeto.
    """
    bloques: list[str] = []
    pila: list[int] = []
    en_cadena = False
    escapado = False

    for i, caracter in enumerate(texto):
        if en_cadena:
            if escapado:
                escapado = False
            elif caracter == "\\":
                escapado = True
            elif caracter == '"':
                en_cadena = False
            continue
        if caracter == '"':
            en_cadena = True
        elif caracter == apertura:
            pila.append(i)
        elif caracter == cierre and pila:
            inicio = pila.pop()
            if not pila:  # se cerró un bloque de nivel superior
                bloques.append(texto[inicio : i + 1])

    return bloques


def extraer_json(texto: str) -> Any:
    """Parsea JSON tolerando lo que los modelos suelen agregar de más.

    Gemma 4 puede anteponer su razonamiento al resultado, y ese razonamiento
    suele traer fragmentos de JSON de ejemplo. Por eso no basta con tomar el
    primer objeto balanceado: se recogen todos los candidatos y se elige **el
    más grande que parsee**, que es siempre la respuesta y no el borrador.
    """
    limpio = texto.strip()
    if limpio.startswith("```"):
        limpio = limpio.split("\n", 1)[-1] if "\n" in limpio else limpio
        if limpio.rstrip().endswith("```"):
            limpio = limpio.rstrip()[:-3]
    limpio = limpio.strip()

    try:
        return json.loads(limpio)
    except json.JSONDecodeError:
        pass

    candidatos: list[str] = []
    for apertura, cierre in (("{", "}"), ("[", "]")):
        candidatos.extend(_bloques_balanceados(limpio, apertura, cierre))

    for bloque in sorted(candidatos, key=len, reverse=True):
        try:
            return json.loads(bloque)
        except json.JSONDecodeError:
            continue

    raise ErrorGemma(f"El modelo no devolvió JSON utilizable: {texto[:400]}")


def _armar_partes(instruccion: str, imagenes: list[tuple[str, bytes]] | None) -> list[dict]:
    partes: list[dict] = [{"text": instruccion}]
    for tipo_mime, contenido in imagenes or []:
        partes.append(
            {
                "inline_data": {
                    "mime_type": tipo_mime,
                    "data": base64.b64encode(contenido).decode("ascii"),
                }
            }
        )
    return partes


def _texto_de_respuesta(datos: dict) -> str:
    candidatos = datos.get("candidates") or []
    if not candidatos:
        motivo = (datos.get("promptFeedback") or {}).get("blockReason", "sin candidatos")
        raise ErrorGemma(f"Gemma no devolvió respuesta ({motivo}).")

    candidato = candidatos[0]
    partes = (candidato.get("content") or {}).get("parts") or []
    texto = "".join(parte.get("text", "") for parte in partes).strip()
    if not texto:
        raise ErrorGemma(
            f"Respuesta vacía de Gemma (finishReason={candidato.get('finishReason')})."
        )
    return texto


async def generar(
    instruccion: str,
    *,
    sistema: str | None = None,
    imagenes: list[tuple[str, bytes]] | None = None,
    json_esperado: bool = False,
    simulado: Any = None,
    temperatura: float = 0.2,
    max_tokens: int = 4096,
    pensar: bool = False,
) -> Any:
    """Llama a Gemma 4 y devuelve texto, o el JSON ya parseado si se pide.

    `imagenes` es una lista de pares (tipo MIME, bytes) para el temario fotografiado.
    `simulado` es la respuesta que se devuelve cuando el modo simulado está activo.
    `pensar` deja que el modelo razone en voz alta antes de responder; por defecto
    se apaga, porque ese razonamiento se devuelve al cliente y se come el
    presupuesto de tokens sin aportar nada al producto.
    """
    global _soporta_instruccion_sistema, _soporta_json_nativo, _soporta_nivel_pensamiento

    if MODO_SIMULADO:
        if simulado is None:
            return {} if json_esperado else ""
        return simulado

    url = f"{GEMMA_ENDPOINT}/{GEMMA_MODELO}:generateContent"
    intentos_red = 0

    while True:
        cuerpo: dict[str, Any] = {
            "contents": [{"role": "user", "parts": _armar_partes(instruccion, imagenes)}],
            "generationConfig": {
                "temperature": temperatura,
                "maxOutputTokens": max_tokens,
            },
        }
        if sistema and _soporta_instruccion_sistema:
            cuerpo["system_instruction"] = {"parts": [{"text": sistema}]}
        elif sistema:
            # El endpoint rechazó la instrucción de sistema: va como preámbulo.
            cuerpo["contents"][0]["parts"][0]["text"] = f"{sistema}\n\n---\n\n{instruccion}"
        if json_esperado and _soporta_json_nativo:
            cuerpo["generationConfig"]["responseMimeType"] = "application/json"
        if not pensar and _soporta_nivel_pensamiento:
            cuerpo["generationConfig"]["thinkingConfig"] = {"thinkingLevel": "MINIMAL"}

        await _limitador.esperar_turno()

        try:
            async with httpx.AsyncClient(timeout=120) as cliente:
                respuesta = await cliente.post(url, params={"key": GEMINI_API_KEY}, json=cuerpo)
        except httpx.RequestError as error:
            intentos_red += 1
            if intentos_red >= 3:
                raise ErrorGemma(f"No se pudo contactar a Gemma: {error}") from error
            await asyncio.sleep(2 * intentos_red)
            continue

        if respuesta.status_code == 200:
            texto = _texto_de_respuesta(respuesta.json())
            return extraer_json(texto) if json_esperado else texto

        detalle = respuesta.text[:500]

        # Degradaciones: se apaga la opción conflictiva y se reintenta una vez.
        if respuesta.status_code == 400 and not pensar and _soporta_nivel_pensamiento:
            _soporta_nivel_pensamiento = False
            continue
        if respuesta.status_code == 400 and sistema and _soporta_instruccion_sistema:
            _soporta_instruccion_sistema = False
            continue
        if respuesta.status_code == 400 and json_esperado and _soporta_json_nativo:
            _soporta_json_nativo = False
            continue

        if respuesta.status_code in {429, 500, 502, 503, 504}:
            intentos_red += 1
            if intentos_red >= 4:
                raise ErrorGemma(f"Gemma respondió {respuesta.status_code}: {detalle}")
            await asyncio.sleep(min(2**intentos_red, 20))
            continue

        raise ErrorGemma(f"Gemma respondió {respuesta.status_code}: {detalle}")

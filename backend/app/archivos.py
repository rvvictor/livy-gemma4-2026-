"""Lectura de los documentos que sube el profesor.

Tanto el temario como el horario llegan igual: una foto tomada con el celular o
un PDF institucional. La diferencia importa para Gemma 4:

- Del PDF se extrae el texto y se manda como texto. Es más barato en tokens y más
  fiel que renderizar la página como imagen.
- La foto se manda tal cual y la resuelve la visión del modelo, que aguanta
  fotografías en ángulo y anotaciones a mano.
"""

from __future__ import annotations

import io

from fastapi import HTTPException, UploadFile

TIPOS_IMAGEN = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/heic"}
EXTENSIONES_IMAGEN = (".png", ".jpg", ".jpeg", ".webp", ".heic")


async def leer_documento(
    archivo: UploadFile,
) -> tuple[list[tuple[str, bytes]] | None, str | None]:
    """Devuelve (imágenes, texto) según el formato; solo uno de los dos trae valor."""
    contenido = await archivo.read()
    if not contenido:
        raise HTTPException(400, "El archivo llegó vacío")

    tipo = (archivo.content_type or "").lower()
    nombre = (archivo.filename or "").lower()

    if tipo == "application/pdf" or nombre.endswith(".pdf"):
        try:
            from pypdf import PdfReader

            lector = PdfReader(io.BytesIO(contenido))
            texto = "\n".join((pagina.extract_text() or "") for pagina in lector.pages)
        except Exception as error:  # noqa: BLE001 - el mensaje va al usuario
            raise HTTPException(400, f"No se pudo leer el PDF: {error}") from error

        if not texto.strip():
            raise HTTPException(
                400,
                "El PDF no tiene texto extraíble (parece un escaneo). "
                "Sube una foto y Gemma lo lee con visión.",
            )
        return None, texto

    if tipo in TIPOS_IMAGEN or nombre.endswith(EXTENSIONES_IMAGEN):
        return [(tipo or "image/jpeg", contenido)], None

    raise HTTPException(400, f"Formato no soportado: {tipo or archivo.filename}")

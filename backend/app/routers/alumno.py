"""Portal del alumno: consulta de sus clases y chat anclado a ellas.

Dos decisiones deliberadas de privacidad y de producto:

- El alumno nunca ve la transcripción cruda, solo los resúmenes. La transcripción
  se usa del lado del servidor para fundamentar las respuestas, pero no se expone.
- El chat responde con lo que su profesor enseñó **a su grupo**, no con internet
  genérico. Si el tema aún no se ve en su sección, lo dice en vez de adelantarse.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from .. import gemma, prompts
from ..avance import historial_de_clases
from ..db import obtener_sesion
from ..models import Grupo, Materia, MensajeChat, Sesion

router = APIRouter(prefix="/api", tags=["alumno"])

MENSAJES_DE_CONTEXTO = 6


class PreguntaEntrada(BaseModel):
    pregunta: str


class GuiaEntrada(BaseModel):
    enfoque: str = ""


def _materia_y_grupo(db: Session, grupo_id: int) -> tuple[Materia, Grupo]:
    grupo = db.get(Grupo, grupo_id)
    if not grupo:
        raise HTTPException(404, "Grupo no encontrado")
    materia = db.get(Materia, grupo.materia_id)
    if not materia:
        raise HTTPException(404, "Materia no encontrada")
    return materia, grupo


@router.get("/grupos/{grupo_id}/clases")
def clases_del_grupo(grupo_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Vista de solo lectura: qué se vio en cada sesión de este grupo."""
    materia, grupo = _materia_y_grupo(db, grupo_id)
    sesiones = db.exec(
        select(Sesion)
        .where(Sesion.grupo_id == grupo_id, Sesion.estado == "cerrada")
        .order_by(Sesion.fecha.desc())
    ).all()

    return {
        "materia": materia.nombre,
        "profesor": materia.profesor,
        "grupo": grupo.nombre,
        "clases": [
            {
                "id": s.id,
                "fecha": s.fecha.isoformat(),
                "titulo": s.titulo,
                "resumen": s.resumen.get("resumen", ""),
                "puntos_clave": s.resumen.get("puntos_clave", []),
                "donde_quedo": s.resumen.get("donde_quedo", ""),
                "pendientes": s.resumen.get("pendientes", []),
            }
            for s in sesiones
        ],
    }


@router.get("/grupos/{grupo_id}/chat")
def historial_chat(grupo_id: int, db: Session = Depends(obtener_sesion)) -> list[dict]:
    mensajes = db.exec(
        select(MensajeChat).where(MensajeChat.grupo_id == grupo_id).order_by(MensajeChat.id)
    ).all()
    return [{"rol": m.rol, "contenido": m.contenido} for m in mensajes]


@router.post("/grupos/{grupo_id}/chat")
async def preguntar(
    grupo_id: int,
    entrada: PreguntaEntrada,
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Responde la duda del alumno usando solo las clases de su grupo.

    El historial completo del grupo entra íntegro en el contexto de 256K de
    Gemma 4: sin embeddings, sin base vectorial y sin fallos de recuperación.
    """
    materia, grupo = _materia_y_grupo(db, grupo_id)
    pregunta = entrada.pregunta.strip()
    if not pregunta:
        raise HTTPException(400, "La pregunta llegó vacía")

    historial = historial_de_clases(db, grupo_id, incluir_transcripcion=True)

    previos = db.exec(
        select(MensajeChat)
        .where(MensajeChat.grupo_id == grupo_id)
        .order_by(MensajeChat.id.desc())
        .limit(MENSAJES_DE_CONTEXTO)
    ).all()
    conversacion = "\n".join(
        f"{'Alumno' if m.rol == 'alumno' else 'Livy'}: {m.contenido}" for m in reversed(previos)
    )

    try:
        respuesta = await gemma.generar(
            prompts.responder_alumno(
                materia.nombre, grupo.nombre, historial, pregunta, conversacion
            ),
            sistema=prompts.SISTEMA,
            simulado=prompts.simulacion("texto"),
            temperatura=0.4,
            max_tokens=2048,
        )
    except gemma.ErrorGemma as error:
        raise HTTPException(502, str(error)) from error

    db.add(MensajeChat(grupo_id=grupo_id, rol="alumno", contenido=pregunta))
    db.add(MensajeChat(grupo_id=grupo_id, rol="asistente", contenido=respuesta))
    db.commit()

    return {"respuesta": respuesta}


@router.post("/grupos/{grupo_id}/guia")
async def guia_de_estudio(
    grupo_id: int,
    entrada: GuiaEntrada,
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Guía de repaso construida sobre las clases que este grupo sí recibió."""
    materia, grupo = _materia_y_grupo(db, grupo_id)
    historial = historial_de_clases(db, grupo_id, incluir_transcripcion=True)

    try:
        guia = await gemma.generar(
            prompts.generar_guia(materia.nombre, grupo.nombre, historial, entrada.enfoque),
            sistema=prompts.SISTEMA,
            simulado=prompts.simulacion("texto"),
            temperatura=0.5,
            max_tokens=4096,
        )
    except gemma.ErrorGemma as error:
        raise HTTPException(502, str(error)) from error

    return {"guia": guia}

"""Alta de la materia y lectura del plan de estudios con la visión de Gemma 4.

El profesor sube una foto o un PDF de su temario; Gemma lo convierte en una lista
ordenada de temas. Nunca se guarda directo: el resultado vuelve al profesor para
que lo revise y lo corrija. Él es el autor del plan, el modelo solo transcribe.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from .. import gemma, prompts
from ..archivos import leer_documento
from ..avance import temas_de_materia
from ..db import obtener_sesion
from ..models import Grupo, Materia, Tema

router = APIRouter(prefix="/api", tags=["temario"])


class TemaEntrada(BaseModel):
    orden: int
    unidad: str = ""
    titulo: str
    subtemas: list[str] = []


class TemarioEntrada(BaseModel):
    temas: list[TemaEntrada]


def _serializar_tema(tema: Tema) -> dict:
    return {
        "id": tema.id,
        "orden": tema.orden,
        "unidad": tema.unidad,
        "titulo": tema.titulo,
        "subtemas": tema.subtemas,
    }


@router.get("/materias")
def listar_materias(db: Session = Depends(obtener_sesion)) -> list[dict]:
    materias = db.exec(select(Materia)).all()
    salida = []
    for materia in materias:
        grupos = db.exec(select(Grupo).where(Grupo.materia_id == materia.id)).all()
        salida.append(
            {
                "id": materia.id,
                "nombre": materia.nombre,
                "profesor": materia.profesor,
                "ciclo": materia.ciclo,
                "sesiones_planeadas": materia.sesiones_planeadas,
                "grupos": [
                    {"id": g.id, "nombre": g.nombre, "horario": g.horario, "alumnos": g.alumnos}
                    for g in grupos
                ],
            }
        )
    return salida


@router.get("/materias/{materia_id}")
def obtener_materia(materia_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    materia = db.get(Materia, materia_id)
    if not materia:
        raise HTTPException(404, "Materia no encontrada")
    grupos = db.exec(select(Grupo).where(Grupo.materia_id == materia_id)).all()
    return {
        "id": materia.id,
        "nombre": materia.nombre,
        "profesor": materia.profesor,
        "ciclo": materia.ciclo,
        "sesiones_planeadas": materia.sesiones_planeadas,
        "temas": [_serializar_tema(t) for t in temas_de_materia(db, materia_id)],
        "grupos": [
            {"id": g.id, "nombre": g.nombre, "horario": g.horario, "alumnos": g.alumnos}
            for g in grupos
        ],
    }


@router.post("/materias/{materia_id}/temario/analizar")
async def analizar_temario(
    materia_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Lee el temario de una imagen o un PDF y propone la estructura.

    No escribe nada en la base: la propuesta va a la pantalla de revisión.
    """
    materia = db.get(Materia, materia_id)
    if not materia:
        raise HTTPException(404, "Materia no encontrada")

    imagenes, texto_fuente = await leer_documento(archivo)

    try:
        resultado = await gemma.generar(
            prompts.leer_temario(materia.nombre, texto_fuente),
            sistema=prompts.SISTEMA,
            imagenes=imagenes,
            json_esperado=True,
            simulado=prompts.simulacion("temario"),
            temperatura=0.1,
        )
    except gemma.ErrorGemma as error:
        raise HTTPException(502, str(error)) from error

    temas = resultado.get("temas", []) if isinstance(resultado, dict) else []
    if not temas:
        raise HTTPException(422, "Gemma no encontró temas legibles en el documento")

    for indice, tema in enumerate(temas, start=1):
        tema.setdefault("orden", indice)
        tema.setdefault("unidad", "")
        tema.setdefault("subtemas", [])

    return {"temas": temas, "fuente": "pdf" if texto_fuente else "imagen"}


@router.put("/materias/{materia_id}/temario")
def guardar_temario(
    materia_id: int,
    entrada: TemarioEntrada,
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Reemplaza el plan de estudios con la versión que el profesor ya validó."""
    materia = db.get(Materia, materia_id)
    if not materia:
        raise HTTPException(404, "Materia no encontrada")
    if not entrada.temas:
        raise HTTPException(400, "El temario no puede quedar vacío")

    for tema in db.exec(select(Tema).where(Tema.materia_id == materia_id)).all():
        db.delete(tema)
    db.commit()

    for tema in sorted(entrada.temas, key=lambda t: t.orden):
        db.add(
            Tema(
                materia_id=materia_id,
                orden=tema.orden,
                unidad=tema.unidad,
                titulo=tema.titulo,
                subtemas_json=json.dumps(tema.subtemas, ensure_ascii=False),
            )
        )
    db.commit()

    return {"temas": [_serializar_tema(t) for t in temas_de_materia(db, materia_id)]}

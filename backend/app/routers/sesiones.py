"""Ciclo de vida de una clase: iniciar, transcribir y cerrar.

Al cerrar es donde ocurre lo importante. Gemma 4 recibe la transcripción cruda
junto con el plan de estudios y el punto en el que venía **ese grupo**, y devuelve
en una sola llamada la memoria estructurada de la sesión más el mapeo de qué temas
se tocaron y con qué profundidad. Ese mapeo es lo que hace avanzar la bitácora de
la sección sin tocar a las demás.
"""

from __future__ import annotations

import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from .. import gemma, prompts
from ..avance import contexto_previo, estado_de_grupo, temas_de_materia
from ..db import obtener_sesion
from ..models import Cobertura, Grupo, Materia, Sesion

router = APIRouter(prefix="/api", tags=["sesiones"])

NIVELES_VALIDOS = {"introducido", "cubierto", "reforzado"}


class FragmentoEntrada(BaseModel):
    texto: str


class CierreEntrada(BaseModel):
    duracion_min: int = 0


def _serializar_sesion(sesion: Sesion) -> dict:
    return {
        "id": sesion.id,
        "grupo_id": sesion.grupo_id,
        "fecha": sesion.fecha.isoformat(),
        "estado": sesion.estado,
        "titulo": sesion.titulo,
        "duracion_min": sesion.duracion_min,
        "transcripcion": sesion.transcripcion,
        "resumen": sesion.resumen,
    }


@router.post("/grupos/{grupo_id}/sesiones/iniciar")
def iniciar_sesion(grupo_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Abre una clase. Si ya había una en curso para este grupo, la retoma."""
    grupo = db.get(Grupo, grupo_id)
    if not grupo:
        raise HTTPException(404, "Grupo no encontrado")

    en_curso = db.exec(
        select(Sesion).where(Sesion.grupo_id == grupo_id, Sesion.estado == "en_curso")
    ).first()
    if en_curso:
        return _serializar_sesion(en_curso)

    sesion = Sesion(grupo_id=grupo_id, fecha=date.today(), estado="en_curso")
    db.add(sesion)
    db.commit()
    db.refresh(sesion)
    return _serializar_sesion(sesion)


@router.post("/sesiones/{sesion_id}/transcripcion")
def agregar_fragmento(
    sesion_id: int,
    fragmento: FragmentoEntrada,
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Recibe los lotes de texto que el navegador va dictando durante la clase."""
    sesion = db.get(Sesion, sesion_id)
    if not sesion:
        raise HTTPException(404, "Sesión no encontrada")
    if sesion.estado == "cerrada":
        raise HTTPException(409, "La sesión ya fue cerrada")

    texto = fragmento.texto.strip()
    if texto:
        separador = " " if sesion.transcripcion else ""
        sesion.transcripcion = f"{sesion.transcripcion}{separador}{texto}"
        db.add(sesion)
        db.commit()

    return {"id": sesion.id, "caracteres": len(sesion.transcripcion)}


@router.get("/sesiones/{sesion_id}")
def obtener_sesion_detalle(sesion_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    sesion = db.get(Sesion, sesion_id)
    if not sesion:
        raise HTTPException(404, "Sesión no encontrada")
    return _serializar_sesion(sesion)


@router.get("/grupos/{grupo_id}/sesiones")
def listar_sesiones(grupo_id: int, db: Session = Depends(obtener_sesion)) -> list[dict]:
    sesiones = db.exec(
        select(Sesion).where(Sesion.grupo_id == grupo_id).order_by(Sesion.fecha.desc())
    ).all()
    return [_serializar_sesion(s) for s in sesiones]


@router.post("/sesiones/{sesion_id}/cerrar")
async def cerrar_sesion(
    sesion_id: int,
    entrada: CierreEntrada,
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Convierte la clase en memoria estructurada y hace avanzar al grupo."""
    sesion = db.get(Sesion, sesion_id)
    if not sesion:
        raise HTTPException(404, "Sesión no encontrada")
    if not sesion.transcripcion.strip():
        raise HTTPException(400, "No hay transcripción que resumir")

    grupo = db.get(Grupo, sesion.grupo_id)
    materia = db.get(Materia, grupo.materia_id)
    temas = temas_de_materia(db, materia.id)
    if not temas:
        raise HTTPException(409, "La materia todavía no tiene plan de estudios cargado")

    estado = estado_de_grupo(db, grupo, temas)

    try:
        resultado = await gemma.generar(
            prompts.resumir_sesion(
                materia=materia.nombre,
                grupo=grupo.nombre,
                temas=[
                    {"id": t.id, "orden": t.orden, "titulo": t.titulo, "subtemas": t.subtemas}
                    for t in temas
                ],
                transcripcion=sesion.transcripcion,
                contexto_previo=contexto_previo(estado),
            ),
            sistema=prompts.SISTEMA,
            json_esperado=True,
            simulado=prompts.simulacion("resumen"),
            temperatura=0.2,
            max_tokens=4096,
        )
    except gemma.ErrorGemma as error:
        raise HTTPException(502, str(error)) from error

    if not isinstance(resultado, dict):
        raise HTTPException(502, "Gemma devolvió una estructura inesperada")

    # La cobertura se reescribe por completo: cerrar dos veces no duplica avance.
    for previa in db.exec(select(Cobertura).where(Cobertura.sesion_id == sesion.id)).all():
        db.delete(previa)

    ids_validos = {t.id for t in temas}
    registrados = 0
    for marca in resultado.get("temas", []) or []:
        try:
            tema_id = int(marca.get("tema_id"))
        except (TypeError, ValueError):
            continue
        if tema_id not in ids_validos:
            continue  # el modelo inventó un identificador: se descarta
        nivel = str(marca.get("nivel", "cubierto")).strip().lower()
        if nivel not in NIVELES_VALIDOS:
            nivel = "cubierto"
        db.add(
            Cobertura(
                sesion_id=sesion.id,
                grupo_id=grupo.id,
                tema_id=tema_id,
                nivel=nivel,
                evidencia=str(marca.get("evidencia", ""))[:500],
            )
        )
        registrados += 1

    sesion.estado = "cerrada"
    sesion.titulo = str(resultado.get("titulo", ""))[:120]
    sesion.resumen_json = json.dumps(resultado, ensure_ascii=False)
    sesion.duracion_min = entrada.duracion_min or sesion.duracion_min
    db.add(sesion)
    db.commit()
    db.refresh(sesion)

    return {
        "sesion": _serializar_sesion(sesion),
        "temas_registrados": registrados,
        "estado_grupo": estado_de_grupo(db, grupo, temas),
    }

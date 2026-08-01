"""Tablero de continuidad: dónde va cada sección y qué sigue para cada una.

Las recomendaciones de todos los grupos se piden a Gemma en **una sola llamada**.
No es solo economía de cuota: darle al modelo el panorama completo le permite
razonar comparativamente sobre el ciclo y las sesiones que quedan.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from .. import gemma, prompts
from ..avance import estado_de_grupo, temas_de_materia
from ..db import obtener_sesion
from ..models import Grupo, Materia, Sesion

router = APIRouter(prefix="/api", tags=["bitacora"])

RIESGOS_VALIDOS = {"al_dia", "atencion", "rezagado"}


@router.get("/materias/{materia_id}/bitacora")
def bitacora(materia_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Avance de cada grupo contra el plan, calculado por sección."""
    materia = db.get(Materia, materia_id)
    if not materia:
        raise HTTPException(404, "Materia no encontrada")

    temas = temas_de_materia(db, materia_id)
    grupos = db.exec(select(Grupo).where(Grupo.materia_id == materia_id)).all()
    estados = [estado_de_grupo(db, grupo, temas) for grupo in grupos]

    return {
        "materia": {
            "id": materia.id,
            "nombre": materia.nombre,
            "profesor": materia.profesor,
            "ciclo": materia.ciclo,
            "sesiones_planeadas": materia.sesiones_planeadas,
        },
        "temas": [
            {"id": t.id, "orden": t.orden, "unidad": t.unidad, "titulo": t.titulo} for t in temas
        ],
        "grupos": estados,
        "brecha": _brecha(estados),
    }


def _brecha(estados: list[dict]) -> dict:
    """Distancia entre la sección más adelantada y la más atrasada."""
    if len(estados) < 2:
        return {"temas": 0, "adelantado": None, "rezagado": None}
    ordenados = sorted(estados, key=lambda e: e["temas_cubiertos"])
    return {
        "temas": ordenados[-1]["temas_cubiertos"] - ordenados[0]["temas_cubiertos"],
        "adelantado": ordenados[-1]["grupo"],
        "rezagado": ordenados[0]["grupo"],
    }


@router.get("/materias/{materia_id}/recomendaciones")
async def recomendaciones(materia_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Siguiente tema sugerido para cada sección, razonado por Gemma 4."""
    materia = db.get(Materia, materia_id)
    if not materia:
        raise HTTPException(404, "Materia no encontrada")

    temas = temas_de_materia(db, materia_id)
    if not temas:
        raise HTTPException(409, "La materia todavía no tiene plan de estudios cargado")

    grupos = db.exec(select(Grupo).where(Grupo.materia_id == materia_id)).all()
    estados = [estado_de_grupo(db, grupo, temas) for grupo in grupos]

    sesiones_dadas = db.exec(
        select(Sesion).where(Sesion.grupo_id.in_([g.id for g in grupos]), Sesion.estado == "cerrada")
    ).all()
    promedio = len(sesiones_dadas) / max(len(grupos), 1)
    restantes = max(0, round(materia.sesiones_planeadas - promedio))

    resumen_para_modelo = [
        {
            "grupo_id": estado["grupo_id"],
            "grupo": estado["grupo"],
            "horario": estado["horario"],
            "sesiones_impartidas": estado["sesiones_impartidas"],
            "avance_porcentaje": round(estado["avance"] * 100),
            "ultimo_tema_cubierto": estado["tema_actual"],
            "siguiente_pendiente": estado["siguiente_pendiente"],
            "temas_solo_introducidos": [
                {"tema_id": f["tema_id"], "titulo": f["titulo"]}
                for f in estado["detalle"]
                if f["nivel"] == "introducido"
            ],
        }
        for estado in estados
    ]

    try:
        resultado = await gemma.generar(
            prompts.recomendar_siguiente(materia.nombre, resumen_para_modelo, restantes),
            sistema=prompts.SISTEMA,
            json_esperado=True,
            simulado=prompts.simulacion("recomendaciones"),
            temperatura=0.3,
        )
    except gemma.ErrorGemma as error:
        raise HTTPException(502, str(error)) from error

    crudas = resultado.get("recomendaciones", []) if isinstance(resultado, dict) else []
    titulos = {t.id: t.titulo for t in temas}
    ids_grupo = {g.id for g in grupos}

    limpias = []
    for cruda in crudas:
        try:
            grupo_id = int(cruda.get("grupo_id"))
        except (TypeError, ValueError):
            continue
        if grupo_id not in ids_grupo:
            continue
        try:
            tema_id = int(cruda.get("siguiente_tema_id"))
        except (TypeError, ValueError):
            tema_id = None
        riesgo = str(cruda.get("riesgo", "")).strip().lower()
        limpias.append(
            {
                "grupo_id": grupo_id,
                "siguiente_tema_id": tema_id if tema_id in titulos else None,
                "siguiente_tema": titulos.get(tema_id, ""),
                "justificacion": str(cruda.get("justificacion", "")),
                "riesgo": riesgo if riesgo in RIESGOS_VALIDOS else "atencion",
                "ajuste_sugerido": str(cruda.get("ajuste_sugerido", "")),
            }
        )

    return {"sesiones_restantes": restantes, "recomendaciones": limpias}

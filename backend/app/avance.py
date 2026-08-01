"""Cálculo del avance por sección.

Este módulo es la razón de ser de Livy: traduce los registros de `Cobertura` en
la respuesta a la pregunta que el profesor no puede contestar hoy —"¿dónde quedó
exactamente cada uno de mis grupos?"— y la contesta por separado para cada sección.
"""

from __future__ import annotations

from sqlmodel import Session, select

from .models import NIVELES, Cobertura, Grupo, Sesion, Tema

# Un tema "reforzado" implica que ya estaba cubierto.
_JERARQUIA = {"introducido": 1, "cubierto": 2, "reforzado": 3}


def _nivel_mas_alto(actual: str | None, nuevo: str) -> str:
    if actual is None:
        return nuevo
    return nuevo if _JERARQUIA.get(nuevo, 0) > _JERARQUIA.get(actual, 0) else actual


def temas_de_materia(db: Session, materia_id: int) -> list[Tema]:
    return list(
        db.exec(select(Tema).where(Tema.materia_id == materia_id).order_by(Tema.orden)).all()
    )


def estado_de_grupo(db: Session, grupo: Grupo, temas: list[Tema]) -> dict:
    """Fotografía completa de dónde va una sección contra su plan de estudios."""
    coberturas = db.exec(select(Cobertura).where(Cobertura.grupo_id == grupo.id)).all()

    niveles: dict[int, str] = {}
    evidencias: dict[int, str] = {}
    for cobertura in coberturas:
        niveles[cobertura.tema_id] = _nivel_mas_alto(
            niveles.get(cobertura.tema_id), cobertura.nivel
        )
        if cobertura.evidencia and cobertura.tema_id not in evidencias:
            evidencias[cobertura.tema_id] = cobertura.evidencia

    sesiones = db.exec(
        select(Sesion)
        .where(Sesion.grupo_id == grupo.id, Sesion.estado == "cerrada")
        .order_by(Sesion.fecha)
    ).all()

    detalle = []
    for tema in temas:
        nivel = niveles.get(tema.id)
        detalle.append(
            {
                "tema_id": tema.id,
                "orden": tema.orden,
                "unidad": tema.unidad,
                "titulo": tema.titulo,
                "nivel": nivel,
                "peso": NIVELES.get(nivel, 0.0) if nivel else 0.0,
                "evidencia": evidencias.get(tema.id, ""),
            }
        )

    total = len(temas) or 1
    avance = sum(fila["peso"] for fila in detalle) / total

    cubiertos = [f for f in detalle if f["nivel"] in {"cubierto", "reforzado"}]
    tema_actual = cubiertos[-1] if cubiertos else None
    pendientes = [f for f in detalle if f["nivel"] is None or f["nivel"] == "introducido"]
    siguiente = pendientes[0] if pendientes else None

    return {
        "grupo_id": grupo.id,
        "grupo": grupo.nombre,
        "horario": grupo.horario,
        "alumnos": grupo.alumnos,
        "avance": round(avance, 3),
        "temas_totales": len(temas),
        "temas_cubiertos": len(cubiertos),
        "temas_introducidos": len([f for f in detalle if f["nivel"] == "introducido"]),
        "sesiones_impartidas": len(sesiones),
        "ultima_sesion": sesiones[-1].fecha.isoformat() if sesiones else None,
        "tema_actual": tema_actual,
        "siguiente_pendiente": siguiente,
        "detalle": detalle,
    }


def contexto_previo(estado: dict) -> str:
    """Resumen en prosa del punto de partida del grupo, para alimentar a Gemma."""
    if not estado["tema_actual"]:
        return "Es la primera sesión registrada del grupo."
    partes = [
        f"El grupo lleva {estado['sesiones_impartidas']} sesiones registradas y "
        f"un avance del {round(estado['avance'] * 100)}% del plan.",
        f"El último tema cubierto fue [{estado['tema_actual']['tema_id']}] "
        f"{estado['tema_actual']['titulo']}.",
    ]
    if estado["siguiente_pendiente"]:
        siguiente = estado["siguiente_pendiente"]
        nota = " (quedó solo introducido)" if siguiente["nivel"] == "introducido" else ""
        partes.append(
            f"El siguiente tema pendiente es [{siguiente['tema_id']}] {siguiente['titulo']}{nota}."
        )
    return " ".join(partes)


def historial_de_clases(db: Session, grupo_id: int, incluir_transcripcion: bool = True) -> str:
    """Todas las clases del grupo concatenadas para el contexto de Gemma 4.

    No usamos vectores ni RAG: el historial completo de una sección en un semestre
    cabe holgadamente en los 256K tokens de contexto de Gemma 4, así que inyectamos
    el corpus íntegro. Elimina el fallo de recuperación y una dependencia entera.
    """
    sesiones = db.exec(
        select(Sesion)
        .where(Sesion.grupo_id == grupo_id, Sesion.estado == "cerrada")
        .order_by(Sesion.fecha)
    ).all()

    bloques = []
    for sesion in sesiones:
        resumen = sesion.resumen
        bloque = [f"### Sesión del {sesion.fecha.isoformat()} — {sesion.titulo or 'sin título'}"]
        if resumen.get("resumen"):
            bloque.append(resumen["resumen"])
        if resumen.get("puntos_clave"):
            bloque.append("Puntos clave: " + "; ".join(resumen["puntos_clave"]))
        if resumen.get("donde_quedo"):
            bloque.append(f"Terminó en: {resumen['donde_quedo']}")
        if incluir_transcripcion and sesion.transcripcion:
            bloque.append(f"Transcripción:\n{sesion.transcripcion}")
        bloques.append("\n".join(bloque))

    return "\n\n".join(bloques) or "Este grupo todavía no tiene clases registradas."

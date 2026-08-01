"""Todo lo que quita datos, en un solo archivo.

Livy carga información por visión —un horario, un temario— y la va acumulando
clase tras clase. Sin una salida, el primer error de lectura de Gemma se queda
para siempre. Estos endpoints son esa salida.

Están juntos a propósito: el borrado es la superficie de mayor riesgo de la API y
conviene poder leerla entera de una sentada. Cada uno delega la cascada en
`borrado.py` y confirma la transacción una sola vez, al final.

Todas las respuestas devuelven el conteo de lo que se eliminó, para que la
interfaz pueda decir exactamente qué se fue en lugar de un "listo" a ciegas.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from .. import borrado
from ..db import obtener_sesion
from ..models import Cobertura, Grupo, Materia, MensajeChat, Sesion
from ..seed import MARCA_SIEMBRA, sembrar_si_esta_vacia

router = APIRouter(prefix="/api", tags=["mantenimiento"])


class ReinicioEntrada(BaseModel):
    # Por omisión se repuebla con la demostración: es lo que quiere quien está
    # enseñando el producto. Vaciar de verdad hay que pedirlo explícitamente.
    con_demo: bool = True


def _sesion_o_404(db: Session, sesion_id: int) -> Sesion:
    sesion = db.get(Sesion, sesion_id)
    if not sesion:
        raise HTTPException(404, "Sesión no encontrada")
    return sesion


def _grupo_o_404(db: Session, grupo_id: int) -> Grupo:
    grupo = db.get(Grupo, grupo_id)
    if not grupo:
        raise HTTPException(404, "Grupo no encontrado")
    return grupo


# ── Materias y planes de estudio ──


@router.delete("/materias/{materia_id}")
def eliminar_materia(materia_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """La materia completa: su plan, sus secciones y la bitácora de cada una."""
    materia = db.get(Materia, materia_id)
    if not materia:
        raise HTTPException(404, "Materia no encontrada")

    nombre = materia.nombre
    conteo = borrado.borrar_materia(db, materia)
    db.commit()
    return {"borrado": conteo, "detalle": f"Se eliminó {nombre} con todo su historial"}


@router.delete("/materias/{materia_id}/temario")
def eliminar_temario(materia_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Solo el plan de estudios. Las secciones y sus clases se conservan.

    El avance de los grupos vuelve a cero porque ya no hay temas contra los
    cuales medirlo; en cuanto se cargue un temario nuevo habrá que volver a
    cerrar las clases para reconstruirlo.
    """
    materia = db.get(Materia, materia_id)
    if not materia:
        raise HTTPException(404, "Materia no encontrada")

    conteo = borrado.borrar_temario(db, materia_id)
    db.commit()
    return {
        "borrado": conteo,
        "detalle": f"El plan de {materia.nombre} quedó vacío; sus clases siguen ahí",
    }


# ── Grupos y horario ──


@router.delete("/grupos/{grupo_id}")
def eliminar_grupo(grupo_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Una sección con su bitácora completa."""
    grupo = _grupo_o_404(db, grupo_id)
    nombre = grupo.nombre
    conteo = borrado.borrar_grupo(db, grupo)
    db.commit()
    return {"borrado": conteo, "detalle": f"Se eliminó el grupo {nombre}"}


@router.delete("/grupos/{grupo_id}/sesiones")
def eliminar_clases_del_grupo(grupo_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Borra las clases grabadas del grupo dejando la sección en pie.

    Es el reinicio que se usa cuando se estuvo probando el dictado: el grupo
    conserva su horario y su plan, pero su avance vuelve a cero.
    """
    grupo = _grupo_o_404(db, grupo_id)
    conteo = borrado.borrar_sesiones_de_grupo(db, grupo_id)
    db.commit()
    return {
        "borrado": conteo,
        "detalle": f"{grupo.nombre} volvió a cero: {conteo['sesiones']} clases eliminadas",
    }


@router.delete("/grupos/{grupo_id}/chat")
def eliminar_chat_del_grupo(
    grupo_id: int,
    alcance: str = "todo",
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Las dudas que los alumnos le preguntaron a Livy.

    Con `alcance=general` se conservan las preguntas hechas dentro de una clase
    concreta y solo se limpia la conversación sobre el curso completo.
    """
    grupo = _grupo_o_404(db, grupo_id)
    conteo = borrado.borrar_chat_de_grupo(db, grupo_id, solo_general=alcance == "general")
    db.commit()
    return {"borrado": conteo, "detalle": f"Se limpiaron las dudas de {grupo.nombre}"}


@router.delete("/profesor/horario")
def eliminar_horario(db: Session = Depends(obtener_sesion)) -> dict:
    """Vacía el horario: se van todos los grupos, quedan materias y temarios.

    Sirve para volver a cargar el horario desde cero cuando Gemma leyó mal la
    foto y quedaron secciones que no existen.
    """
    conteo = borrado.borrar_todos_los_grupos(db)
    db.commit()
    return {
        "borrado": conteo,
        "detalle": f"Se eliminaron {conteo['grupos']} grupos; los planes de estudio siguen ahí",
    }


# ── Clases ──


@router.delete("/sesiones/{sesion_id}")
def eliminar_clase(sesion_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Una clase concreta, con su cobertura y las dudas de esa sesión."""
    sesion = _sesion_o_404(db, sesion_id)
    titulo = sesion.titulo or f"clase del {sesion.fecha.isoformat()}"
    conteo = borrado.borrar_sesion(db, sesion)
    db.commit()
    return {"borrado": conteo, "detalle": f"Se eliminó «{titulo}»"}


@router.delete("/sesiones/{sesion_id}/transcripcion")
def eliminar_transcripcion(sesion_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Borra lo que se dijo en clase conservando la memoria ya generada.

    Es la palanca de privacidad: el resumen y el avance se quedan, el texto
    literal de lo que se habló en el salón desaparece.
    """
    sesion = _sesion_o_404(db, sesion_id)
    caracteres = len(sesion.transcripcion)
    sesion.transcripcion = ""
    db.add(sesion)
    db.commit()
    return {
        "borrado": {"caracteres": caracteres},
        "detalle": f"Se eliminaron {caracteres} caracteres de transcripción",
    }


@router.delete("/sesiones/{sesion_id}/chat")
def eliminar_chat_de_clase(sesion_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Las dudas preguntadas dentro de una clase."""
    _sesion_o_404(db, sesion_id)
    mensajes = db.exec(select(MensajeChat).where(MensajeChat.sesion_id == sesion_id)).all()
    for mensaje in mensajes:
        db.delete(mensaje)
    db.commit()
    return {
        "borrado": {"mensajes": len(mensajes)},
        "detalle": f"Se eliminaron {len(mensajes)} mensajes de esta clase",
    }


@router.post("/sesiones/{sesion_id}/reabrir")
def reabrir_clase(sesion_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Deshace el cierre: tira la memoria y el avance, conserva la transcripción.

    Es lo que se hace cuando Gemma resumió mal o mapeó temas que no se tocaron.
    La sesión vuelve a quedar abierta y se puede cerrar otra vez para que el
    modelo lo intente de nuevo sobre el mismo texto.
    """
    sesion = _sesion_o_404(db, sesion_id)

    coberturas = db.exec(select(Cobertura).where(Cobertura.sesion_id == sesion_id)).all()
    for cobertura in coberturas:
        db.delete(cobertura)

    sesion.estado = "en_curso"
    sesion.titulo = ""
    sesion.resumen_json = ""
    db.add(sesion)
    db.commit()

    return {
        "borrado": {"coberturas": len(coberturas)},
        "detalle": (
            "La clase quedó abierta otra vez. Ciérrala desde «Clase en vivo» para "
            "que Gemma vuelva a construir la memoria."
        ),
    }


# ── Reinicio completo ──


@router.post("/mantenimiento/reiniciar")
def reiniciar(
    entrada: ReinicioEntrada,
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Deja la base en blanco y, si se pide, vuelve a sembrar la demostración.

    Cuando se vacía **sin** demostración se deja una marca en la base: sin ella,
    el sembrado del siguiente arranque volvería a llenarla y el borrado parecería
    no haber servido de nada.
    """
    conteo = borrado.borrar_todo(db)

    if entrada.con_demo:
        borrado.desmarcar(db, MARCA_SIEMBRA)
        db.commit()
        sembrar_si_esta_vacia()
        return {"borrado": conteo, "detalle": "Se restauraron los datos de demostración"}

    borrado.marcar(db, MARCA_SIEMBRA, "omitida")
    db.commit()
    return {
        "borrado": conteo,
        "detalle": "La base quedó vacía. Carga tu horario para empezar de cero.",
    }

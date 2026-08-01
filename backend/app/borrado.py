"""Borrado en cascada.

El modelo de datos no declara `ON DELETE`: las relaciones se resuelven aquí, en
un único lugar, porque un borrado a medias es peor que no borrar. Una cobertura
huérfana —apuntando a una sesión que ya no existe— seguiría contando avance para
un grupo, y el avance por sección es justamente lo que el producto promete.

Ninguna función confirma la transacción: cada endpoint decide cuándo hacer
`commit`, de modo que un borrado compuesto (una materia con sus grupos y todas
sus sesiones) se aplique entero o no se aplique.
"""

from __future__ import annotations

from sqlmodel import Session, select

from .models import Ajuste, Cobertura, Grupo, Materia, MensajeChat, Sesion, Tema


def _sumar(*parciales: dict) -> dict:
    """Junta los conteos de varios borrados en un solo resumen."""
    total: dict[str, int] = {}
    for parcial in parciales:
        for clave, valor in parcial.items():
            total[clave] = total.get(clave, 0) + valor
    return total


def _borrar_todos(db: Session, filas) -> int:
    filas = list(filas)
    for fila in filas:
        db.delete(fila)
    return len(filas)


def borrar_sesion(db: Session, sesion: Sesion) -> dict:
    """Una clase con su cobertura y las dudas que se preguntaron sobre ella."""
    conteo = {
        "coberturas": _borrar_todos(
            db, db.exec(select(Cobertura).where(Cobertura.sesion_id == sesion.id)).all()
        ),
        "mensajes": _borrar_todos(
            db, db.exec(select(MensajeChat).where(MensajeChat.sesion_id == sesion.id)).all()
        ),
        "sesiones": 1,
    }
    db.delete(sesion)
    db.flush()
    return conteo


def borrar_sesiones_de_grupo(db: Session, grupo_id: int) -> dict:
    """Todas las clases grabadas de una sección: el grupo vuelve a cero avance."""
    sesiones = db.exec(select(Sesion).where(Sesion.grupo_id == grupo_id)).all()
    return _sumar(*[borrar_sesion(db, sesion) for sesion in sesiones]) or {
        "sesiones": 0,
        "coberturas": 0,
        "mensajes": 0,
    }


def borrar_chat_de_grupo(db: Session, grupo_id: int, solo_general: bool = False) -> dict:
    """El historial de preguntas de un grupo.

    Con `solo_general` se conservan las dudas atadas a una clase concreta y se
    limpia únicamente la conversación sobre el curso completo.
    """
    consulta = select(MensajeChat).where(MensajeChat.grupo_id == grupo_id)
    if solo_general:
        consulta = consulta.where(MensajeChat.sesion_id.is_(None))
    conteo = {"mensajes": _borrar_todos(db, db.exec(consulta).all())}
    db.flush()
    return conteo


def borrar_grupo(db: Session, grupo: Grupo) -> dict:
    """Una sección completa: su bitácora, sus clases y sus dudas."""
    conteo = _sumar(
        borrar_sesiones_de_grupo(db, grupo.id),
        borrar_chat_de_grupo(db, grupo.id),
        {
            "coberturas": _borrar_todos(
                db, db.exec(select(Cobertura).where(Cobertura.grupo_id == grupo.id)).all()
            ),
            "grupos": 1,
        },
    )
    db.delete(grupo)
    db.flush()
    return conteo


def borrar_temario(db: Session, materia_id: int) -> dict:
    """El plan de estudios de una materia.

    Se arrastra la cobertura porque sin temas no hay contra qué medir: dejarla
    dejaría el avance de todos los grupos apuntando a temas inexistentes.
    """
    temas = db.exec(select(Tema).where(Tema.materia_id == materia_id)).all()
    ids = [tema.id for tema in temas]
    coberturas = (
        db.exec(select(Cobertura).where(Cobertura.tema_id.in_(ids))).all() if ids else []
    )
    conteo = {
        "coberturas": _borrar_todos(db, coberturas),
        "temas": _borrar_todos(db, temas),
    }
    db.flush()
    return conteo


def borrar_materia(db: Session, materia: Materia) -> dict:
    """Una materia entera, con su plan y todas sus secciones."""
    grupos = db.exec(select(Grupo).where(Grupo.materia_id == materia.id)).all()
    conteo = _sumar(
        *[borrar_grupo(db, grupo) for grupo in grupos],
        borrar_temario(db, materia.id),
        {"materias": 1},
    )
    db.delete(materia)
    db.flush()
    return conteo


def borrar_todos_los_grupos(db: Session) -> dict:
    """Vacía el horario conservando las materias y sus planes de estudio."""
    grupos = db.exec(select(Grupo)).all()
    return _sumar(*[borrar_grupo(db, grupo) for grupo in grupos]) or {"grupos": 0}


def borrar_todo(db: Session) -> dict:
    """Deja la base en blanco. Las banderas de instalación se conservan."""
    return _sumar(
        *[borrar_materia(db, materia) for materia in db.exec(select(Materia)).all()],
        # Restos de datos que ya no cuelgan de ninguna materia viva.
        {
            "grupos": _borrar_todos(db, db.exec(select(Grupo)).all()),
            "sesiones": _borrar_todos(db, db.exec(select(Sesion)).all()),
            "coberturas": _borrar_todos(db, db.exec(select(Cobertura)).all()),
            "temas": _borrar_todos(db, db.exec(select(Tema)).all()),
            "mensajes": _borrar_todos(db, db.exec(select(MensajeChat)).all()),
        },
    )


def marcar(db: Session, clave: str, valor: str) -> None:
    ajuste = db.get(Ajuste, clave)
    if ajuste:
        ajuste.valor = valor
    else:
        ajuste = Ajuste(clave=clave, valor=valor)
    db.add(ajuste)
    db.flush()


def desmarcar(db: Session, clave: str) -> None:
    ajuste = db.get(Ajuste, clave)
    if ajuste:
        db.delete(ajuste)
        db.flush()

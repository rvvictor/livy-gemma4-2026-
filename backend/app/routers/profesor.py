"""Vista del profesor sobre su ciclo completo: la agenda de la semana y el mapa
de todas sus materias.

El problema que Livy ataca no es solo "resumir una clase", es la organización de
un ciclo escolar entero repartido en varias materias y varias secciones. Estos
endpoints son los que arman esa vista de sistema.

Ninguno de los dos llama al modelo: el tema sugerido para cada clase de la semana
sale del avance ya registrado. Consultar la agenda no gasta cuota.
"""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..avance import estado_de_grupo, temas_de_materia
from ..db import obtener_sesion
from ..models import Grupo, Materia, Sesion

router = APIRouter(prefix="/api/profesor", tags=["profesor"])

DIAS_NOMBRE = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado",
    7: "Domingo",
}


@router.get("/ciclo")
def ciclo(db: Session = Depends(obtener_sesion)) -> dict:
    """Todas las materias del profesor, su plan y el avance de cada sección.

    Es la respuesta a "¿cómo va mi semestre completo?", no a "¿cómo va este grupo?".
    """
    materias = db.exec(select(Materia)).all()
    if not materias:
        raise HTTPException(404, "No hay materias registradas")

    salida = []
    for materia in materias:
        temas = temas_de_materia(db, materia.id)
        grupos = db.exec(select(Grupo).where(Grupo.materia_id == materia.id)).all()
        estados = [estado_de_grupo(db, grupo, temas) for grupo in grupos]

        avance_promedio = sum(e["avance"] for e in estados) / len(estados) if estados else 0.0
        salida.append(
            {
                "id": materia.id,
                "nombre": materia.nombre,
                "clave": materia.clave,
                "ciclo": materia.ciclo,
                "profesor": materia.profesor,
                "relacion": materia.relacion,
                "sesiones_planeadas": materia.sesiones_planeadas,
                "avance_promedio": round(avance_promedio, 3),
                "temas": [
                    {"id": t.id, "orden": t.orden, "unidad": t.unidad, "titulo": t.titulo,
                     "subtemas": t.subtemas}
                    for t in temas
                ],
                "grupos": estados,
            }
        )

    # Grupos que aparecen en más de una materia: son los mismos alumnos y el
    # profesor debería verlos como una sola población, no como dos listas.
    conteo: dict[str, list[str]] = {}
    for materia in salida:
        for grupo in materia["grupos"]:
            conteo.setdefault(grupo["grupo"], []).append(materia["nombre"])
    compartidos = [
        {"grupo": nombre, "materias": materias_}
        for nombre, materias_ in conteo.items()
        if len(materias_) > 1
    ]

    total_alumnos = sum(g["alumnos"] for m in salida for g in m["grupos"])
    return {
        "profesor": materias[0].profesor,
        "ciclo": materias[0].ciclo,
        "materias": salida,
        "grupos_compartidos": compartidos,
        "total_grupos": sum(len(m["grupos"]) for m in salida),
        "total_alumnos": total_alumnos,
    }


@router.get("/agenda")
def agenda(referencia: str | None = None, db: Session = Depends(obtener_sesion)) -> dict:
    """Las clases de una semana, con el tema que toca en cada una.

    `referencia` es cualquier día dentro de la semana deseada (por defecto, hoy).
    Para las clases que ya se impartieron se muestra lo que realmente se vio; para
    las que faltan, el siguiente tema pendiente de esa sección, avanzando la
    sugerencia si el grupo tiene más de una clase en la semana.
    """
    try:
        dia_referencia = date.fromisoformat(referencia) if referencia else date.today()
    except ValueError as error:
        raise HTTPException(400, "La fecha debe venir en formato AAAA-MM-DD") from error

    lunes = dia_referencia - timedelta(days=dia_referencia.weekday())
    dias_semana = [lunes + timedelta(days=i) for i in range(7)]

    materias = {m.id: m for m in db.exec(select(Materia)).all()}
    grupos = db.exec(select(Grupo)).all()

    entradas = []
    for grupo in grupos:
        materia = materias.get(grupo.materia_id)
        if not materia:
            continue

        temas = temas_de_materia(db, materia.id)
        estado = estado_de_grupo(db, grupo, temas)
        pendientes = [
            fila for fila in estado["detalle"] if fila["nivel"] in (None, "introducido")
        ]
        siguiente_por_asignar = 0

        fechas_del_grupo = [f for f in dias_semana if f.isoweekday() in grupo.dias]
        for fecha in fechas_del_grupo:
            sesion = db.exec(
                select(Sesion).where(Sesion.grupo_id == grupo.id, Sesion.fecha == fecha)
            ).first()

            if sesion and sesion.estado == "cerrada":
                estado_clase = "impartida"
                tema = {"titulo": sesion.titulo, "nota": "Lo que realmente se vio"}
            elif sesion and sesion.estado == "en_curso":
                estado_clase = "en_curso"
                tema = {"titulo": "Sesión abierta ahora mismo", "nota": ""}
            else:
                estado_clase = "planeada"
                if siguiente_por_asignar < len(pendientes):
                    propuesto = pendientes[siguiente_por_asignar]
                    siguiente_por_asignar += 1
                    nota = (
                        "Quedó a medias, conviene cerrarlo"
                        if propuesto["nivel"] == "introducido"
                        else "Siguiente en el plan"
                    )
                    tema = {"titulo": propuesto["titulo"], "nota": nota}
                else:
                    tema = {"titulo": "Plan de estudios completo", "nota": ""}

            entradas.append(
                {
                    "fecha": fecha.isoformat(),
                    "dia": DIAS_NOMBRE[fecha.isoweekday()],
                    "hora_inicio": grupo.hora_inicio,
                    "hora_fin": grupo.hora_fin,
                    "materia": materia.nombre,
                    "materia_id": materia.id,
                    "clave": materia.clave,
                    "grupo": grupo.nombre,
                    "grupo_id": grupo.id,
                    "alumnos": grupo.alumnos,
                    "estado": estado_clase,
                    "sesion_id": sesion.id if sesion else None,
                    "tema": tema,
                    "avance": estado["avance"],
                }
            )

    entradas.sort(key=lambda e: (e["fecha"], e["hora_inicio"]))

    return {
        "inicio": lunes.isoformat(),
        "fin": (lunes + timedelta(days=6)).isoformat(),
        "hoy": date.today().isoformat(),
        "es_semana_actual": lunes == date.today() - timedelta(days=date.today().weekday()),
        "clases": entradas,
        "total": len(entradas),
        "impartidas": len([e for e in entradas if e["estado"] == "impartida"]),
    }

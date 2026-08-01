"""Vista del profesor sobre su ciclo completo: la agenda de la semana y el mapa
de todas sus materias.

El problema que Livy ataca no es solo "resumir una clase", es la organización de
un ciclo escolar entero repartido en varias materias y varias secciones. Estos
endpoints son los que arman esa vista de sistema.

Ninguno de los dos llama al modelo: el tema sugerido para cada clase de la semana
sale del avance ya registrado. Consultar la agenda no gasta cuota.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from .. import gemma, prompts
from ..archivos import leer_documento
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


class ClaseHorario(BaseModel):
    materia: str
    clave: str = ""
    grupo: str
    dias: list[int] = []
    hora_inicio: str = ""
    hora_fin: str = ""
    alumnos: int = 0


class HorarioEntrada(BaseModel):
    clases: list[ClaseHorario]


DIAS_CORTOS = {1: "Lun", 2: "Mar", 3: "Mié", 4: "Jue", 5: "Vie", 6: "Sáb", 7: "Dom"}


def _horario_legible(dias: list[int], inicio: str, fin: str) -> str:
    nombres = [DIAS_NOMBRE.get(dia, str(dia)) for dia in sorted(set(dias))]
    etiqueta = " y ".join(nombres) if len(nombres) == 2 else ", ".join(nombres)
    return f"{etiqueta}, {inicio}–{fin}" if etiqueta else f"{inicio}–{fin}"


@router.post("/horario/analizar")
async def analizar_horario(
    archivo: UploadFile = File(...),
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Lee el horario semanal de una foto o un PDF y propone la estructura.

    No escribe nada: la propuesta va a la pantalla de revisión, igual que el
    temario. El profesor corrige antes de que quede asentado.
    """
    imagenes, texto_fuente = await leer_documento(archivo)

    materia = db.exec(select(Materia)).first()
    nombre_profesor = materia.profesor if materia else "el profesor"

    try:
        resultado = await gemma.generar(
            prompts.leer_horario(nombre_profesor, texto_fuente),
            sistema=prompts.SISTEMA,
            imagenes=imagenes,
            json_esperado=True,
            simulado=prompts.simulacion("horario"),
            temperatura=0.1,
        )
    except gemma.ErrorGemma as error:
        raise HTTPException(502, str(error)) from error

    crudas = resultado.get("clases", []) if isinstance(resultado, dict) else []
    if not crudas:
        raise HTTPException(422, "Gemma no encontró clases legibles en el documento")

    # Se comparan contra lo que ya existe para poder avisar en la revisión qué se
    # va a crear y qué solo se va a actualizar.
    existentes = {
        (m.nombre.strip().lower(), g.nombre.strip().lower())
        for m in db.exec(select(Materia)).all()
        for g in db.exec(select(Grupo).where(Grupo.materia_id == m.id)).all()
    }

    limpias = []
    for cruda in crudas:
        nombre_materia = str(cruda.get("materia", "")).strip()
        nombre_grupo = str(cruda.get("grupo", "")).strip()
        if not nombre_materia or not nombre_grupo:
            continue
        dias = sorted({int(d) for d in cruda.get("dias", []) if str(d).isdigit() and 1 <= int(d) <= 7})
        limpias.append(
            {
                "materia": nombre_materia,
                "clave": str(cruda.get("clave", "")).strip(),
                "grupo": nombre_grupo,
                "dias": dias,
                "dias_texto": ", ".join(DIAS_CORTOS[d] for d in dias),
                "hora_inicio": str(cruda.get("hora_inicio", "")).strip(),
                "hora_fin": str(cruda.get("hora_fin", "")).strip(),
                "alumnos": 0,
                "nueva": (nombre_materia.lower(), nombre_grupo.lower()) not in existentes,
            }
        )

    if not limpias:
        raise HTTPException(422, "Gemma leyó el documento pero no reconoció ninguna clase")

    return {
        "clases": limpias,
        "fuente": "pdf" if texto_fuente else "imagen",
        "nuevas": len([c for c in limpias if c["nueva"]]),
    }


@router.put("/horario")
def guardar_horario(
    entrada: HorarioEntrada,
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Aplica el horario que el profesor ya validó.

    La operación es **aditiva**: crea las materias y los grupos que no existan y
    actualiza los días y horas de los que sí. Nunca borra un grupo, porque con él
    se iría su bitácora de avance, que es el activo del producto.
    """
    if not entrada.clases:
        raise HTTPException(400, "El horario no puede quedar vacío")

    materia_referencia = db.exec(select(Materia)).first()
    profesor = materia_referencia.profesor if materia_referencia else "Profesor"
    ciclo = materia_referencia.ciclo if materia_referencia else ""

    creadas_materias, creados_grupos, actualizados = 0, 0, 0

    for clase in entrada.clases:
        nombre_materia = clase.materia.strip()
        nombre_grupo = clase.grupo.strip()
        if not nombre_materia or not nombre_grupo:
            continue

        materia = next(
            (
                m
                for m in db.exec(select(Materia)).all()
                if m.nombre.strip().lower() == nombre_materia.lower()
            ),
            None,
        )
        if not materia:
            materia = Materia(
                nombre=nombre_materia,
                profesor=profesor,
                clave=clase.clave.strip(),
                ciclo=ciclo,
            )
            db.add(materia)
            db.commit()
            db.refresh(materia)
            creadas_materias += 1
        elif clase.clave.strip() and not materia.clave:
            materia.clave = clase.clave.strip()
            db.add(materia)

        grupo = next(
            (
                g
                for g in db.exec(select(Grupo).where(Grupo.materia_id == materia.id)).all()
                if g.nombre.strip().lower() == nombre_grupo.lower()
            ),
            None,
        )
        dias = sorted({d for d in clase.dias if 1 <= d <= 7})

        if grupo:
            actualizados += 1
        else:
            grupo = Grupo(materia_id=materia.id, nombre=nombre_grupo, alumnos=clase.alumnos)
            creados_grupos += 1

        grupo.dias_json = json.dumps(dias)
        grupo.hora_inicio = clase.hora_inicio
        grupo.hora_fin = clase.hora_fin
        grupo.horario = _horario_legible(dias, clase.hora_inicio, clase.hora_fin)
        if clase.alumnos:
            grupo.alumnos = clase.alumnos
        db.add(grupo)

    db.commit()

    return {
        "materias_creadas": creadas_materias,
        "grupos_creados": creados_grupos,
        "grupos_actualizados": actualizados,
    }


@router.get("/ciclo")
def ciclo(db: Session = Depends(obtener_sesion)) -> dict:
    """Todas las materias del profesor, su plan y el avance de cada sección.

    Es la respuesta a "¿cómo va mi semestre completo?", no a "¿cómo va este grupo?".

    Una base vacía no es un error, es el estado inicial de un profesor que acaba
    de borrar todo y va a cargar su horario: se responde con la misma estructura
    sin nada dentro para que la interfaz siga en pie.
    """
    materias = db.exec(select(Materia)).all()
    if not materias:
        return {
            "profesor": "",
            "ciclo": "",
            "materias": [],
            "grupos_compartidos": [],
            "total_grupos": 0,
            "total_alumnos": 0,
        }

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

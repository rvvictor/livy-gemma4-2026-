"""Siembra de la base de demostración.

Arma la historia del producto: **un profesor, dos materias conectadas, cinco
grupos, cinco puntos distintos del temario**. El 1CV1 de Cálculo va al corriente,
el 2CV2 perdió una sesión por un puente y el 3CV3 se quedó a medias de un tema
por un simulacro. Encima, el grupo 1CV1 lleva las dos materias con la misma
profesora, así que el ciclo se ve como un sistema y no como asignaturas sueltas.

Las fechas se generan **relativas a hoy** y el historial termina ayer: así la
agenda de la semana en curso siempre trae clases ya impartidas y clases todavía
pendientes, sin importar cuándo se ejecute la demostración.

El contenido de las clases vive en `contenido_demo.py`. Aquí solo está el cableado.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

from sqlmodel import Session, select

from .contenido_demo import (
    CALCULO_1CV1,
    CALCULO_2CV2,
    CALCULO_3CV3,
    DUDAS,
    GEOMETRIA_1CV1,
    GEOMETRIA_4CM2,
    TEMARIO_CALCULO,
    TEMARIO_GEOMETRIA,
)
from .db import motor
from .models import Cobertura, Grupo, Materia, MensajeChat, Sesion, Tema

# Se retrocede lo suficiente para que quepa el historial de cualquier grupo.
SEMANAS_DE_HISTORIA = 10

DIAS_NOMBRE = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}

MATERIAS = [
    {
        "nombre": "Cálculo Diferencial",
        "clave": "MAT-1201",
        "ciclo": "2026/1",
        "sesiones_planeadas": 32,
        "relacion": (
            "El grupo 1CV1 lleva también Geometría Analítica con la misma profesora. Las "
            "transformaciones de funciones de la Unidad 2 preparan el terreno para la "
            "traslación de ejes en cónicas, y la pendiente de la recta anticipa la derivada."
        ),
        "temario": TEMARIO_CALCULO,
        "grupos": [
            {"nombre": "1CV1", "dias": [1, 3], "inicio": "07:00", "fin": "08:30",
             "alumnos": 42, "clases": CALCULO_1CV1, "saltos": []},
            # El 2CV2 perdió la quinta sesión del calendario por el puente.
            {"nombre": "2CV2", "dias": [2, 4], "inicio": "12:30", "fin": "14:00",
             "alumnos": 38, "clases": CALCULO_2CV2, "saltos": [4]},
            {"nombre": "3CV3", "dias": [1, 5], "inicio": "18:00", "fin": "19:30",
             "alumnos": 45, "clases": CALCULO_3CV3, "saltos": []},
        ],
    },
    {
        "nombre": "Geometría Analítica",
        "clave": "MAT-1202",
        "ciclo": "2026/1",
        "sesiones_planeadas": 28,
        "relacion": (
            "Comparte el grupo 1CV1 con Cálculo Diferencial: son los mismos alumnos en las dos "
            "materias. La traslación de ejes en cónicas se apoya en las transformaciones de "
            "funciones que ese grupo ya vio en Cálculo, y la pendiente de la recta es la misma "
            "razón de cambio que después se generaliza en la derivada."
        ),
        "temario": TEMARIO_GEOMETRIA,
        "grupos": [
            {"nombre": "1CV1", "dias": [2, 4], "inicio": "07:00", "fin": "08:30",
             "alumnos": 42, "clases": GEOMETRIA_1CV1, "saltos": []},
            {"nombre": "4CM2", "dias": [3, 5], "inicio": "10:00", "fin": "11:30",
             "alumnos": 40, "clases": GEOMETRIA_4CM2, "saltos": []},
        ],
    },
]


def _fechas_de_clase(dias: list[int], desde: date, hasta: date, cantidad: int) -> list[date]:
    """Las últimas `cantidad` fechas de clase del grupo, terminando en `hasta`.

    Se cuenta hacia atrás en vez de hacia adelante para que el historial sembrado
    siempre termine pegado a la fecha de hoy.
    """
    todas: list[date] = []
    cursor = desde
    while cursor <= hasta:
        if cursor.isoweekday() in dias:
            todas.append(cursor)
        cursor += timedelta(days=1)
    return todas[-cantidad:]


def _horario_legible(dias: list[int], inicio: str, fin: str) -> str:
    nombres = [DIAS_NOMBRE.get(dia, str(dia)) for dia in dias]
    etiqueta = " y ".join(nombres) if len(nombres) == 2 else ", ".join(nombres)
    return f"{etiqueta}, {inicio}–{fin}"


def sembrar_si_esta_vacia() -> None:
    """Crea las materias de demostración solo si no hay nada en la base."""
    with Session(motor) as db:
        if db.exec(select(Materia)).first():
            return

        hoy = date.today()
        inicio_ciclo = hoy - timedelta(weeks=SEMANAS_DE_HISTORIA)
        # El historial llega hasta ayer: las clases de hoy quedan pendientes en la
        # agenda, que es como el profesor abre la aplicación por la mañana.
        fin_historial = hoy - timedelta(days=1)

        indice_grupos: dict[tuple[str, str], int] = {}
        indice_sesiones: dict[tuple[str, str], list[int]] = {}

        for definicion in MATERIAS:
            materia = Materia(
                nombre=definicion["nombre"],
                profesor="Ing. Leticia Ramírez",
                clave=definicion["clave"],
                ciclo=definicion["ciclo"],
                sesiones_planeadas=definicion["sesiones_planeadas"],
                relacion=definicion["relacion"],
            )
            db.add(materia)
            db.commit()
            db.refresh(materia)

            temas_por_orden: dict[int, Tema] = {}
            for indice, (unidad, titulo, subtemas) in enumerate(definicion["temario"], start=1):
                tema = Tema(
                    materia_id=materia.id,
                    orden=indice,
                    unidad=unidad,
                    titulo=titulo,
                    subtemas_json=json.dumps(subtemas, ensure_ascii=False),
                )
                db.add(tema)
                temas_por_orden[indice] = tema
            db.commit()
            for tema in temas_por_orden.values():
                db.refresh(tema)

            for definicion_grupo in definicion["grupos"]:
                grupo = Grupo(
                    materia_id=materia.id,
                    nombre=definicion_grupo["nombre"],
                    horario=_horario_legible(
                        definicion_grupo["dias"],
                        definicion_grupo["inicio"],
                        definicion_grupo["fin"],
                    ),
                    alumnos=definicion_grupo["alumnos"],
                    dias_json=json.dumps(definicion_grupo["dias"]),
                    hora_inicio=definicion_grupo["inicio"],
                    hora_fin=definicion_grupo["fin"],
                )
                db.add(grupo)
                db.commit()
                db.refresh(grupo)
                indice_grupos[(materia.nombre, grupo.nombre)] = grupo.id

                clases = definicion_grupo["clases"]
                saltos = set(definicion_grupo["saltos"])
                # Se piden fechas de más para poder saltar las sesiones perdidas.
                calendario = _fechas_de_clase(
                    definicion_grupo["dias"],
                    inicio_ciclo,
                    fin_historial,
                    len(clases) + len(saltos),
                )
                fechas = [f for i, f in enumerate(calendario) if i not in saltos]

                ids_sesiones: list[int] = []
                for fecha, clase in zip(fechas, clases):
                    (
                        titulo,
                        coberturas,
                        resumen,
                        puntos,
                        donde_quedo,
                        pendientes,
                        transcripcion,
                    ) = clase

                    sesion = Sesion(
                        grupo_id=grupo.id,
                        fecha=fecha,
                        estado="cerrada",
                        titulo=titulo,
                        transcripcion=transcripcion,
                        duracion_min=90,
                        resumen_json=json.dumps(
                            {
                                "titulo": titulo,
                                "resumen": resumen,
                                "puntos_clave": puntos,
                                "donde_quedo": donde_quedo,
                                "pendientes": pendientes,
                                "dudas_detectadas": [],
                            },
                            ensure_ascii=False,
                        ),
                    )
                    db.add(sesion)
                    db.commit()
                    db.refresh(sesion)
                    ids_sesiones.append(sesion.id)

                    for orden, nivel in coberturas:
                        db.add(
                            Cobertura(
                                sesion_id=sesion.id,
                                grupo_id=grupo.id,
                                tema_id=temas_por_orden[orden].id,
                                nivel=nivel,
                                evidencia=transcripcion[:200],
                            )
                        )
                    db.commit()

                indice_sesiones[(materia.nombre, grupo.nombre)] = ids_sesiones

        for materia_nombre, grupo_nombre, indice_clase, pregunta, respuesta in DUDAS:
            grupo_id = indice_grupos.get((materia_nombre, grupo_nombre))
            if grupo_id is None:
                continue
            sesiones = indice_sesiones.get((materia_nombre, grupo_nombre), [])
            sesion_id = (
                sesiones[indice_clase]
                if indice_clase is not None and indice_clase < len(sesiones)
                else None
            )
            db.add(
                MensajeChat(
                    grupo_id=grupo_id, sesion_id=sesion_id, rol="alumno", contenido=pregunta
                )
            )
            db.add(
                MensajeChat(
                    grupo_id=grupo_id, sesion_id=sesion_id, rol="asistente", contenido=respuesta
                )
            )
        db.commit()

"""Modelo de datos de Livy.

La pieza que define al producto es `Cobertura`: cada sesión deja registros de qué
temas del plan de estudios se tocaron **y en qué grupo**. El avance se calcula
siempre por sección, nunca por materia — ahí vive la continuidad que ninguna otra
herramienta resuelve.
"""

from __future__ import annotations

import json
from datetime import date, datetime

from sqlmodel import Field, SQLModel

# Cuánto cuenta cada nivel para el porcentaje de avance de un tema.
NIVELES: dict[str, float] = {
    "introducido": 0.4,   # se mencionó y se abrió el tema
    "cubierto": 1.0,      # se explicó completo
    "reforzado": 1.0,     # se repasó algo ya cubierto
}


class Materia(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    profesor: str
    clave: str = ""
    ciclo: str = ""
    sesiones_planeadas: int = 32
    # Materias que comparten alumnos o que se apoyan en esta: permite ver el ciclo
    # completo del profesor como un sistema, no como asignaturas sueltas.
    relacion: str = ""


class Tema(SQLModel, table=True):
    """Un punto del plan de estudios. El orden importa: define la secuencia."""

    id: int | None = Field(default=None, primary_key=True)
    materia_id: int = Field(foreign_key="materia.id", index=True)
    orden: int
    unidad: str = ""
    titulo: str
    subtemas_json: str = "[]"

    @property
    def subtemas(self) -> list[str]:
        try:
            return json.loads(self.subtemas_json)
        except json.JSONDecodeError:
            return []


class Grupo(SQLModel, table=True):
    """Una sección. Varias secciones comparten materia y temario, pero cada una
    avanza a su propio ritmo."""

    id: int | None = Field(default=None, primary_key=True)
    materia_id: int = Field(foreign_key="materia.id", index=True)
    nombre: str
    horario: str = ""
    alumnos: int = 0
    # Días de la semana en formato ISO (1 = lunes … 7 = domingo). Estructurado
    # para poder armar la agenda semanal sin interpretar texto libre.
    dias_json: str = "[]"
    hora_inicio: str = ""
    hora_fin: str = ""

    @property
    def dias(self) -> list[int]:
        try:
            return json.loads(self.dias_json)
        except json.JSONDecodeError:
            return []


class Sesion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    grupo_id: int = Field(foreign_key="grupo.id", index=True)
    fecha: date = Field(default_factory=date.today)
    estado: str = "planeada"  # planeada | en_curso | cerrada
    titulo: str = ""
    transcripcion: str = ""
    resumen_json: str = ""
    duracion_min: int = 0
    creada_en: datetime = Field(default_factory=datetime.utcnow)

    @property
    def resumen(self) -> dict:
        if not self.resumen_json:
            return {}
        try:
            return json.loads(self.resumen_json)
        except json.JSONDecodeError:
            return {}


class Cobertura(SQLModel, table=True):
    """Qué tema se tocó, en qué sesión, en qué grupo y con qué profundidad.

    `grupo_id` está desnormalizado a propósito: la consulta que más se ejecuta es
    "dame el avance de este grupo" y así se resuelve sin join.
    """

    id: int | None = Field(default=None, primary_key=True)
    sesion_id: int = Field(foreign_key="sesion.id", index=True)
    grupo_id: int = Field(foreign_key="grupo.id", index=True)
    tema_id: int = Field(foreign_key="tema.id", index=True)
    nivel: str = "cubierto"
    evidencia: str = ""


class Ajuste(SQLModel, table=True):
    """Banderas de la instalación, una fila por clave.

    Existe por una sola razón: recordar que el profesor ya vació la base a
    propósito, para que el sembrado de demostración no se la vuelva a llenar en
    el siguiente arranque del servidor.
    """

    clave: str = Field(primary_key=True)
    valor: str = ""


class MensajeChat(SQLModel, table=True):
    """Historial del chat del alumno.

    `sesion_id` en nulo significa una pregunta general sobre todo el curso;
    con valor, la pregunta está acotada a esa clase. Las preguntas de los alumnos
    alimentan además el panel de dudas del grupo.
    """

    id: int | None = Field(default=None, primary_key=True)
    grupo_id: int = Field(foreign_key="grupo.id", index=True)
    sesion_id: int | None = Field(default=None, foreign_key="sesion.id", index=True)
    rol: str = "alumno"  # alumno | asistente
    contenido: str = ""
    creado_en: datetime = Field(default_factory=datetime.utcnow)

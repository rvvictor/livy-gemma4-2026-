"""Acceso a datos.

SQLite en lugar de PostgreSQL: es el mismo SQL, cero operación durante el sprint,
y el disco del tier gratuito de Render es efímero de todos modos —los datos de
demostración se resiembran al arrancar. Migrar a Postgres es cambiar `DATABASE_URL`.
"""

from sqlmodel import Session, SQLModel, create_engine

from .config import DATABASE_URL

_argumentos = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
motor = create_engine(DATABASE_URL, echo=False, connect_args=_argumentos)


def crear_tablas() -> None:
    SQLModel.metadata.create_all(motor)


def obtener_sesion():
    """Dependencia de FastAPI: una sesión de base de datos por petición."""
    with Session(motor) as sesion:
        yield sesion

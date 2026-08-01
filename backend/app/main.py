"""Punto de entrada de la API de Livy."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGENES, GEMMA_MODELO, MODO_SIMULADO
from .db import crear_tablas
from .routers import alumno, bitacora, sesiones, temario
from .seed import sembrar_si_esta_vacia


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    crear_tablas()
    sembrar_si_esta_vacia()
    yield


app = FastAPI(
    title="Livy — asistente de continuidad docente",
    description=(
        "Convierte cada clase en memoria estructurada y lleva la bitácora de avance "
        "de cada grupo contra el plan de estudios. Construido sobre Gemma 4."
    ),
    version="1.0.0",
    lifespan=ciclo_de_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGENES,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(temario.router)
app.include_router(sesiones.router)
app.include_router(bitacora.router)
app.include_router(alumno.router)


@app.get("/health")
def salud() -> dict:
    """Verificación de vida. Delata si falta la clave sin exponerla."""
    return {
        "estado": "ok",
        "modelo": GEMMA_MODELO,
        "modo_simulado": MODO_SIMULADO,
    }

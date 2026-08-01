"""Portal del alumno: consulta de sus clases y chat anclado a ellas.

Tres decisiones deliberadas de privacidad y de producto:

- El alumno ve el resumen y, si lo pide explícitamente, la transcripción de la
  clase; nunca el audio ni voces de sus compañeros.
- El chat responde con lo que su profesor enseñó **a su grupo**, no con internet
  genérico. Si el tema aún no se ve en su sección, lo dice en vez de adelantarse.
- Hay dos alcances de conversación: general sobre todo el curso, o acotada a una
  clase concreta. Las preguntas quedan registradas y alimentan el panel de dudas
  del grupo, que le muestra a cada quien dónde se está atorando el resto.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from .. import gemma, prompts
from ..avance import historial_de_clases
from ..db import obtener_sesion
from ..models import Grupo, Materia, MensajeChat, Sesion

router = APIRouter(prefix="/api", tags=["alumno"])

MENSAJES_DE_CONTEXTO = 6


class PreguntaEntrada(BaseModel):
    pregunta: str


class GuiaEntrada(BaseModel):
    enfoque: str = ""


def _materia_y_grupo(db: Session, grupo_id: int) -> tuple[Materia, Grupo]:
    grupo = db.get(Grupo, grupo_id)
    if not grupo:
        raise HTTPException(404, "Grupo no encontrado")
    materia = db.get(Materia, grupo.materia_id)
    if not materia:
        raise HTTPException(404, "Materia no encontrada")
    return materia, grupo


def _conversacion_previa(db: Session, grupo_id: int, sesion_id: int | None) -> str:
    consulta = select(MensajeChat).where(MensajeChat.grupo_id == grupo_id)
    consulta = consulta.where(
        MensajeChat.sesion_id == sesion_id
        if sesion_id is not None
        else MensajeChat.sesion_id.is_(None)
    )
    previos = db.exec(consulta.order_by(MensajeChat.id.desc()).limit(MENSAJES_DE_CONTEXTO)).all()
    return "\n".join(
        f"{'Alumno' if m.rol == 'alumno' else 'Livy'}: {m.contenido}" for m in reversed(previos)
    )


@router.get("/alumno/grupos")
def grupos_disponibles(db: Session = Depends(obtener_sesion)) -> list[dict]:
    """Índice del portal: todas las secciones a las que un alumno puede entrar."""
    grupos = db.exec(select(Grupo)).all()
    materias = {m.id: m for m in db.exec(select(Materia)).all()}

    salida = []
    for grupo in grupos:
        materia = materias.get(grupo.materia_id)
        if not materia:
            continue
        clases = db.exec(
            select(Sesion).where(Sesion.grupo_id == grupo.id, Sesion.estado == "cerrada")
        ).all()
        salida.append(
            {
                "grupo_id": grupo.id,
                "grupo": grupo.nombre,
                "materia": materia.nombre,
                "clave": materia.clave,
                "profesor": materia.profesor,
                "horario": grupo.horario,
                "clases": len(clases),
                "ultima_clase": max((s.fecha for s in clases), default=None),
            }
        )
    salida.sort(key=lambda g: (g["materia"], g["grupo"]))
    return [
        {**g, "ultima_clase": g["ultima_clase"].isoformat() if g["ultima_clase"] else None}
        for g in salida
    ]


@router.get("/grupos/{grupo_id}/clases")
def clases_del_grupo(grupo_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Listado de solo lectura: qué se vio en cada sesión de este grupo."""
    materia, grupo = _materia_y_grupo(db, grupo_id)
    sesiones = db.exec(
        select(Sesion)
        .where(Sesion.grupo_id == grupo_id, Sesion.estado == "cerrada")
        .order_by(Sesion.fecha.desc())
    ).all()

    return {
        "materia": materia.nombre,
        "clave": materia.clave,
        "profesor": materia.profesor,
        "grupo": grupo.nombre,
        "grupo_id": grupo.id,
        "horario": grupo.horario,
        "clases": [
            {
                "id": s.id,
                "fecha": s.fecha.isoformat(),
                "titulo": s.titulo,
                # En el listado va solo la primera idea; el detalle vive en su propia página.
                "adelanto": (s.resumen.get("resumen", "").split("\n")[0] or "")[:180],
                "donde_quedo": s.resumen.get("donde_quedo", ""),
            }
            for s in sesiones
        ],
    }


@router.get("/sesiones/{sesion_id}/publica")
def clase_para_alumno(sesion_id: int, db: Session = Depends(obtener_sesion)) -> dict:
    """Una clase concreta, con todo su detalle y su transcripción."""
    sesion = db.get(Sesion, sesion_id)
    if not sesion or sesion.estado != "cerrada":
        raise HTTPException(404, "Clase no encontrada")

    materia, grupo = _materia_y_grupo(db, sesion.grupo_id)
    resumen = sesion.resumen

    vecinas = db.exec(
        select(Sesion)
        .where(Sesion.grupo_id == sesion.grupo_id, Sesion.estado == "cerrada")
        .order_by(Sesion.fecha)
    ).all()
    posicion = [s.id for s in vecinas].index(sesion.id)

    return {
        "id": sesion.id,
        "fecha": sesion.fecha.isoformat(),
        "titulo": sesion.titulo,
        "duracion_min": sesion.duracion_min,
        "materia": materia.nombre,
        "profesor": materia.profesor,
        "grupo": grupo.nombre,
        "grupo_id": grupo.id,
        "numero": posicion + 1,
        "total": len(vecinas),
        "resumen": resumen.get("resumen", ""),
        "puntos_clave": resumen.get("puntos_clave", []),
        "donde_quedo": resumen.get("donde_quedo", ""),
        "pendientes": resumen.get("pendientes", []),
        "dudas_detectadas": resumen.get("dudas_detectadas", []),
        "transcripcion": sesion.transcripcion,
        "anterior": vecinas[posicion - 1].id if posicion > 0 else None,
        "siguiente": vecinas[posicion + 1].id if posicion + 1 < len(vecinas) else None,
    }


def _serializar_duda(pregunta: MensajeChat, respuesta: str, titulo: str) -> dict:
    return {
        "id": pregunta.id,
        "contenido": pregunta.contenido,
        "respuesta": respuesta,
        "sesion_id": pregunta.sesion_id,
        "clase": titulo,
    }


def _respuestas_por_pregunta(db: Session, preguntas: list[MensajeChat]) -> dict[int, str]:
    """Empareja cada pregunta con la respuesta que Livy dio justo después."""
    if not preguntas:
        return {}
    posteriores = db.exec(
        select(MensajeChat)
        .where(MensajeChat.rol == "asistente", MensajeChat.id > min(p.id for p in preguntas))
        .order_by(MensajeChat.id)
    ).all()
    emparejadas: dict[int, str] = {}
    for pregunta in preguntas:
        siguiente = next((m for m in posteriores if m.id > pregunta.id), None)
        if siguiente:
            emparejadas[pregunta.id] = siguiente.contenido
    return emparejadas


@router.get("/grupos/{grupo_id}/dudas")
def dudas_del_grupo(
    grupo_id: int,
    alcance: str = "general",
    db: Session = Depends(obtener_sesion),
) -> list[dict]:
    """Lo que están preguntando los alumnos de este grupo sobre el curso completo.

    Es la vista que le revela al profesor dónde falló la explicación sin tener que
    preguntarle a nadie. Con `alcance=general` (por defecto) solo trae las dudas
    que no están atadas a una clase concreta; las de cada sesión viven en el
    endpoint de esa sesión.
    """
    _materia_y_grupo(db, grupo_id)

    consulta = select(MensajeChat).where(
        MensajeChat.grupo_id == grupo_id, MensajeChat.rol == "alumno"
    )
    if alcance == "general":
        consulta = consulta.where(MensajeChat.sesion_id.is_(None))

    preguntas = db.exec(consulta.order_by(MensajeChat.id.desc()).limit(40)).all()
    respuestas = _respuestas_por_pregunta(db, preguntas)
    titulos = {
        s.id: s.titulo for s in db.exec(select(Sesion).where(Sesion.grupo_id == grupo_id)).all()
    }

    return [
        _serializar_duda(
            pregunta,
            respuestas.get(pregunta.id, ""),
            titulos.get(pregunta.sesion_id, "") if pregunta.sesion_id else "",
        )
        for pregunta in preguntas
    ]


@router.get("/sesiones/{sesion_id}/dudas")
def dudas_de_la_clase(sesion_id: int, db: Session = Depends(obtener_sesion)) -> list[dict]:
    """Lo que se preguntó sobre esta clase en particular."""
    sesion = db.get(Sesion, sesion_id)
    if not sesion:
        raise HTTPException(404, "Clase no encontrada")

    preguntas = db.exec(
        select(MensajeChat)
        .where(MensajeChat.sesion_id == sesion_id, MensajeChat.rol == "alumno")
        .order_by(MensajeChat.id.desc())
        .limit(40)
    ).all()
    respuestas = _respuestas_por_pregunta(db, preguntas)

    return [
        _serializar_duda(pregunta, respuestas.get(pregunta.id, ""), sesion.titulo)
        for pregunta in preguntas
    ]


@router.get("/grupos/{grupo_id}/chat")
def historial_chat(grupo_id: int, db: Session = Depends(obtener_sesion)) -> list[dict]:
    """Conversación general del grupo, sin acotar a ninguna clase."""
    mensajes = db.exec(
        select(MensajeChat)
        .where(MensajeChat.grupo_id == grupo_id, MensajeChat.sesion_id.is_(None))
        .order_by(MensajeChat.id)
    ).all()
    return [{"rol": m.rol, "contenido": m.contenido} for m in mensajes]


@router.post("/grupos/{grupo_id}/chat")
async def preguntar(
    grupo_id: int,
    entrada: PreguntaEntrada,
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Pregunta general sobre todo lo visto en el curso.

    El historial completo del grupo entra íntegro en el contexto de 256K de
    Gemma 4: sin embeddings, sin base vectorial y sin fallos de recuperación.
    """
    materia, grupo = _materia_y_grupo(db, grupo_id)
    pregunta = entrada.pregunta.strip()
    if not pregunta:
        raise HTTPException(400, "La pregunta llegó vacía")

    historial = historial_de_clases(db, grupo_id, incluir_transcripcion=True)
    conversacion = _conversacion_previa(db, grupo_id, None)

    try:
        respuesta = await gemma.generar(
            prompts.responder_alumno(
                materia.nombre, grupo.nombre, historial, pregunta, conversacion
            ),
            sistema=prompts.SISTEMA,
            simulado=prompts.simulacion("texto"),
            temperatura=0.4,
            max_tokens=2048,
        )
    except gemma.ErrorGemma as error:
        raise HTTPException(502, str(error)) from error

    db.add(MensajeChat(grupo_id=grupo_id, rol="alumno", contenido=pregunta))
    db.add(MensajeChat(grupo_id=grupo_id, rol="asistente", contenido=respuesta))
    db.commit()

    return {"respuesta": respuesta}


@router.get("/sesiones/{sesion_id}/chat")
def historial_chat_clase(sesion_id: int, db: Session = Depends(obtener_sesion)) -> list[dict]:
    mensajes = db.exec(
        select(MensajeChat).where(MensajeChat.sesion_id == sesion_id).order_by(MensajeChat.id)
    ).all()
    return [{"rol": m.rol, "contenido": m.contenido} for m in mensajes]


@router.post("/sesiones/{sesion_id}/chat")
async def preguntar_sobre_clase(
    sesion_id: int,
    entrada: PreguntaEntrada,
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Pregunta acotada a una sola clase.

    Al reducir el contexto a esa sesión, la respuesta se apega a cómo se explicó
    el tema ese día en lugar de mezclarlo con el resto del semestre.
    """
    sesion = db.get(Sesion, sesion_id)
    if not sesion or sesion.estado != "cerrada":
        raise HTTPException(404, "Clase no encontrada")

    materia, grupo = _materia_y_grupo(db, sesion.grupo_id)
    pregunta = entrada.pregunta.strip()
    if not pregunta:
        raise HTTPException(400, "La pregunta llegó vacía")

    resumen = sesion.resumen
    contenido = "\n".join(
        parte
        for parte in [
            f"Clase del {sesion.fecha.isoformat()} — {sesion.titulo}",
            resumen.get("resumen", ""),
            "Puntos clave: " + "; ".join(resumen.get("puntos_clave", []))
            if resumen.get("puntos_clave")
            else "",
            f"Terminó en: {resumen.get('donde_quedo', '')}" if resumen.get("donde_quedo") else "",
            f"Transcripción:\n{sesion.transcripcion}" if sesion.transcripcion else "",
        ]
        if parte
    )

    try:
        respuesta = await gemma.generar(
            prompts.responder_sobre_clase(
                materia.nombre,
                grupo.nombre,
                contenido,
                pregunta,
                _conversacion_previa(db, grupo.id, sesion_id),
            ),
            sistema=prompts.SISTEMA,
            simulado=prompts.simulacion("texto"),
            temperatura=0.4,
            max_tokens=2048,
        )
    except gemma.ErrorGemma as error:
        raise HTTPException(502, str(error)) from error

    db.add(
        MensajeChat(grupo_id=grupo.id, sesion_id=sesion_id, rol="alumno", contenido=pregunta)
    )
    db.add(
        MensajeChat(grupo_id=grupo.id, sesion_id=sesion_id, rol="asistente", contenido=respuesta)
    )
    db.commit()

    return {"respuesta": respuesta}


@router.post("/grupos/{grupo_id}/guia")
async def guia_de_estudio(
    grupo_id: int,
    entrada: GuiaEntrada,
    db: Session = Depends(obtener_sesion),
) -> dict:
    """Guía de repaso construida sobre las clases que este grupo sí recibió."""
    materia, grupo = _materia_y_grupo(db, grupo_id)
    historial = historial_de_clases(db, grupo_id, incluir_transcripcion=True)

    try:
        guia = await gemma.generar(
            prompts.generar_guia(materia.nombre, grupo.nombre, historial, entrada.enfoque),
            sistema=prompts.SISTEMA,
            simulado=prompts.simulacion("texto"),
            temperatura=0.5,
            max_tokens=4096,
        )
    except gemma.ErrorGemma as error:
        raise HTTPException(502, str(error)) from error

    return {"guia": guia}

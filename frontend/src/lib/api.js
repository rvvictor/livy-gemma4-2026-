// Cliente HTTP de Livy. En desarrollo apunta al backend local; en Vercel se
// configura VITE_API_URL con la URL pública del servicio de Render.
const BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

async function pedir(ruta, opciones = {}) {
  const respuesta = await fetch(`${BASE}${ruta}`, {
    headers: opciones.body instanceof FormData ? {} : { "Content-Type": "application/json" },
    ...opciones,
  });

  if (!respuesta.ok) {
    let detalle = `Error ${respuesta.status}`;
    try {
      const cuerpo = await respuesta.json();
      detalle = cuerpo.detail || detalle;
    } catch {
      // El backend no devolvió JSON; nos quedamos con el código.
    }
    throw new Error(detalle);
  }

  return respuesta.json();
}

export const api = {
  salud: () => pedir("/health"),

  // — Profesor —
  ciclo: () => pedir("/api/profesor/ciclo"),
  agenda: (referencia) =>
    pedir(`/api/profesor/agenda${referencia ? `?referencia=${referencia}` : ""}`),

  analizarHorario: (archivo) => {
    const datos = new FormData();
    datos.append("archivo", archivo);
    return pedir("/api/profesor/horario/analizar", { method: "POST", body: datos });
  },
  guardarHorario: (clases) =>
    pedir("/api/profesor/horario", { method: "PUT", body: JSON.stringify({ clases }) }),

  materias: () => pedir("/api/materias"),
  materia: (id) => pedir(`/api/materias/${id}`),
  bitacora: (materiaId) => pedir(`/api/materias/${materiaId}/bitacora`),
  recomendaciones: (materiaId) => pedir(`/api/materias/${materiaId}/recomendaciones`),

  analizarTemario: (materiaId, archivo) => {
    const datos = new FormData();
    datos.append("archivo", archivo);
    return pedir(`/api/materias/${materiaId}/temario/analizar`, { method: "POST", body: datos });
  },
  guardarTemario: (materiaId, temas) =>
    pedir(`/api/materias/${materiaId}/temario`, {
      method: "PUT",
      body: JSON.stringify({ temas }),
    }),

  // — Clase en vivo —
  iniciarSesion: (grupoId) => pedir(`/api/grupos/${grupoId}/sesiones/iniciar`, { method: "POST" }),
  enviarFragmento: (sesionId, texto) =>
    pedir(`/api/sesiones/${sesionId}/transcripcion`, {
      method: "POST",
      body: JSON.stringify({ texto }),
    }),
  consultarEnVivo: (sesionId, pregunta) =>
    pedir(`/api/sesiones/${sesionId}/consultar`, {
      method: "POST",
      body: JSON.stringify({ pregunta }),
    }),
  cerrarSesion: (sesionId, duracionMin) =>
    pedir(`/api/sesiones/${sesionId}/cerrar`, {
      method: "POST",
      body: JSON.stringify({ duracion_min: duracionMin }),
    }),
  sesiones: (grupoId) => pedir(`/api/grupos/${grupoId}/sesiones`),

  // — Portal del alumno —
  gruposAlumno: () => pedir("/api/alumno/grupos"),
  clases: (grupoId) => pedir(`/api/grupos/${grupoId}/clases`),
  clase: (sesionId) => pedir(`/api/sesiones/${sesionId}/publica`),
  dudas: (grupoId, alcance = "general") =>
    pedir(`/api/grupos/${grupoId}/dudas?alcance=${alcance}`),
  dudasDeClase: (sesionId) => pedir(`/api/sesiones/${sesionId}/dudas`),

  historialChat: (grupoId) => pedir(`/api/grupos/${grupoId}/chat`),
  preguntar: (grupoId, pregunta) =>
    pedir(`/api/grupos/${grupoId}/chat`, {
      method: "POST",
      body: JSON.stringify({ pregunta }),
    }),
  historialChatClase: (sesionId) => pedir(`/api/sesiones/${sesionId}/chat`),
  preguntarSobreClase: (sesionId, pregunta) =>
    pedir(`/api/sesiones/${sesionId}/chat`, {
      method: "POST",
      body: JSON.stringify({ pregunta }),
    }),
  guia: (grupoId, enfoque) =>
    pedir(`/api/grupos/${grupoId}/guia`, {
      method: "POST",
      body: JSON.stringify({ enfoque }),
    }),

  // — Borrado y limpieza —
  // Todas responden `{ borrado: {...}, detalle }` para poder decirle al profesor
  // exactamente qué se fue en lugar de un "listo" a ciegas.
  borrarMateria: (materiaId) => pedir(`/api/materias/${materiaId}`, { method: "DELETE" }),
  borrarTemario: (materiaId) =>
    pedir(`/api/materias/${materiaId}/temario`, { method: "DELETE" }),
  borrarGrupo: (grupoId) => pedir(`/api/grupos/${grupoId}`, { method: "DELETE" }),
  borrarClasesDeGrupo: (grupoId) =>
    pedir(`/api/grupos/${grupoId}/sesiones`, { method: "DELETE" }),
  borrarDudasDeGrupo: (grupoId, alcance = "todo") =>
    pedir(`/api/grupos/${grupoId}/chat?alcance=${alcance}`, { method: "DELETE" }),
  borrarClase: (sesionId) => pedir(`/api/sesiones/${sesionId}`, { method: "DELETE" }),
  borrarTranscripcion: (sesionId) =>
    pedir(`/api/sesiones/${sesionId}/transcripcion`, { method: "DELETE" }),
  borrarDudasDeClase: (sesionId) => pedir(`/api/sesiones/${sesionId}/chat`, { method: "DELETE" }),
  reabrirClase: (sesionId) => pedir(`/api/sesiones/${sesionId}/reabrir`, { method: "POST" }),
  borrarHorario: () => pedir("/api/profesor/horario", { method: "DELETE" }),
  reiniciar: (conDemo) =>
    pedir("/api/mantenimiento/reiniciar", {
      method: "POST",
      body: JSON.stringify({ con_demo: conDemo }),
    }),
};

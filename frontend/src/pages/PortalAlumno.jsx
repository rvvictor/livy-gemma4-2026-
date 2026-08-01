// Portal del alumno. Solo lectura de lo que se vio en SU grupo, más un chat que
// responde con las clases de su propio profesor —no con internet genérico— y que
// no se adelanta al punto donde va su sección.
import { useEffect, useRef, useState } from "react";

import { Aviso, Cargando, Encabezado, TextoRico } from "../components/ui.jsx";
import { useMateria } from "../estado.jsx";
import { api } from "../lib/api.js";

export default function PortalAlumno() {
  const { materia } = useMateria();
  const [grupoId, setGrupoId] = useState(null);
  const [datos, setDatos] = useState(null);
  const [mensajes, setMensajes] = useState([]);
  const [pregunta, setPregunta] = useState("");
  const [pensando, setPensando] = useState(false);
  const [guia, setGuia] = useState(null);
  const [generandoGuia, setGenerandoGuia] = useState(false);
  const [error, setError] = useState(null);
  const finConversacion = useRef(null);

  useEffect(() => {
    if (!materia?.grupos?.length) return;
    setGrupoId((actual) => actual ?? materia.grupos[0].id);
  }, [materia]);

  useEffect(() => {
    if (!grupoId) return;
    setDatos(null);
    setGuia(null);
    setError(null);
    Promise.all([api.clases(grupoId), api.historialChat(grupoId)])
      .then(([clases, historial]) => {
        setDatos(clases);
        setMensajes(historial);
      })
      .catch((fallo) => setError(fallo.message));
  }, [grupoId]);

  useEffect(() => {
    finConversacion.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensajes, pensando]);

  async function preguntar(evento) {
    evento.preventDefault();
    const texto = pregunta.trim();
    if (!texto || pensando) return;

    setMensajes((previos) => [...previos, { rol: "alumno", contenido: texto }]);
    setPregunta("");
    setPensando(true);
    setError(null);
    try {
      const respuesta = await api.preguntar(grupoId, texto);
      setMensajes((previos) => [...previos, { rol: "asistente", contenido: respuesta.respuesta }]);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setPensando(false);
    }
  }

  async function pedirGuia() {
    setGenerandoGuia(true);
    setError(null);
    try {
      const respuesta = await api.guia(grupoId, "repaso de todo lo visto hasta ahora");
      setGuia(respuesta.guia);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setGenerandoGuia(false);
    }
  }

  if (!materia) return <Cargando />;

  return (
    <div className="space-y-6">
      <Encabezado
        titulo="Portal del alumno"
        descripcion="Lo que se vio en tu grupo, en las palabras de tu propio profesor. Si faltaste, aquí está la clase."
        acciones={
          <select
            className="rounded-md border border-borde bg-blanco px-3 py-2 text-sm
                       focus:border-guinda focus:outline-none"
            value={grupoId ?? ""}
            onChange={(evento) => setGrupoId(Number(evento.target.value))}
          >
            {materia.grupos.map((grupo) => (
              <option key={grupo.id} value={grupo.id}>
                Grupo {grupo.nombre}
              </option>
            ))}
          </select>
        }
      />

      {error && <Aviso tipo="error">{error}</Aviso>}
      {!datos ? (
        <Cargando texto="Abriendo tus clases…" />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
          <section className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-tinta">
                {datos.clases.length} clases registradas
              </h2>
              <button className="boton-secundario" onClick={pedirGuia} disabled={generandoGuia}>
                {generandoGuia ? "Gemma está armando la guía…" : "Generar guía de estudio"}
              </button>
            </div>

            {guia && (
              <article className="tarjeta border-guinda-600/30 bg-nieve/40">
                <p className="etiqueta mb-2">Guía de estudio</p>
                <TextoRico contenido={guia} />
              </article>
            )}

            {datos.clases.length === 0 && (
              <Aviso>Todavía no hay clases registradas para este grupo.</Aviso>
            )}

            {datos.clases.map((clase) => (
              <article key={clase.id} className="tarjeta space-y-3">
                <header className="flex flex-wrap items-baseline justify-between gap-2">
                  <h3 className="font-semibold text-tinta">{clase.titulo}</h3>
                  <span className="text-xs text-gris">{clase.fecha}</span>
                </header>
                <p className="text-sm leading-relaxed text-tinta">{clase.resumen}</p>

                {clase.puntos_clave.length > 0 && (
                  <div className="border-t border-borde pt-3">
                    <p className="etiqueta mb-1.5">Lo que hay que llevarse</p>
                    <ul className="space-y-1 text-sm text-tinta">
                      {clase.puntos_clave.map((punto, indice) => (
                        <li key={indice} className="flex gap-2">
                          <span className="text-guinda-600">•</span>
                          {punto}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {clase.donde_quedo && (
                  <p className="rounded-md bg-hueso px-3 py-2 text-xs text-gris">
                    La clase terminó en: {clase.donde_quedo}
                  </p>
                )}
              </article>
            ))}
          </section>

          <aside className="lg:sticky lg:top-6 lg:h-[calc(100vh-8rem)]">
            <div className="tarjeta flex h-full flex-col">
              <header className="border-b border-borde pb-3">
                <h2 className="font-semibold text-tinta">Pregúntale a tus clases</h2>
                <p className="mt-1 text-xs text-gris">
                  Responde con lo que {datos.profesor} enseñó al grupo {datos.grupo}. Si un tema
                  todavía no se ve en tu sección, te lo dice en vez de adelantarse.
                </p>
              </header>

              <div className="flex-1 space-y-3 overflow-y-auto py-4">
                {mensajes.length === 0 && (
                  <p className="text-sm text-gris">
                    Prueba con algo de lo que se vio: «no entendí por qué 0/0 no es una
                    respuesta» o «¿qué me perdí la clase pasada?».
                  </p>
                )}
                {mensajes.map((mensaje, indice) => (
                  <div
                    key={indice}
                    className={
                      mensaje.rol === "alumno"
                        ? "ml-6 rounded-lg bg-guinda px-3 py-2 text-sm text-blanco"
                        : "mr-2 rounded-lg bg-hueso px-3 py-2"
                    }
                  >
                    {mensaje.rol === "alumno" ? (
                      mensaje.contenido
                    ) : (
                      <TextoRico contenido={mensaje.contenido} />
                    )}
                  </div>
                ))}
                {pensando && (
                  <div className="mr-2 rounded-lg bg-hueso px-3 py-2 text-sm text-gris">
                    <span className="latido">Buscando en tus clases…</span>
                  </div>
                )}
                <div ref={finConversacion} />
              </div>

              <form onSubmit={preguntar} className="flex gap-2 border-t border-borde pt-3">
                <input
                  className="flex-1 rounded-md border border-borde px-3 py-2 text-sm
                             focus:border-guinda focus:outline-none"
                  placeholder="Escribe tu duda…"
                  value={pregunta}
                  onChange={(evento) => setPregunta(evento.target.value)}
                />
                <button className="boton-primario px-4" disabled={pensando || !pregunta.trim()}>
                  Enviar
                </button>
              </form>
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}

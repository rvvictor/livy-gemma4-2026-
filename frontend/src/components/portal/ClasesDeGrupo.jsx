// Listado de clases de una sección.
//
// Las tarjetas van deliberadamente escuetas —fecha, título, adelanto y en qué
// terminó la sesión— porque el detalle vive en la página propia de cada clase.
//
// El costado cambia según quién mira: el alumno tiene el chat de dudas globales
// sobre todo el curso; el profesor, el registro de lo que ese grupo preguntó.
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Aparece, Aviso, Encabezado, Esqueleto } from "../ui.jsx";
import { PanelChat, PanelDudas, Regresar, VistaGuia } from "./piezas.jsx";
import { api } from "../../lib/api.js";

const SUGERENCIAS = [
  "¿Qué me perdí la clase pasada?",
  "¿Dónde vamos del temario?",
  "Explícame otra vez lo último que vimos",
];

function fechaLarga(iso) {
  return new Date(`${iso}T12:00:00`).toLocaleDateString("es-MX", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
}

export default function ClasesDeGrupo({ modo, base }) {
  const { grupoId } = useParams();
  const esProfesor = modo === "profesor";

  const [datos, setDatos] = useState(null);
  const [dudas, setDudas] = useState([]);
  const [mensajes, setMensajes] = useState([]);
  const [pensando, setPensando] = useState(false);
  const [guia, setGuia] = useState(null);
  const [generando, setGenerando] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setDatos(null);
    setGuia(null);
    setError(null);

    const lateral = esProfesor
      ? api.dudas(grupoId, "general")
      : api.historialChat(grupoId);

    Promise.all([api.clases(grupoId), lateral])
      .then(([clases, secundario]) => {
        setDatos(clases);
        if (esProfesor) setDudas(secundario);
        else setMensajes(secundario);
      })
      .catch((fallo) => setError(fallo.message));
  }, [grupoId, esProfesor]);

  async function preguntar(texto) {
    setMensajes((previos) => [...previos, { rol: "alumno", contenido: texto }]);
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

  async function generarGuia() {
    setGenerando(true);
    setError(null);
    try {
      const respuesta = await api.guia(grupoId, "repaso de todo lo visto hasta ahora");
      setGuia(respuesta.guia);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setGenerando(false);
    }
  }

  if (error && !datos) return <Aviso tipo="error">{error}</Aviso>;
  if (!datos) return <Esqueleto filas={4} />;

  if (guia) {
    return (
      <VistaGuia
        guia={guia}
        materia={datos.materia}
        grupo={datos.grupo}
        profesor={datos.profesor}
        onCerrar={() => setGuia(null)}
      />
    );
  }

  return (
    <div>
      <div className="mb-4">
        <Regresar a={base}>
          {esProfesor ? "Todas las secciones" : "Mis materias"}
        </Regresar>
      </div>

      <Encabezado
        titulo={datos.materia}
        descripcion={`Grupo ${datos.grupo} · ${datos.profesor} · ${datos.horario}`}
        acciones={
          <button className="boton-primario" onClick={generarGuia} disabled={generando}>
            {generando ? "Gemma está armando la guía…" : "Generar guía de estudio"}
          </button>
        }
      />

      {error && <Aviso tipo="error">{error}</Aviso>}

      <div className="grid gap-8 lg:grid-cols-[1fr_330px]">
        <section className="space-y-3">
          <h2 className="text-sm font-semibold text-gris">
            {datos.clases.length} {datos.clases.length === 1 ? "clase" : "clases"}
          </h2>

          {datos.clases.length === 0 && (
            <Aviso>Todavía no hay clases registradas para este grupo.</Aviso>
          )}

          {datos.clases.map((clase, indice) => (
            <Aparece key={clase.id} retraso={indice * 60}>
              <Link
                to={`${base}/clase/${clase.id}`}
                className="group block rounded-2xl border border-borde bg-blanco p-5 transition-all
                           duration-300 hover:-translate-y-0.5 hover:border-guinda-300
                           hover:shadow-[0_8px_30px_-12px_rgba(109,26,54,0.25)]"
              >
                <p className="text-sm font-semibold uppercase tracking-wide text-guinda">
                  {fechaLarga(clase.fecha)}
                </p>
                <h3 className="mt-1.5 text-lg font-semibold leading-snug text-tinta">
                  {clase.titulo}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-gris">{clase.adelanto}…</p>

                {clase.donde_quedo && (
                  <p className="mt-3 border-t border-borde pt-3 text-xs text-gris">
                    <span className="font-medium text-guinda-900">Terminó en:</span>{" "}
                    {clase.donde_quedo}
                  </p>
                )}

                <span className="mt-3 inline-block text-sm font-medium text-rojo opacity-0 transition-opacity duration-200 group-hover:opacity-100">
                  Abrir la clase →
                </span>
              </Link>
            </Aparece>
          ))}
        </section>

        <aside className="lg:sticky lg:top-24 lg:h-[calc(100vh-9rem)] lg:self-start">
          <Aparece retraso={120} className="h-full">
            {esProfesor ? (
              <PanelDudas
                dudas={dudas}
                titulo="Lo que pregunta tu grupo"
                descripcion={`Dudas de ${datos.grupo} sobre el curso en general. Las de cada clase están dentro de su propia sesión.`}
              />
            ) : (
              <PanelChat
                titulo="Pregunta sobre el curso"
                descripcion={`Livy responde con las ${datos.clases.length} clases que ${datos.profesor} le dio a tu grupo. Para dudas de una clase concreta, ábrela y pregunta ahí.`}
                mensajes={mensajes}
                pensando={pensando}
                onEnviar={preguntar}
                sugerencias={SUGERENCIAS}
              />
            )}
          </Aparece>
        </aside>
      </div>
    </div>
  );
}

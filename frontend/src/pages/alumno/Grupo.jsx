// Listado de clases de una sección.
//
// Las tarjetas van deliberadamente escuetas —título, fecha y en qué terminó la
// sesión— porque el detalle vive en la página propia de cada clase. Al costado,
// en lugar de un chat, están las dudas que ya preguntaron los compañeros: le
// dice al alumno que no es el único atorado y al profesor dónde falló la
// explicación.
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Aparece, Aviso, Encabezado, Esqueleto, TextoRico } from "../../components/ui.jsx";
import { api } from "../../lib/api.js";

function fechaLarga(iso) {
  return new Date(`${iso}T12:00:00`).toLocaleDateString("es-MX", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
}

export default function GrupoAlumno() {
  const { grupoId } = useParams();
  const [datos, setDatos] = useState(null);
  const [dudas, setDudas] = useState([]);
  const [guia, setGuia] = useState(null);
  const [generando, setGenerando] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setDatos(null);
    setGuia(null);
    Promise.all([api.clases(grupoId), api.dudas(grupoId)])
      .then(([clases, listaDudas]) => {
        setDatos(clases);
        setDudas(listaDudas);
      })
      .catch((fallo) => setError(fallo.message));
  }, [grupoId]);

  async function pedirGuia() {
    setGenerando(true);
    setError(null);
    try {
      const respuesta = await api.guia(grupoId, "repaso de todo lo visto hasta ahora");
      setGuia(respuesta.guia);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setGenerando(false);
    }
  }

  if (error && !datos) return <Aviso tipo="error">{error}</Aviso>;
  if (!datos) return <Esqueleto filas={4} />;

  return (
    <div>
      <Encabezado
        titulo={datos.materia}
        descripcion={`Grupo ${datos.grupo} · ${datos.profesor} · ${datos.horario}`}
        acciones={
          <>
            <Link to={`/alumno/${grupoId}/chat`} className="boton-primario">
              Preguntar sobre el curso
            </Link>
            <button className="boton-secundario" onClick={pedirGuia} disabled={generando}>
              {generando ? "Armando la guía…" : "Guía de estudio"}
            </button>
          </>
        }
      />

      {error && <Aviso tipo="error">{error}</Aviso>}

      {guia && (
        <Aparece className="mb-8">
          <article className="tarjeta border-guinda-600/25 bg-nieve/30">
            <p className="etiqueta mb-2">Guía de estudio · generada con Gemma 4</p>
            <TextoRico contenido={guia} />
          </article>
        </Aparece>
      )}

      <div className="grid gap-8 lg:grid-cols-[1fr_290px]">
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
                to={`/alumno/clase/${clase.id}`}
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

        <aside className="lg:sticky lg:top-24 lg:self-start">
          <Aparece retraso={120}>
            <div className="tarjeta">
              <p className="etiqueta">Lo que pregunta tu grupo</p>
              <p className="mt-1 text-xs text-gris">
                Dudas reales de {datos.grupo}. Si te suena alguna, no eres el único.
              </p>

              <div className="mt-4 space-y-3">
                {dudas.length === 0 && (
                  <p className="text-sm text-gris">
                    Nadie ha preguntado nada todavía. Puedes ser el primero.
                  </p>
                )}
                {dudas.slice(0, 8).map((duda, indice) => (
                  <Aparece
                    key={duda.id}
                    retraso={160 + indice * 60}
                    className="border-l-2 border-nieve pl-3 transition-colors hover:border-guinda"
                  >
                    <p className="text-sm leading-snug text-tinta">{duda.contenido}</p>
                    {duda.clase ? (
                      <Link
                        to={`/alumno/clase/${duda.sesion_id}`}
                        className="mt-1 inline-block text-xs text-gris subraya-hover hover:text-guinda"
                      >
                        {duda.clase}
                      </Link>
                    ) : (
                      <span className="mt-1 inline-block text-xs text-gris">
                        Sobre el curso en general
                      </span>
                    )}
                  </Aparece>
                ))}
              </div>
            </div>
          </Aparece>
        </aside>
      </div>
    </div>
  );
}

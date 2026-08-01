// Una clase, con su propia dirección.
//
// Cada sesión tiene liga propia (/alumno/clase/:id) para que se pueda compartir
// entre compañeros: "lo que faltaste es esto". Trae el resumen extenso, el botón
// de transcripción en el encabezado —lo que se dijo, tal cual— y un chat acotado
// a esta sesión, que no se mezcla con el resto del semestre.
import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  Aparece,
  Aviso,
  Burbuja,
  Escribiendo,
  Esqueleto,
  TextoRico,
} from "../../components/ui.jsx";
import { api } from "../../lib/api.js";

function fechaLarga(iso) {
  return new Date(`${iso}T12:00:00`).toLocaleDateString("es-MX", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export default function ClaseAlumno() {
  const { sesionId } = useParams();
  const [clase, setClase] = useState(null);
  const [vista, setVista] = useState("resumen"); // resumen | transcripcion
  const [mensajes, setMensajes] = useState([]);
  const [pregunta, setPregunta] = useState("");
  const [pensando, setPensando] = useState(false);
  const [error, setError] = useState(null);
  const finChat = useRef(null);

  useEffect(() => {
    setClase(null);
    setVista("resumen");
    Promise.all([api.clase(sesionId), api.historialChatClase(sesionId)])
      .then(([detalle, historial]) => {
        setClase(detalle);
        setMensajes(historial);
      })
      .catch((fallo) => setError(fallo.message));
  }, [sesionId]);

  useEffect(() => {
    finChat.current?.scrollIntoView({ behavior: "smooth", block: "end" });
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
      const respuesta = await api.preguntarSobreClase(sesionId, texto);
      setMensajes((previos) => [...previos, { rol: "asistente", contenido: respuesta.respuesta }]);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setPensando(false);
    }
  }

  if (error && !clase) return <Aviso tipo="error">{error}</Aviso>;
  if (!clase) return <Esqueleto filas={4} />;

  return (
    <div>
      {/* ── Encabezado de la clase ── */}
      <Aparece className="mb-7 border-b border-borde pb-5">
        <div className="flex flex-wrap items-center gap-2 text-xs text-gris">
          <Link
            to={`/alumno/${clase.grupo_id}`}
            className="subraya-hover hover:text-guinda"
          >
            {clase.materia} · {clase.grupo}
          </Link>
          <span>›</span>
          <span>
            Clase {clase.numero} de {clase.total}
          </span>
        </div>

        <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-guinda">
              {fechaLarga(clase.fecha)}
            </p>
            <h1 className="mt-1 text-[26px] font-semibold leading-tight tracking-tight text-tinta">
              {clase.titulo}
            </h1>
            <p className="mt-1.5 text-sm text-gris">
              {clase.profesor}
              {clase.duracion_min ? ` · ${clase.duracion_min} minutos` : ""}
            </p>
          </div>

          <div className="flex gap-1 rounded-full border border-borde bg-blanco p-1">
            {[
              ["resumen", "Resumen"],
              ["transcripcion", "Transcripción"],
            ].map(([clave, etiqueta]) => (
              <button
                key={clave}
                onClick={() => setVista(clave)}
                className={`rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors duration-200 ${
                  vista === clave ? "bg-guinda text-blanco" : "text-gris hover:text-guinda"
                }`}
              >
                {etiqueta}
              </button>
            ))}
          </div>
        </div>
      </Aparece>

      {error && (
        <div className="mb-4">
          <Aviso tipo="error">{error}</Aviso>
        </div>
      )}

      <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
        <section>
          {vista === "resumen" ? (
            <Aparece className="space-y-6">
              <article className="tarjeta">
                <TextoRico contenido={clase.resumen} className="text-[15px] leading-[1.8]" />
              </article>

              {clase.puntos_clave.length > 0 && (
                <article className="tarjeta">
                  <p className="etiqueta mb-3">Lo que hay que llevarse</p>
                  <ul className="space-y-2 text-[15px] text-tinta">
                    {clase.puntos_clave.map((punto, indice) => (
                      <Aparece
                        key={indice}
                        como="li"
                        retraso={indice * 70}
                        className="flex gap-2.5"
                      >
                        <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-guinda" />
                        {punto}
                      </Aparece>
                    ))}
                  </ul>
                </article>
              )}

              <div className="grid gap-4 sm:grid-cols-2">
                {clase.donde_quedo && (
                  <article className="tarjeta bg-hueso">
                    <p className="etiqueta mb-1.5">La clase terminó en</p>
                    <p className="text-sm leading-relaxed text-guinda-900">{clase.donde_quedo}</p>
                  </article>
                )}
                {clase.pendientes.length > 0 && (
                  <article className="tarjeta bg-hueso">
                    <p className="etiqueta mb-1.5">Quedó pendiente</p>
                    <ul className="space-y-1 text-sm text-tinta">
                      {clase.pendientes.map((pendiente, indice) => (
                        <li key={indice}>· {pendiente}</li>
                      ))}
                    </ul>
                  </article>
                )}
              </div>
            </Aparece>
          ) : (
            <Aparece className="tarjeta">
              <div className="mb-4 flex items-baseline justify-between border-b border-borde pb-3">
                <p className="etiqueta">Lo que se dijo en clase</p>
                <span className="text-xs text-gris">
                  {clase.transcripcion.length} caracteres
                </span>
              </div>
              {clase.transcripcion ? (
                <p className="whitespace-pre-line text-[15px] leading-[1.9] text-tinta">
                  {clase.transcripcion}
                </p>
              ) : (
                <p className="text-sm text-gris">Esta sesión no tiene transcripción guardada.</p>
              )}
            </Aparece>
          )}

          {/* Navegación entre sesiones */}
          <div className="mt-8 flex items-center justify-between border-t border-borde pt-5">
            {clase.anterior ? (
              <Link to={`/alumno/clase/${clase.anterior}`} className="boton-secundario">
                ← Clase anterior
              </Link>
            ) : (
              <span />
            )}
            {clase.siguiente ? (
              <Link to={`/alumno/clase/${clase.siguiente}`} className="boton-secundario">
                Clase siguiente →
              </Link>
            ) : (
              <span className="text-xs text-gris">Es la clase más reciente</span>
            )}
          </div>
        </section>

        {/* ── Chat acotado a esta clase ── */}
        <aside className="lg:sticky lg:top-24 lg:h-[calc(100vh-9rem)] lg:self-start">
          <div className="tarjeta flex h-full flex-col">
            <header className="border-b border-borde pb-3">
              <h2 className="font-semibold text-tinta">Pregunta sobre esta clase</h2>
              <p className="mt-1 text-xs leading-relaxed text-gris">
                Responde solo con lo que se vio el {fechaLarga(clase.fecha).split(",")[0]}. Para
                dudas de todo el curso,{" "}
                <Link
                  to={`/alumno/${clase.grupo_id}/chat`}
                  className="text-guinda subraya-hover"
                >
                  usa el chat general
                </Link>
                .
              </p>
            </header>

            <div className="flex-1 space-y-3 overflow-y-auto py-4">
              {mensajes.length === 0 && (
                <p className="text-sm leading-relaxed text-gris">
                  Prueba con algo de esta sesión: «no entendí la parte del final» o «dame otro
                  ejemplo de lo que explicó».
                </p>
              )}
              {mensajes.map((mensaje, indice) => (
                <Burbuja key={indice} rol={mensaje.rol}>
                  {mensaje.rol === "alumno" ? (
                    mensaje.contenido
                  ) : (
                    <TextoRico contenido={mensaje.contenido} />
                  )}
                </Burbuja>
              ))}
              {pensando && <Escribiendo texto="Buscando en esta clase" />}
              <div ref={finChat} />
            </div>

            <form onSubmit={preguntar} className="flex items-end gap-2 border-t border-borde pt-3">
              <input
                className="campo rounded-full"
                placeholder="Tu duda sobre esta clase…"
                value={pregunta}
                onChange={(evento) => setPregunta(evento.target.value)}
              />
              <button
                className="boton-primario h-10 w-10 shrink-0 rounded-full p-0"
                disabled={pensando || !pregunta.trim()}
                aria-label="Enviar"
              >
                ↑
              </button>
            </form>
          </div>
        </aside>
      </div>
    </div>
  );
}

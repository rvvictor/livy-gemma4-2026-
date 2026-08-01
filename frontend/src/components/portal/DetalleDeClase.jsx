// Una clase, con su propia dirección.
//
// Cada sesión tiene liga propia para que se pueda compartir entre compañeros:
// "lo que faltaste es esto". El encabezado alterna entre el resumen extenso y la
// transcripción literal de lo que se dijo.
//
// El costado cambia según quién mira: el alumno tiene un chat acotado a esta
// sesión —no se mezcla con el resto del semestre— y el profesor ve lo que se
// preguntó sobre esta clase en particular.
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { Aparece, Aviso, Esqueleto, TextoRico, useConfirmacion } from "../ui.jsx";
import { PanelChat, PanelDudas, Regresar } from "./piezas.jsx";
import { useCicloOpcional } from "../../estado.jsx";
import { api } from "../../lib/api.js";

const SUGERENCIAS = [
  "No entendí la parte del final",
  "Dame otro ejemplo de lo que explicó",
];

function fechaLarga(iso) {
  return new Date(`${iso}T12:00:00`).toLocaleDateString("es-MX", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export default function DetalleDeClase({ modo, base }) {
  const { sesionId } = useParams();
  const esProfesor = modo === "profesor";
  const navegar = useNavigate();

  const [clase, setClase] = useState(null);
  const [vista, setVista] = useState("resumen"); // resumen | transcripcion
  const [dudas, setDudas] = useState([]);
  const [mensajes, setMensajes] = useState([]);
  const [pensando, setPensando] = useState(false);
  const [error, setError] = useState(null);
  const [aviso, setAviso] = useState(null);

  const ciclo = useCicloOpcional(); // solo existe dentro de la vista del profesor
  const { pedir, dialogo } = useConfirmacion();

  useEffect(() => {
    setClase(null);
    setVista("resumen");
    setError(null);

    const lateral = esProfesor
      ? api.dudasDeClase(sesionId)
      : api.historialChatClase(sesionId);

    Promise.all([api.clase(sesionId), lateral])
      .then(([detalle, secundario]) => {
        setClase(detalle);
        if (esProfesor) setDudas(secundario);
        else setMensajes(secundario);
      })
      .catch((fallo) => setError(fallo.message));
  }, [sesionId, esProfesor]);

  async function preguntar(texto) {
    setMensajes((previos) => [...previos, { rol: "alumno", contenido: texto }]);
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

  /**
   * Lanza un borrado sobre esta clase.
   *
   * `salir` marca las acciones tras las cuales la página ya no puede existir:
   * borrarla o reabrirla la saca del portal —solo se publican las clases
   * cerradas— así que hay que devolver al profesor al listado del grupo.
   */
  function borrar(peticion, llamada, { salir = false } = {}) {
    const grupoId = clase.grupo_id;
    pedir({
      ...peticion,
      accion: async () => {
        setError(null);
        setAviso(null);
        try {
          const respuesta = await llamada();
          await ciclo?.recargar();
          if (salir) {
            navegar(`${base}/${grupoId}`, { state: { aviso: respuesta.detalle } });
            return;
          }
          const [detalle, nuevasDudas] = await Promise.all([
            api.clase(sesionId),
            api.dudasDeClase(sesionId),
          ]);
          setClase(detalle);
          setDudas(nuevasDudas);
          setAviso(respuesta.detalle);
        } catch (fallo) {
          setError(fallo.message);
        }
      },
    });
  }

  if (error && !clase) return <Aviso tipo="error">{error}</Aviso>;
  if (!clase) return <Esqueleto filas={4} />;

  return (
    <div>
      <div className="mb-4">
        <Regresar a={`${base}/${clase.grupo_id}`}>
          {clase.materia} · {clase.grupo}
        </Regresar>
      </div>

      <Aparece className="mb-7 border-b border-borde pb-5">
        <p className="text-xs text-gris">
          Clase {clase.numero} de {clase.total}
        </p>

        <div className="mt-2 flex flex-wrap items-end justify-between gap-4">
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

      {/* Controles de mantenimiento de la sesión. Van aparte y en tono discreto:
          son de uso raro y ninguno se puede deshacer. */}
      {esProfesor && (
        <Aparece className="mb-6 flex flex-wrap items-center gap-2 rounded-xl border border-borde bg-hueso px-4 py-2.5">
          <span className="mr-auto text-xs text-gris">
            Estos controles no los ven tus alumnos.
          </span>

          <button
            className="enlace-peligro"
            disabled={!clase.transcripcion}
            onClick={() =>
              borrar(
                {
                  titulo: "Borrar la transcripción",
                  cuerpo: `Se eliminan los ${clase.transcripcion.length} caracteres de lo que se dijo en el salón.`,
                  consecuencias: [
                    "Livy dejará de poder citar textualmente esta clase",
                    "Las respuestas sobre esta sesión se apoyarán solo en el resumen",
                  ],
                  conserva: [
                    "El resumen, los puntos clave y el avance se quedan",
                    "La clase sigue publicada para tus alumnos",
                  ],
                  confirmar: "Borrar la transcripción",
                },
                () => api.borrarTranscripcion(sesionId),
              )
            }
          >
            Borrar transcripción
          </button>

          <button
            className="enlace-peligro"
            disabled={!clase.transcripcion}
            onClick={() =>
              borrar(
                {
                  titulo: "Volver a generar la memoria",
                  cuerpo:
                    "La clase se reabre y Gemma podrá resumirla otra vez sobre la misma transcripción. Es lo que se hace cuando el resumen salió mal o marcó temas que no se tocaron.",
                  consecuencias: [
                    "Se pierde el resumen actual y los temas que marcó",
                    "El avance de la sección baja hasta que la vuelvas a cerrar",
                    "La clase sale del portal de alumnos mientras esté abierta",
                  ],
                  conserva: ["La transcripción se conserva íntegra"],
                  confirmar: "Reabrir la clase",
                },
                () => api.reabrirClase(sesionId),
                { salir: true },
              )
            }
          >
            Volver a generar la memoria
          </button>

          <button
            className="enlace-peligro"
            onClick={() =>
              borrar(
                {
                  titulo: "Borrar esta clase",
                  cuerpo: `Se elimina «${clase.titulo}» del ${fechaLarga(clase.fecha)}.`,
                  consecuencias: [
                    "Se pierden el resumen y la transcripción",
                    "Los temas que cubrió dejan de contar en el avance de la sección",
                    "Se pierden las dudas que se preguntaron sobre ella",
                  ],
                  confirmar: "Borrar la clase",
                },
                () => api.borrarClase(sesionId),
                { salir: true },
              )
            }
          >
            Borrar la clase
          </button>
        </Aparece>
      )}

      {error && (
        <div className="mb-4">
          <Aviso tipo="error">{error}</Aviso>
        </div>
      )}
      {aviso && (
        <div className="mb-4">
          <Aviso tipo="alerta">{aviso}</Aviso>
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
                      <Aparece key={indice} como="li" retraso={indice * 70} className="flex gap-2.5">
                        <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-guinda" />
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
                <span className="text-xs text-gris">{clase.transcripcion.length} caracteres</span>
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

          <div className="mt-8 flex items-center justify-between border-t border-borde pt-5">
            {clase.anterior ? (
              <Link to={`${base}/clase/${clase.anterior}`} className="boton-secundario">
                ← Clase anterior
              </Link>
            ) : (
              <span />
            )}
            {clase.siguiente ? (
              <Link to={`${base}/clase/${clase.siguiente}`} className="boton-secundario">
                Clase siguiente →
              </Link>
            ) : (
              <span className="text-xs text-gris">Es la clase más reciente</span>
            )}
          </div>
        </section>

        <aside className="lg:sticky lg:top-24 lg:h-[calc(100vh-9rem)] lg:self-start">
          {esProfesor ? (
            <PanelDudas
              dudas={dudas}
              titulo="Dudas sobre esta clase"
              descripcion={`Lo que ${clase.grupo} preguntó específicamente de esta sesión.`}
              onBorrar={() =>
                borrar(
                  {
                    titulo: "Borrar las dudas de esta clase",
                    cuerpo: `Se elimina lo que ${clase.grupo} preguntó sobre esta sesión.`,
                    consecuencias: ["Se pierde el rastro de qué no quedó claro ese día"],
                    conserva: ["Las dudas generales del curso se quedan"],
                    confirmar: "Borrar las dudas",
                  },
                  () => api.borrarDudasDeClase(sesionId),
                )
              }
            />
          ) : (
            <PanelChat
              titulo="Pregunta sobre esta clase"
              descripcion="Responde solo con lo que se vio en esta sesión. Para dudas de todo el curso, regresa al listado y usa el chat de ahí."
              mensajes={mensajes}
              pensando={pensando}
              onEnviar={preguntar}
              sugerencias={SUGERENCIAS}
              textoPensando="Buscando en esta clase"
              marcador="Tu duda sobre esta clase…"
            />
          )}
        </aside>
      </div>

      {dialogo}
    </div>
  );
}

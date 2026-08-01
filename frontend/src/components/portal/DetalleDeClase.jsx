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
import { Link, useParams } from "react-router-dom";

import { Aparece, Aviso, Esqueleto, TextoRico } from "../ui.jsx";
import { PanelChat, PanelDudas, Regresar } from "./piezas.jsx";
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

  const [clase, setClase] = useState(null);
  const [vista, setVista] = useState("resumen"); // resumen | transcripcion
  const [dudas, setDudas] = useState([]);
  const [mensajes, setMensajes] = useState([]);
  const [pensando, setPensando] = useState(false);
  const [error, setError] = useState(null);

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
    </div>
  );
}

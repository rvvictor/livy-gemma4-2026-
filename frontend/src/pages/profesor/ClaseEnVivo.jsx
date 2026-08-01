// Clase en vivo, en formato conversación.
//
// El profesor no quiere un formulario mientras da clase: quiere una superficie
// que escuche y a la que pueda preguntarle algo de reojo. Por eso todo pasa por
// un hilo único —eventos, preguntas al modelo y la memoria final— y todos los
// controles viven en la barra de abajo, al alcance del pulgar.
import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation } from "react-router-dom";

import {
  Aparece,
  Aviso,
  BarraAvance,
  Burbuja,
  Escribiendo,
  Esqueleto,
  TextoRico,
  useConfirmacion,
} from "../../components/ui.jsx";
import { useCiclo } from "../../estado.jsx";
import { api } from "../../lib/api.js";
import { crearDictado, soportaDictado } from "../../lib/speech.js";

// Los fragmentos se agrupan antes de subirlos: una petición por frase saturaría
// la red sin ganar nada, porque el resumen ocurre hasta el cierre.
const MS_ENTRE_ENVIOS = 8000;

export default function ClaseEnVivo() {
  const { ciclo, recargar } = useCiclo();
  const ubicacion = useLocation();
  const { pedir, dialogo } = useConfirmacion();

  const [grupoId, setGrupoId] = useState(ubicacion.state?.grupoId ?? null);
  const [sesion, setSesion] = useState(null);
  const [hilo, setHilo] = useState([]);
  const [transcripcion, setTranscripcion] = useState("");
  const [parcial, setParcial] = useState("");
  const [grabando, setGrabando] = useState(false);
  const [segundos, setSegundos] = useState(0);
  const [vista, setVista] = useState("hilo"); // hilo | transcripcion
  const [borrador, setBorrador] = useState("");
  const [consultando, setConsultando] = useState(false);
  const [cerrando, setCerrando] = useState(false);
  const [error, setError] = useState(null);

  const dictadoRef = useRef(null);
  const pendienteRef = useRef("");
  const sesionRef = useRef(null);
  const finHilo = useRef(null);

  const grupos = useMemo(
    () =>
      (ciclo?.materias || []).flatMap((materia) =>
        materia.grupos.map((grupo) => ({ ...grupo, materia: materia.nombre })),
      ),
    [ciclo],
  );
  const grupo = grupos.find((g) => g.grupo_id === grupoId) || grupos[0];

  useEffect(() => {
    if (!grupoId && grupos.length) setGrupoId(grupos[0].grupo_id);
  }, [grupos, grupoId]);

  useEffect(() => {
    if (!grabando) return undefined;
    const reloj = setInterval(() => setSegundos((valor) => valor + 1), 1000);
    return () => clearInterval(reloj);
  }, [grabando]);

  useEffect(() => {
    if (!grabando) return undefined;
    const envio = setInterval(vaciarPendiente, MS_ENTRE_ENVIOS);
    return () => clearInterval(envio);
  }, [grabando]);

  useEffect(() => () => dictadoRef.current?.detener(), []);

  useEffect(() => {
    finHilo.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [hilo, consultando, vista]);

  function agregar(tipo, contenido, extra = {}) {
    setHilo((previo) => [...previo, { tipo, contenido, ...extra, id: crypto.randomUUID() }]);
  }

  async function vaciarPendiente() {
    const texto = pendienteRef.current.trim();
    if (!texto || !sesionRef.current) return;
    pendienteRef.current = "";
    try {
      await api.enviarFragmento(sesionRef.current.id, texto);
    } catch (fallo) {
      pendienteRef.current = `${texto} ${pendienteRef.current}`.trim();
      setError(`No se pudo guardar un fragmento: ${fallo.message}`);
    }
  }

  async function iniciar() {
    setError(null);
    if (!soportaDictado()) {
      setError("Este navegador no soporta dictado. Usa Chrome o Edge para la clase en vivo.");
      return;
    }
    try {
      const nueva = await api.iniciarSesion(grupoId);
      sesionRef.current = nueva;
      setSesion(nueva);
      setTranscripcion(nueva.transcripcion || "");
      setSegundos(0);
      setHilo([]);
      agregar("sistema", `Clase abierta con ${grupo.grupo}. Livy está escuchando.`);

      dictadoRef.current = crearDictado({
        onParcial: setParcial,
        onFinal: (texto) => {
          pendienteRef.current = `${pendienteRef.current} ${texto}`.trim();
          setTranscripcion((previa) => `${previa} ${texto}`.trim());
          setParcial("");
        },
        onError: (motivo) =>
          setError(
            motivo === "not-allowed"
              ? "El navegador bloqueó el micrófono. Permite el acceso y vuelve a iniciar."
              : `Error de dictado: ${motivo}`,
          ),
      });
      dictadoRef.current.iniciar();
      setGrabando(true);
    } catch (fallo) {
      setError(fallo.message);
    }
  }

  async function preguntar(evento) {
    evento?.preventDefault();
    const pregunta = borrador.trim();
    if (!pregunta || !sesion || consultando) return;

    setBorrador("");
    agregar("profesor", pregunta);
    setConsultando(true);
    setVista("hilo");
    try {
      await vaciarPendiente();
      const respuesta = await api.consultarEnVivo(sesion.id, pregunta);
      agregar("livy", respuesta.respuesta);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setConsultando(false);
    }
  }

  /**
   * Tira la sesión abierta sin resumirla.
   *
   * Es la salida de la prueba de micrófono y del arranque en falso: sin esto,
   * cada ensayo dejaría una sesión a medias colgada del grupo, que la agenda
   * seguiría mostrando como "en curso" para siempre.
   */
  function descartar() {
    pedir({
      titulo: `Descartar la clase con ${grupo?.grupo ?? "este grupo"}`,
      cuerpo: "Se tira la sesión abierta sin convertirla en memoria.",
      consecuencias: [
        transcripcion
          ? `Se pierden los ${transcripcion.length} caracteres dictados`
          : "Se elimina la sesión que quedó abierta",
        "El grupo no avanza: no se registra ningún tema",
      ],
      conserva: ["El avance y las clases anteriores del grupo no se tocan"],
      confirmar: "Descartar la clase",
      accion: async () => {
        dictadoRef.current?.detener();
        setGrabando(false);
        setParcial("");
        setError(null);
        try {
          await api.borrarClase(sesion.id);
          pendienteRef.current = "";
          sesionRef.current = null;
          setSesion(null);
          setTranscripcion("");
          setSegundos(0);
          setHilo([]);
          await recargar();
        } catch (fallo) {
          setError(fallo.message);
        }
      },
    });
  }

  async function cerrar() {
    dictadoRef.current?.detener();
    setGrabando(false);
    setParcial("");
    setCerrando(true);
    setError(null);
    setVista("hilo");
    try {
      await vaciarPendiente();
      const respuesta = await api.cerrarSesion(sesion.id, Math.round(segundos / 60));
      agregar("memoria", "", { resultado: respuesta });
      setSesion(null);
      sesionRef.current = null;
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setCerrando(false);
    }
  }

  if (!ciclo) return <Esqueleto filas={4} />;

  const reloj = `${String(Math.floor(segundos / 60)).padStart(2, "0")}:${String(segundos % 60).padStart(2, "0")}`;

  return (
    <div className="flex h-[calc(100vh-11rem)] flex-col">
      {/* ── Contexto de la sesión ── */}
      <Aparece className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-borde pb-4">
        <div className="flex items-center gap-3">
          {grabando && (
            <span className="pulso-grabando inline-block h-2.5 w-2.5 rounded-full bg-rojo" />
          )}
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-tinta">
              {grupo ? `${grupo.materia} · ${grupo.grupo}` : "Clase en vivo"}
            </h1>
            <p className="text-xs text-gris">
              {grupo?.tema_actual
                ? `Quedaron en: ${grupo.tema_actual.titulo}`
                : "Sin sesiones registradas"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {grupo && (
            <div className="hidden w-32 sm:block">
              <BarraAvance valor={grupo.avance} alto="h-1.5" animada={false} />
            </div>
          )}
          <span className="font-mono text-sm tabular-nums text-gris">{reloj}</span>
        </div>
      </Aparece>

      {error && (
        <div className="mb-3">
          <Aviso tipo="error">{error}</Aviso>
        </div>
      )}
      {!soportaDictado() && (
        <div className="mb-3">
          <Aviso tipo="alerta">
            Este navegador no expone la API de dictado. La clase en vivo requiere Chrome o Edge.
          </Aviso>
        </div>
      )}

      {/* ── Hilo o transcripción ── */}
      <div className="flex-1 overflow-y-auto pr-1">
        {vista === "transcripcion" ? (
          <Aparece className="mx-auto max-w-3xl py-2">
            <p className="etiqueta mb-3">Transcripción en vivo</p>
            {transcripcion || parcial ? (
              <p className="text-[15px] leading-[1.85] text-tinta">
                {transcripcion} <span className="text-gris">{parcial}</span>
              </p>
            ) : (
              <p className="text-sm text-gris">
                Todavía no se ha dictado nada. Inicia la clase y habla con normalidad.
              </p>
            )}
            {transcripcion && (
              <p className="mt-6 border-t border-borde pt-3 text-xs text-gris">
                {transcripcion.length} caracteres capturados
              </p>
            )}
          </Aparece>
        ) : (
          <div className="mx-auto max-w-3xl space-y-3 py-2">
            {hilo.length === 0 && (
              <Aparece className="tarjeta">
                <p className="etiqueta mb-2">Antes de empezar</p>
                <p className="text-sm leading-relaxed text-tinta">
                  {grupo?.siguiente_pendiente
                    ? `A ${grupo.grupo} le toca ${grupo.siguiente_pendiente.titulo}.`
                    : "Elige el grupo con el que vas a trabajar."}{" "}
                  Al iniciar, Livy transcribe la sesión y la convierte en memoria estructurada
                  cuando la cierres. Mientras tanto puedes preguntarle cosas sin salirte de la
                  clase.
                </p>
              </Aparece>
            )}

            {hilo.map((elemento) => {
              if (elemento.tipo === "sistema") {
                return (
                  <Aparece key={elemento.id} className="py-1 text-center">
                    <span className="chip bg-hueso text-gris">{elemento.contenido}</span>
                  </Aparece>
                );
              }
              if (elemento.tipo === "profesor") {
                return (
                  <Burbuja key={elemento.id} rol="profesor">
                    {elemento.contenido}
                  </Burbuja>
                );
              }
              if (elemento.tipo === "livy") {
                return (
                  <Burbuja key={elemento.id} rol="asistente">
                    <TextoRico contenido={elemento.contenido} />
                  </Burbuja>
                );
              }
              return <MemoriaDeSesion key={elemento.id} resultado={elemento.resultado} />;
            })}

            {consultando && <Escribiendo />}
            {cerrando && <Escribiendo texto="Gemma está construyendo la memoria de la clase" />}
          </div>
        )}
        <div ref={finHilo} />
      </div>

      {/* ── Barra de control: todo lo que el profesor toca vive aquí ── */}
      <Aparece className="mt-4 rounded-2xl border border-borde bg-blanco p-3 shadow-[0_-4px_24px_-20px_rgba(26,20,22,0.5)]">
        <div className="mb-2.5 flex flex-wrap items-center gap-2">
          <select
            className="rounded-full border border-borde bg-hueso px-3.5 py-1.5 text-sm text-tinta
                       transition-colors hover:border-guinda focus:border-guinda focus:outline-none
                       disabled:opacity-50"
            value={grupoId ?? ""}
            disabled={grabando}
            onChange={(evento) => setGrupoId(Number(evento.target.value))}
          >
            {grupos.map((opcion) => (
              <option key={opcion.grupo_id} value={opcion.grupo_id}>
                {opcion.materia} · {opcion.grupo}
              </option>
            ))}
          </select>

          <div className="flex gap-1 rounded-full border border-borde p-1">
            {[
              ["hilo", "Conversación"],
              ["transcripcion", "Transcripción"],
            ].map(([clave, etiqueta]) => (
              <button
                key={clave}
                onClick={() => setVista(clave)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition-colors duration-200 ${
                  vista === clave ? "bg-guinda text-blanco" : "text-gris hover:text-guinda"
                }`}
              >
                {etiqueta}
              </button>
            ))}
          </div>

          <div className="ml-auto flex items-center gap-2">
            {sesion && (
              <button className="boton-peligro" onClick={descartar} disabled={cerrando}>
                Descartar
              </button>
            )}
            {!grabando ? (
              <button className="boton-primario" onClick={iniciar} disabled={!grupoId || cerrando}>
                Iniciar clase
              </button>
            ) : (
              <button className="boton-primario" onClick={cerrar} disabled={cerrando}>
                {cerrando ? "Generando memoria…" : "Terminar y guardar"}
              </button>
            )}
          </div>
        </div>

        <form onSubmit={preguntar} className="flex items-end gap-2">
          <textarea
            rows={1}
            className="campo max-h-32 min-h-[44px] resize-none rounded-2xl"
            placeholder={
              sesion
                ? "Pregúntale a Livy sin salirte de la clase…"
                : "Inicia la clase para poder preguntarle a Livy"
            }
            value={borrador}
            disabled={!sesion}
            onChange={(evento) => setBorrador(evento.target.value)}
            onKeyDown={(evento) => {
              if (evento.key === "Enter" && !evento.shiftKey) preguntar(evento);
            }}
          />
          <button
            className="boton-primario h-11 w-11 rounded-full p-0 text-lg"
            disabled={!sesion || consultando || !borrador.trim()}
            aria-label="Enviar pregunta"
          >
            ↑
          </button>
        </form>
      </Aparece>

      {dialogo}
    </div>
  );
}

function MemoriaDeSesion({ resultado }) {
  const resumen = resultado.sesion.resumen || {};
  const estado = resultado.estado_grupo;

  return (
    <Aparece className="tarjeta border-guinda-600/25 bg-nieve/30">
      <header className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-borde pb-3">
        <div>
          <p className="etiqueta">Memoria de la sesión</p>
          <h2 className="text-base font-semibold text-tinta">
            {resumen.titulo || "Sesión registrada"}
          </h2>
        </div>
        <span className="chip bg-guinda text-blanco">
          {resultado.temas_registrados}{" "}
          {resultado.temas_registrados === 1 ? "tema registrado" : "temas registrados"}
        </span>
      </header>

      <TextoRico contenido={resumen.resumen} />

      {resumen.puntos_clave?.length > 0 && (
        <div className="mt-4 border-t border-borde pt-3">
          <p className="etiqueta mb-2">Puntos clave</p>
          <ul className="space-y-1 text-sm text-tinta">
            {resumen.puntos_clave.map((punto, indice) => (
              <li key={indice} className="flex gap-2">
                <span className="mt-0.5 text-guinda-600">•</span>
                {punto}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4 grid gap-3 border-t border-borde pt-3 sm:grid-cols-2">
        <div>
          <p className="etiqueta">Dónde quedó el grupo</p>
          <p className="mt-1 text-sm text-guinda-900">{resumen.donde_quedo || "—"}</p>
        </div>
        {resumen.pendientes?.length > 0 && (
          <div>
            <p className="etiqueta">Para la próxima</p>
            <ul className="mt-1 space-y-0.5 text-sm text-tinta">
              {resumen.pendientes.map((pendiente, indice) => (
                <li key={indice}>· {pendiente}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {resumen.dudas_detectadas?.length > 0 && (
        <div className="mt-3 rounded-xl bg-blanco p-3">
          <p className="etiqueta mb-1">Dudas que Gemma detectó en el grupo</p>
          <ul className="space-y-0.5 text-sm text-tinta">
            {resumen.dudas_detectadas.map((duda, indice) => (
              <li key={indice}>· {duda}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4 border-t border-borde pt-3">
        <div className="mb-1.5 flex items-baseline justify-between">
          <span className="etiqueta">Avance de {estado.grupo}</span>
          <span className="text-sm font-semibold text-guinda">
            {Math.round(estado.avance * 100)}%
          </span>
        </div>
        <BarraAvance valor={estado.avance} />
        <p className="mt-1.5 text-xs text-gris">
          {estado.temas_cubiertos} de {estado.temas_totales} temas cubiertos
        </p>
      </div>
    </Aparece>
  );
}

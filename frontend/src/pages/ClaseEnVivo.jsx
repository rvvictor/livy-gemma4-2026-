// Dar clase: el profesor abre la sesión, Livy escucha, y al cerrar Gemma 4
// convierte la transcripción en memoria estructurada y hace avanzar la bitácora
// de ESE grupo, sin tocar la de los demás.
import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";

import { Aviso, BarraAvance, Cargando, Encabezado, TextoRico } from "../components/ui.jsx";
import { useMateria } from "../estado.jsx";
import { api } from "../lib/api.js";
import { crearDictado, soportaDictado } from "../lib/speech.js";

// Los fragmentos se agrupan antes de subirlos: una petición por frase saturaría
// la red sin ganar nada, porque el resumen ocurre hasta el cierre.
const MS_ENTRE_ENVIOS = 8000;

export default function ClaseEnVivo() {
  const { materia } = useMateria();
  const ubicacion = useLocation();

  const [estados, setEstados] = useState(null);
  const [grupoId, setGrupoId] = useState(ubicacion.state?.grupoId ?? null);
  const [sesion, setSesion] = useState(null);
  const [transcripcion, setTranscripcion] = useState("");
  const [parcial, setParcial] = useState("");
  const [grabando, setGrabando] = useState(false);
  const [segundos, setSegundos] = useState(0);
  const [cerrando, setCerrando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);

  const dictadoRef = useRef(null);
  const pendienteRef = useRef("");
  const sesionRef = useRef(null);
  const finRef = useRef(null);

  useEffect(() => {
    if (!materia) return;
    api
      .bitacora(materia.id)
      .then((datos) => {
        setEstados(datos.grupos);
        setGrupoId((actual) => actual ?? datos.grupos[0]?.grupo_id ?? null);
      })
      .catch((fallo) => setError(fallo.message));
  }, [materia]);

  // Cronómetro de la sesión.
  useEffect(() => {
    if (!grabando) return undefined;
    const reloj = setInterval(() => setSegundos((valor) => valor + 1), 1000);
    return () => clearInterval(reloj);
  }, [grabando]);

  // Envío periódico de lo dictado.
  useEffect(() => {
    if (!grabando) return undefined;
    const envio = setInterval(vaciarPendiente, MS_ENTRE_ENVIOS);
    return () => clearInterval(envio);
  }, [grabando]);

  useEffect(() => () => dictadoRef.current?.detener(), []);

  async function vaciarPendiente() {
    const texto = pendienteRef.current.trim();
    if (!texto || !sesionRef.current) return;
    pendienteRef.current = "";
    try {
      await api.enviarFragmento(sesionRef.current.id, texto);
    } catch (fallo) {
      // No se pierde nada: el texto vuelve a la cola para el siguiente envío.
      pendienteRef.current = `${texto} ${pendienteRef.current}`.trim();
      setError(`No se pudo guardar un fragmento: ${fallo.message}`);
    }
  }

  async function iniciar() {
    setError(null);
    setResultado(null);
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
      finRef.current = null;

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

  async function cerrar() {
    dictadoRef.current?.detener();
    setGrabando(false);
    setParcial("");
    setCerrando(true);
    setError(null);
    try {
      await vaciarPendiente();
      const respuesta = await api.cerrarSesion(sesion.id, Math.round(segundos / 60));
      setResultado(respuesta);
      setSesion(null);
      sesionRef.current = null;
      const datos = await api.bitacora(materia.id);
      setEstados(datos.grupos);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setCerrando(false);
    }
  }

  if (!estados) return <Cargando texto="Cargando tus grupos…" />;

  const grupo = estados.find((estado) => estado.grupo_id === grupoId);
  const reloj = `${String(Math.floor(segundos / 60)).padStart(2, "0")}:${String(segundos % 60).padStart(2, "0")}`;

  return (
    <div className="space-y-6">
      <Encabezado
        titulo="Clase en vivo"
        descripcion="Livy escucha la sesión y la convierte en memoria estructurada al terminar. El profesor revisa siempre antes de que quede asentada."
      />

      {error && <Aviso tipo="error">{error}</Aviso>}
      {!soportaDictado() && (
        <Aviso tipo="alerta">
          Este navegador no expone la API de dictado. La clase en vivo requiere Chrome o Edge.
        </Aviso>
      )}

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <aside className="space-y-4">
          <div className="tarjeta">
            <label className="etiqueta mb-2 block" htmlFor="grupo">
              Grupo de esta sesión
            </label>
            <select
              id="grupo"
              className="w-full rounded-md border border-borde bg-blanco px-3 py-2 text-sm
                         focus:border-guinda focus:outline-none disabled:opacity-50"
              value={grupoId ?? ""}
              disabled={grabando}
              onChange={(evento) => setGrupoId(Number(evento.target.value))}
            >
              {estados.map((estado) => (
                <option key={estado.grupo_id} value={estado.grupo_id}>
                  {estado.grupo} — {estado.horario}
                </option>
              ))}
            </select>

            {grupo && (
              <div className="mt-4 space-y-3 border-t border-borde pt-4">
                <div>
                  <p className="etiqueta">Este grupo quedó en</p>
                  <p className="text-sm font-medium text-guinda-900">
                    {grupo.tema_actual?.titulo || "Sin sesiones registradas"}
                  </p>
                </div>
                <div>
                  <p className="etiqueta">Le sigue</p>
                  <p className="text-sm text-tinta">
                    {grupo.siguiente_pendiente?.titulo || "Plan completo"}
                  </p>
                </div>
                <div>
                  <p className="etiqueta mb-1">Avance</p>
                  <BarraAvance valor={grupo.avance} />
                </div>
              </div>
            )}
          </div>

          {!grabando ? (
            <button className="boton-primario w-full" onClick={iniciar} disabled={!grupoId}>
              Iniciar clase
            </button>
          ) : (
            <button className="boton-primario w-full" onClick={cerrar} disabled={cerrando}>
              {cerrando ? "Gemma está resumiendo…" : "Terminar y generar memoria"}
            </button>
          )}
        </aside>

        <section className="tarjeta flex min-h-[380px] flex-col">
          <header className="mb-3 flex items-center justify-between border-b border-borde pb-3">
            <div className="flex items-center gap-2">
              {grabando && <span className="latido inline-block h-2.5 w-2.5 rounded-full bg-rojo" />}
              <span className="text-sm font-medium text-tinta">
                {grabando ? "Escuchando la clase" : "Transcripción"}
              </span>
            </div>
            <span className="font-mono text-sm text-gris">{reloj}</span>
          </header>

          <div className="flex-1 overflow-y-auto text-sm leading-relaxed">
            {transcripcion || parcial ? (
              <p className="text-tinta">
                {transcripcion} <span className="text-gris">{parcial}</span>
              </p>
            ) : (
              <p className="text-gris">
                Inicia la clase y habla con normalidad. Lo que digas aparece aquí y se guarda
                conforme avanza la sesión.
              </p>
            )}
          </div>

          {transcripcion && (
            <p className="mt-3 border-t border-borde pt-3 text-xs text-gris">
              {transcripcion.length} caracteres capturados
            </p>
          )}
        </section>
      </div>

      {resultado && <MemoriaDeSesion resultado={resultado} />}
    </div>
  );
}

function MemoriaDeSesion({ resultado }) {
  const resumen = resultado.sesion.resumen || {};
  const estado = resultado.estado_grupo;

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-borde pb-3">
        <h2 className="text-lg font-semibold text-tinta">
          {resumen.titulo || "Memoria de la sesión"}
        </h2>
        <span className="chip bg-nieve text-guinda-900">
          {resultado.temas_registrados}{" "}
          {resultado.temas_registrados === 1 ? "tema registrado" : "temas registrados"}
        </span>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <article className="tarjeta space-y-4">
          <TextoRico contenido={resumen.resumen} />

          {resumen.puntos_clave?.length > 0 && (
            <div className="border-t border-borde pt-3">
              <p className="etiqueta mb-2">Puntos clave</p>
              <ul className="space-y-1 text-sm text-tinta">
                {resumen.puntos_clave.map((punto, indice) => (
                  <li key={indice} className="flex gap-2">
                    <span className="text-guinda-600">•</span>
                    {punto}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {resumen.dudas_detectadas?.length > 0 && (
            <div className="rounded-md bg-hueso p-3">
              <p className="etiqueta mb-1">Dudas que Gemma detectó en el grupo</p>
              <ul className="space-y-1 text-sm text-tinta">
                {resumen.dudas_detectadas.map((duda, indice) => (
                  <li key={indice}>· {duda}</li>
                ))}
              </ul>
            </div>
          )}
        </article>

        <aside className="space-y-4">
          <div className="tarjeta">
            <p className="etiqueta">Dónde quedó el grupo</p>
            <p className="mt-1 text-sm text-guinda-900">{resumen.donde_quedo || "—"}</p>
          </div>

          {resumen.pendientes?.length > 0 && (
            <div className="tarjeta">
              <p className="etiqueta mb-2">Para la próxima sesión</p>
              <ul className="space-y-1 text-sm text-tinta">
                {resumen.pendientes.map((pendiente, indice) => (
                  <li key={indice}>· {pendiente}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="tarjeta">
            <p className="etiqueta mb-2">Avance de {estado.grupo}</p>
            <BarraAvance valor={estado.avance} />
            <p className="mt-2 text-xs text-gris">
              {estado.temas_cubiertos} de {estado.temas_totales} temas ·{" "}
              {Math.round(estado.avance * 100)}%
            </p>
          </div>
        </aside>
      </div>
    </section>
  );
}

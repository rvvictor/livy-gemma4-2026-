// Chat sobre todo el curso.
//
// A diferencia del chat de una clase, aquí entra el historial completo del grupo
// en el contexto de 256K de Gemma 4: sin embeddings ni base vectorial, lo que
// elimina de raíz el fallo de recuperación.
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

const SUGERENCIAS = [
  "¿Qué me perdí la clase pasada?",
  "¿Dónde vamos del temario?",
  "Explícame otra vez lo último que vimos",
];

export default function ChatGeneral() {
  const { grupoId } = useParams();
  const [datos, setDatos] = useState(null);
  const [mensajes, setMensajes] = useState([]);
  const [pregunta, setPregunta] = useState("");
  const [pensando, setPensando] = useState(false);
  const [error, setError] = useState(null);
  const fin = useRef(null);

  useEffect(() => {
    Promise.all([api.clases(grupoId), api.historialChat(grupoId)])
      .then(([clases, historial]) => {
        setDatos(clases);
        setMensajes(historial);
      })
      .catch((fallo) => setError(fallo.message));
  }, [grupoId]);

  useEffect(() => {
    fin.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [mensajes, pensando]);

  async function enviar(texto) {
    const limpio = (texto ?? pregunta).trim();
    if (!limpio || pensando) return;

    setMensajes((previos) => [...previos, { rol: "alumno", contenido: limpio }]);
    setPregunta("");
    setPensando(true);
    setError(null);
    try {
      const respuesta = await api.preguntar(grupoId, limpio);
      setMensajes((previos) => [...previos, { rol: "asistente", contenido: respuesta.respuesta }]);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setPensando(false);
    }
  }

  if (error && !datos) return <Aviso tipo="error">{error}</Aviso>;
  if (!datos) return <Esqueleto filas={3} />;

  return (
    <div className="flex h-[calc(100vh-13rem)] flex-col">
      <Aparece className="mb-5 border-b border-borde pb-4">
        <Link to={`/alumno/${grupoId}`} className="text-xs text-gris subraya-hover hover:text-guinda">
          ← {datos.materia} · {datos.grupo}
        </Link>
        <h1 className="mt-2 text-[26px] font-semibold tracking-tight text-tinta">
          Pregunta sobre el curso
        </h1>
        <p className="mt-1 text-sm text-gris">
          Livy responde con las {datos.clases.length} clases que {datos.profesor} le dio a tu
          grupo. Si algo todavía no se ve en tu sección, te lo dice en vez de adelantarse.
        </p>
      </Aparece>

      {error && (
        <div className="mb-3">
          <Aviso tipo="error">{error}</Aviso>
        </div>
      )}

      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {mensajes.length === 0 && (
          <Aparece className="space-y-3 py-4">
            <p className="text-sm text-gris">Puedes empezar por aquí:</p>
            <div className="flex flex-wrap gap-2">
              {SUGERENCIAS.map((sugerencia, indice) => (
                <Aparece key={sugerencia} retraso={indice * 80} como="span">
                  <button className="boton-secundario" onClick={() => enviar(sugerencia)}>
                    {sugerencia}
                  </button>
                </Aparece>
              ))}
            </div>
          </Aparece>
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
        {pensando && <Escribiendo texto="Buscando en tus clases" />}
        <div ref={fin} />
      </div>

      <form
        onSubmit={(evento) => {
          evento.preventDefault();
          enviar();
        }}
        className="mt-4 flex items-end gap-2 rounded-2xl border border-borde bg-blanco p-2.5"
      >
        <input
          className="campo rounded-full border-transparent focus:ring-0"
          placeholder="Escribe tu duda…"
          value={pregunta}
          onChange={(evento) => setPregunta(evento.target.value)}
        />
        <button
          className="boton-primario h-11 w-11 shrink-0 rounded-full p-0 text-lg"
          disabled={pensando || !pregunta.trim()}
          aria-label="Enviar"
        >
          ↑
        </button>
      </form>
    </div>
  );
}

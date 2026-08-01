// Plan de estudios. El profesor sube la foto o el PDF de su temario y Gemma 4 lo
// lee con visión; el resultado NO se guarda solo: pasa por una pantalla de
// revisión donde él corrige antes de que quede asentado. El modelo transcribe,
// el profesor sigue siendo el autor del plan.
import { useEffect, useRef, useState } from "react";

import { Aviso, Cargando, Encabezado } from "../components/ui.jsx";
import { useMateria } from "../estado.jsx";
import { api } from "../lib/api.js";

export default function Temario() {
  const { materia, recargar } = useMateria();
  const [propuesta, setPropuesta] = useState(null);
  const [analizando, setAnalizando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState(null);
  const [aviso, setAviso] = useState(null);
  const archivoRef = useRef(null);

  useEffect(() => {
    setAviso(null);
  }, [materia]);

  async function analizar(evento) {
    const archivo = evento.target.files?.[0];
    if (!archivo) return;
    setAnalizando(true);
    setError(null);
    setAviso(null);
    try {
      const respuesta = await api.analizarTemario(materia.id, archivo);
      setPropuesta(respuesta.temas);
      setAviso(
        `Gemma leyó ${respuesta.temas.length} temas desde ${
          respuesta.fuente === "pdf" ? "el PDF" : "la imagen"
        }. Revísalos antes de guardar.`,
      );
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setAnalizando(false);
      if (archivoRef.current) archivoRef.current.value = "";
    }
  }

  function editar(indice, campo, valor) {
    setPropuesta((temas) =>
      temas.map((tema, i) => (i === indice ? { ...tema, [campo]: valor } : tema)),
    );
  }

  function eliminar(indice) {
    setPropuesta((temas) =>
      temas.filter((_, i) => i !== indice).map((tema, i) => ({ ...tema, orden: i + 1 })),
    );
  }

  async function guardar() {
    setGuardando(true);
    setError(null);
    try {
      await api.guardarTemario(
        materia.id,
        propuesta.map((tema, indice) => ({
          orden: indice + 1,
          unidad: tema.unidad || "",
          titulo: tema.titulo,
          subtemas: Array.isArray(tema.subtemas)
            ? tema.subtemas
            : String(tema.subtemas || "")
                .split(",")
                .map((s) => s.trim())
                .filter(Boolean),
        })),
      );
      setPropuesta(null);
      setAviso("Plan de estudios actualizado. La bitácora de todos los grupos usa esta versión.");
      await recargar();
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setGuardando(false);
    }
  }

  if (!materia) return <Cargando />;

  return (
    <div className="space-y-6">
      <Encabezado
        titulo="Plan de estudios"
        descripcion="Gemma 4 lee tu temario con visión, incluso fotografiado en ángulo o con anotaciones a mano. Tú validas antes de guardar."
        acciones={
          <>
            <input
              ref={archivoRef}
              id="archivo-temario"
              type="file"
              accept="image/*,application/pdf"
              className="hidden"
              onChange={analizar}
            />
            <label htmlFor="archivo-temario" className="boton-primario cursor-pointer">
              {analizando ? "Gemma está leyendo…" : "Subir foto o PDF del temario"}
            </label>
          </>
        }
      />

      {error && <Aviso tipo="error">{error}</Aviso>}
      {aviso && <Aviso tipo="alerta">{aviso}</Aviso>}

      {propuesta ? (
        <section className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-tinta">Revisión antes de guardar</h2>
            <div className="flex gap-2">
              <button className="boton-secundario" onClick={() => setPropuesta(null)}>
                Descartar
              </button>
              <button className="boton-primario" onClick={guardar} disabled={guardando}>
                {guardando ? "Guardando…" : "Confirmar plan de estudios"}
              </button>
            </div>
          </div>

          <div className="overflow-x-auto rounded-lg border border-borde bg-blanco">
            <table className="w-full min-w-[680px] text-sm">
              <thead>
                <tr className="border-b border-borde text-left">
                  <th className="w-14 px-3 py-2.5 font-medium text-gris">#</th>
                  <th className="px-3 py-2.5 font-medium text-gris">Unidad</th>
                  <th className="px-3 py-2.5 font-medium text-gris">Tema</th>
                  <th className="px-3 py-2.5 font-medium text-gris">Subtemas</th>
                  <th className="w-12 px-3 py-2.5" />
                </tr>
              </thead>
              <tbody>
                {propuesta.map((tema, indice) => (
                  <tr key={indice} className="border-b border-borde last:border-0">
                    <td className="px-3 py-2 text-gris">{indice + 1}</td>
                    <td className="px-3 py-2">
                      <input
                        className="w-full rounded border border-transparent bg-transparent px-2 py-1
                                   hover:border-borde focus:border-guinda focus:outline-none"
                        value={tema.unidad || ""}
                        onChange={(e) => editar(indice, "unidad", e.target.value)}
                      />
                    </td>
                    <td className="px-3 py-2">
                      <input
                        className="w-full rounded border border-transparent bg-transparent px-2 py-1
                                   font-medium hover:border-borde focus:border-guinda focus:outline-none"
                        value={tema.titulo || ""}
                        onChange={(e) => editar(indice, "titulo", e.target.value)}
                      />
                    </td>
                    <td className="px-3 py-2">
                      <input
                        className="w-full rounded border border-transparent bg-transparent px-2 py-1
                                   text-gris hover:border-borde focus:border-guinda focus:outline-none"
                        value={
                          Array.isArray(tema.subtemas)
                            ? tema.subtemas.join(", ")
                            : tema.subtemas || ""
                        }
                        onChange={(e) =>
                          editar(indice, "subtemas", e.target.value.split(",").map((s) => s.trim()))
                        }
                      />
                    </td>
                    <td className="px-3 py-2 text-center">
                      <button
                        className="text-gris transition hover:text-rojo"
                        onClick={() => eliminar(indice)}
                        title="Quitar tema"
                      >
                        ×
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : (
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-tinta">
            Plan vigente · {materia.temas.length} temas
          </h2>
          <div className="overflow-hidden rounded-lg border border-borde bg-blanco">
            {materia.temas.map((tema) => (
              <div
                key={tema.id}
                className="flex flex-wrap gap-x-4 gap-y-1 border-b border-borde px-4 py-3 last:border-0"
              >
                <span className="w-6 text-sm text-gris">{tema.orden}</span>
                <div className="min-w-[220px] flex-1">
                  <p className="text-sm font-medium text-tinta">{tema.titulo}</p>
                  {tema.subtemas.length > 0 && (
                    <p className="text-xs text-gris">{tema.subtemas.join(" · ")}</p>
                  )}
                </div>
                <span className="chip bg-hueso text-gris">{tema.unidad}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

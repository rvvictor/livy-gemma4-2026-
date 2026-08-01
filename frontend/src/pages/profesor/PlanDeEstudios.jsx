// Plan de estudios: cómo está organizado el ciclo completo del profesor.
//
// No es una lista de temas, es la vista de sistema: cuántas materias lleva, qué
// grupos comparten alumnos, dónde va cada sección y qué unidad falta por cubrir.
// Aquí también se carga el temario con la visión de Gemma 4, siempre pasando por
// una pantalla de revisión: el modelo transcribe, el profesor sigue siendo el autor.
import { useEffect, useMemo, useRef, useState } from "react";

import { Aparece, Aviso, BarraAvance, Encabezado, Esqueleto } from "../../components/ui.jsx";
import { useCiclo } from "../../estado.jsx";
import { api } from "../../lib/api.js";

const PUNTO_NIVEL = {
  cubierto: "bg-guinda",
  reforzado: "bg-guinda-900",
  introducido: "bg-nieve ring-1 ring-inset ring-guinda-600/50",
};

export default function PlanDeEstudios() {
  const { ciclo, cargando, recargar } = useCiclo();
  const [materiaId, setMateriaId] = useState(null);
  const [propuesta, setPropuesta] = useState(null);
  const [analizando, setAnalizando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState(null);
  const [aviso, setAviso] = useState(null);
  const archivoRef = useRef(null);

  useEffect(() => {
    if (!ciclo?.materias?.length) return;
    setMateriaId((actual) => actual ?? ciclo.materias[0].id);
  }, [ciclo]);

  const materia = useMemo(
    () => ciclo?.materias.find((m) => m.id === materiaId) || null,
    [ciclo, materiaId],
  );

  const unidades = useMemo(() => {
    if (!materia) return [];
    const mapa = new Map();
    for (const tema of materia.temas) {
      const clave = tema.unidad || "Sin unidad";
      if (!mapa.has(clave)) mapa.set(clave, []);
      mapa.get(clave).push(tema);
    }
    return [...mapa.entries()];
  }, [materia]);

  async function analizar(evento) {
    const archivo = evento.target.files?.[0];
    if (!archivo) return;
    setAnalizando(true);
    setError(null);
    setAviso(null);
    try {
      const respuesta = await api.analizarTemario(materiaId, archivo);
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
    setPropuesta((temas) => temas.filter((_, i) => i !== indice));
  }

  async function guardar() {
    setGuardando(true);
    setError(null);
    try {
      await api.guardarTemario(
        materiaId,
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
      setAviso("Plan actualizado. La bitácora de todos los grupos usa esta versión.");
      await recargar();
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setGuardando(false);
    }
  }

  if (cargando || !ciclo) return <Esqueleto filas={4} />;

  return (
    <div className="space-y-10">
      <Encabezado
        titulo={`Tu ciclo ${ciclo.ciclo}`}
        descripcion={`${ciclo.profesor} · ${ciclo.materias.length} materias · ${ciclo.total_grupos} secciones · ${ciclo.total_alumnos} alumnos en total`}
      />

      {error && <Aviso tipo="error">{error}</Aviso>}
      {aviso && <Aviso tipo="alerta">{aviso}</Aviso>}

      {/* ── Panorama del ciclo ── */}
      <section className="grid gap-4 md:grid-cols-2">
        {ciclo.materias.map((asignatura, indice) => (
          <Aparece key={asignatura.id} retraso={indice * 90}>
            <button
              onClick={() => {
                setMateriaId(asignatura.id);
                setPropuesta(null);
              }}
              className={`w-full rounded-2xl border bg-blanco p-5 text-left transition-all duration-300
                          hover:-translate-y-0.5 hover:shadow-[0_8px_30px_-12px_rgba(109,26,54,0.25)] ${
                            materiaId === asignatura.id
                              ? "border-guinda ring-4 ring-nieve"
                              : "border-borde hover:border-guinda-300"
                          }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="etiqueta">{asignatura.clave}</p>
                  <h2 className="mt-0.5 text-lg font-semibold text-tinta">{asignatura.nombre}</h2>
                </div>
                <span className="chip bg-nieve text-guinda-900">
                  {asignatura.grupos.length}{" "}
                  {asignatura.grupos.length === 1 ? "sección" : "secciones"}
                </span>
              </div>

              <div className="mt-4">
                <div className="mb-1.5 flex items-baseline justify-between text-sm">
                  <span className="text-gris">Avance promedio</span>
                  <span className="font-semibold text-guinda">
                    {Math.round(asignatura.avance_promedio * 100)}%
                  </span>
                </div>
                <BarraAvance valor={asignatura.avance_promedio} />
              </div>

              <p className="mt-3 text-xs text-gris">
                {asignatura.temas.length} temas · {asignatura.sesiones_planeadas} sesiones
                planeadas en el ciclo
              </p>
            </button>
          </Aparece>
        ))}
      </section>

      {ciclo.grupos_compartidos.length > 0 && (
        <Aparece>
          <Aviso tipo="alerta">
            {ciclo.grupos_compartidos.map((compartido) => (
              <span key={compartido.grupo}>
                El grupo <strong className="font-semibold">{compartido.grupo}</strong> lleva
                contigo {compartido.materias.join(" y ")}: son los mismos alumnos en las dos
                listas.
              </span>
            ))}
          </Aviso>
        </Aparece>
      )}

      {materia && (
        <>
          {/* ── Secciones de la materia seleccionada ── */}
          <section>
            <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-tinta">
                  Secciones de {materia.nombre}
                </h2>
                <p className="mt-0.5 text-sm text-gris">
                  El mismo plan, cinco recorridos. Cada barra es independiente.
                </p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {materia.grupos.map((grupo, indice) => (
                <Aparece key={grupo.grupo_id} retraso={indice * 80}>
                  <article className="tarjeta-interactiva h-full">
                    <header className="flex items-start justify-between gap-2">
                      <div>
                        <p className="font-semibold text-tinta">{grupo.grupo}</p>
                        <p className="text-xs text-gris">{grupo.horario}</p>
                      </div>
                      <span className="chip bg-hueso text-gris">{grupo.alumnos} alumnos</span>
                    </header>

                    <div className="mt-4">
                      <div className="mb-1.5 flex items-baseline justify-between">
                        <span className="etiqueta">Avance del plan</span>
                        <span className="text-sm font-semibold text-guinda">
                          {Math.round(grupo.avance * 100)}%
                        </span>
                      </div>
                      <BarraAvance valor={grupo.avance} />
                      <p className="mt-1.5 text-xs text-gris">
                        {grupo.temas_cubiertos} de {grupo.temas_totales} temas ·{" "}
                        {grupo.sesiones_impartidas} sesiones
                      </p>
                    </div>

                    <dl className="mt-4 space-y-2 border-t border-borde pt-3 text-sm">
                      <div>
                        <dt className="etiqueta">Quedó en</dt>
                        <dd className="text-tinta">
                          {grupo.tema_actual?.titulo || "Sin sesiones aún"}
                        </dd>
                      </div>
                      <div>
                        <dt className="etiqueta">Sigue</dt>
                        <dd className="text-guinda-900">
                          {grupo.siguiente_pendiente?.titulo || "Plan completo"}
                        </dd>
                      </div>
                    </dl>
                  </article>
                </Aparece>
              ))}
            </div>
          </section>

          {materia.relacion && (
            <Aparece>
              <div className="tarjeta bg-hueso">
                <p className="etiqueta mb-1.5">Cómo se conecta con el resto de tu ciclo</p>
                <p className="text-sm leading-relaxed text-tinta">{materia.relacion}</p>
              </div>
            </Aparece>
          )}

          {/* ── El plan, unidad por unidad ── */}
          <section>
            <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-tinta">
                  Plan de {materia.nombre} · {materia.temas.length} temas
                </h2>
                <p className="mt-0.5 text-sm text-gris">
                  Cada punto indica si esa sección ya cubrió el tema.
                </p>
              </div>
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
                  {analizando ? "Gemma está leyendo…" : "Cargar temario con foto o PDF"}
                </label>
              </>
            </div>

            {propuesta ? (
              <RevisionTemario
                propuesta={propuesta}
                editar={editar}
                eliminar={eliminar}
                guardar={guardar}
                cancelar={() => setPropuesta(null)}
                guardando={guardando}
              />
            ) : (
              <div className="space-y-5">
                {unidades.map(([unidad, temas], indiceUnidad) => (
                  <Aparece key={unidad} retraso={indiceUnidad * 70}>
                    <div className="overflow-hidden rounded-2xl border border-borde bg-blanco">
                      <div className="flex items-baseline justify-between border-b border-borde bg-hueso px-4 py-2.5">
                        <span className="text-sm font-semibold text-guinda">{unidad}</span>
                        <span className="text-xs text-gris">
                          {temas.length} {temas.length === 1 ? "tema" : "temas"}
                        </span>
                      </div>

                      {temas.map((tema) => (
                        <div
                          key={tema.id}
                          className="flex flex-wrap items-center gap-x-4 gap-y-2 border-b border-borde px-4 py-3 transition-colors last:border-0 hover:bg-hueso"
                        >
                          <span className="w-6 text-sm text-gris">{tema.orden}</span>
                          <div className="min-w-[200px] flex-1">
                            <p className="text-sm font-medium text-tinta">{tema.titulo}</p>
                            {tema.subtemas.length > 0 && (
                              <p className="text-xs text-gris">{tema.subtemas.join(" · ")}</p>
                            )}
                          </div>

                          <div className="flex items-center gap-2">
                            {materia.grupos.map((grupo) => {
                              const celda = grupo.detalle.find((f) => f.tema_id === tema.id);
                              return (
                                <span
                                  key={grupo.grupo_id}
                                  title={`${grupo.grupo}: ${celda?.nivel || "pendiente"}`}
                                  className="flex flex-col items-center gap-1"
                                >
                                  <span
                                    className={`h-2.5 w-2.5 rounded-full ${
                                      celda?.nivel ? PUNTO_NIVEL[celda.nivel] : "bg-borde"
                                    }`}
                                  />
                                  <span className="text-[10px] text-gris">{grupo.grupo}</span>
                                </span>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  </Aparece>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}

function RevisionTemario({ propuesta, editar, eliminar, guardar, cancelar, guardando }) {
  return (
    <Aparece className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-semibold text-tinta">Revisión antes de guardar</h3>
          <p className="text-sm text-gris">
            Gemma leyó el documento. Corrige lo que haga falta: tú firmas el plan.
          </p>
        </div>
        <div className="flex gap-2">
          <button className="boton-secundario" onClick={cancelar}>
            Descartar
          </button>
          <button className="boton-primario" onClick={guardar} disabled={guardando}>
            {guardando ? "Guardando…" : "Confirmar plan"}
          </button>
        </div>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-borde bg-blanco">
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
                    className="w-full rounded-lg border border-transparent bg-transparent px-2 py-1
                               transition-colors hover:border-borde focus:border-guinda focus:outline-none"
                    value={tema.unidad || ""}
                    onChange={(e) => editar(indice, "unidad", e.target.value)}
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    className="w-full rounded-lg border border-transparent bg-transparent px-2 py-1
                               font-medium transition-colors hover:border-borde focus:border-guinda focus:outline-none"
                    value={tema.titulo || ""}
                    onChange={(e) => editar(indice, "titulo", e.target.value)}
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    className="w-full rounded-lg border border-transparent bg-transparent px-2 py-1
                               text-gris transition-colors hover:border-borde focus:border-guinda focus:outline-none"
                    value={
                      Array.isArray(tema.subtemas) ? tema.subtemas.join(", ") : tema.subtemas || ""
                    }
                    onChange={(e) =>
                      editar(indice, "subtemas", e.target.value.split(",").map((s) => s.trim()))
                    }
                  />
                </td>
                <td className="px-3 py-2 text-center">
                  <button
                    className="text-gris transition-colors hover:text-rojo"
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
    </Aparece>
  );
}

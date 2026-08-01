// La pantalla con la que el profesor abre el día: qué clases tiene esta semana,
// qué tema toca en cada una y qué sigue para cada sección.
import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

import RevisionHorario from "../../components/RevisionHorario.jsx";
import {
  Aparece,
  Aviso,
  ChipRiesgo,
  Encabezado,
  Esqueleto,
  useConfirmacion,
} from "../../components/ui.jsx";
import { useCiclo } from "../../estado.jsx";
import { api } from "../../lib/api.js";

const NIVEL_CELDA = {
  cubierto: "bg-guinda",
  reforzado: "bg-guinda-900",
  introducido: "bg-nieve ring-1 ring-inset ring-guinda-600/40",
};

const ESTADO_CLASE = {
  impartida: { chip: "bg-nieve text-guinda-900", texto: "Impartida" },
  en_curso: { chip: "bg-rojo text-blanco", texto: "En curso" },
  planeada: { chip: "bg-hueso text-gris", texto: "Pendiente" },
};

function desplazar(iso, dias) {
  const fecha = new Date(`${iso}T12:00:00`);
  fecha.setDate(fecha.getDate() + dias);
  return fecha.toISOString().slice(0, 10);
}

function formatoCorto(iso) {
  return new Date(`${iso}T12:00:00`).toLocaleDateString("es-MX", {
    day: "numeric",
    month: "short",
  });
}

export default function Bitacora() {
  const { ciclo, recargar } = useCiclo();
  const [referencia, setReferencia] = useState(null);
  const [agenda, setAgenda] = useState(null);
  const [error, setError] = useState(null);
  const [aviso, setAviso] = useState(null);

  const [materiaMapa, setMateriaMapa] = useState(null);
  const [mapa, setMapa] = useState(null);
  const [recomendaciones, setRecomendaciones] = useState({});
  const [pensando, setPensando] = useState(null);

  // Carga del horario por visión
  const [propuesta, setPropuesta] = useState(null);
  const [fuente, setFuente] = useState("");
  const [analizando, setAnalizando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const archivoRef = useRef(null);
  const { pedir, dialogo } = useConfirmacion();

  useEffect(() => {
    let vigente = true;
    setAgenda(null);
    api
      .agenda(referencia)
      .then((datos) => vigente && setAgenda(datos))
      .catch((fallo) => vigente && setError(fallo.message));
    return () => {
      vigente = false;
    };
  }, [referencia]);

  useEffect(() => {
    if (!ciclo?.materias?.length) return;
    setMateriaMapa((actual) => actual ?? ciclo.materias[0].id);
  }, [ciclo]);

  useEffect(() => {
    if (!materiaMapa) return;
    let vigente = true;
    setMapa(null);
    api
      .bitacora(materiaMapa)
      .then((datos) => vigente && setMapa(datos))
      .catch((fallo) => vigente && setError(fallo.message));
    return () => {
      vigente = false;
    };
  }, [materiaMapa]);

  async function pedirRecomendaciones(materiaId) {
    setPensando(materiaId);
    setError(null);
    try {
      const respuesta = await api.recomendaciones(materiaId);
      const porGrupo = {};
      for (const recomendacion of respuesta.recomendaciones) {
        porGrupo[recomendacion.grupo_id] = recomendacion;
      }
      setRecomendaciones((previas) => ({ ...previas, ...porGrupo }));
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setPensando(null);
    }
  }

  async function analizarHorario(evento) {
    const archivo = evento.target.files?.[0];
    if (!archivo) return;
    setAnalizando(true);
    setError(null);
    setAviso(null);
    try {
      const respuesta = await api.analizarHorario(archivo);
      setPropuesta(respuesta.clases);
      setFuente(respuesta.fuente);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setAnalizando(false);
      if (archivoRef.current) archivoRef.current.value = "";
    }
  }

  function editarClase(indice, campo, valor) {
    setPropuesta((clases) =>
      clases.map((clase, i) => (i === indice ? { ...clase, [campo]: valor } : clase)),
    );
  }

  function alternarDia(indice, dia) {
    setPropuesta((clases) =>
      clases.map((clase, i) => {
        if (i !== indice) return clase;
        const dias = clase.dias.includes(dia)
          ? clase.dias.filter((d) => d !== dia)
          : [...clase.dias, dia].sort();
        return { ...clase, dias };
      }),
    );
  }

  function eliminarClase(indice) {
    setPropuesta((clases) => clases.filter((_, i) => i !== indice));
  }

  async function guardarHorario() {
    setGuardando(true);
    setError(null);
    try {
      const resultado = await api.guardarHorario(
        propuesta.map((clase) => ({
          materia: clase.materia,
          clave: clase.clave,
          grupo: clase.grupo,
          dias: clase.dias,
          hora_inicio: clase.hora_inicio,
          hora_fin: clase.hora_fin,
        })),
      );
      setPropuesta(null);
      setAviso(
        `Horario aplicado: ${resultado.materias_creadas} materias nuevas, ` +
          `${resultado.grupos_creados} grupos nuevos, ${resultado.grupos_actualizados} actualizados.`,
      );
      await recargar();
      setAgenda(await api.agenda(referencia)); // releer con los grupos recién creados
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setGuardando(false);
    }
  }

  /** Vacía el horario para poder volver a cargarlo desde cero. */
  function borrarHorario() {
    pedir({
      titulo: "Borrar todo el horario",
      cuerpo: `Se eliminan las ${ciclo?.total_grupos ?? 0} secciones registradas. Es lo que se hace cuando Gemma leyó mal la foto y quedaron grupos que no existen.`,
      consecuencias: [
        "Se pierden todas las clases grabadas y el avance de cada sección",
        "La agenda semanal queda vacía",
      ],
      conserva: ["Las materias y sus planes de estudio se quedan"],
      confirmar: "Borrar el horario",
      accion: async () => {
        setError(null);
        setAviso(null);
        try {
          const respuesta = await api.borrarHorario();
          setAviso(respuesta.detalle);
          await recargar();
          setAgenda(await api.agenda(referencia));
        } catch (fallo) {
          setError(fallo.message);
        }
      },
    });
  }

  const porDia = useMemo(() => {
    if (!agenda) return [];
    const mapaDias = new Map();
    for (const clase of agenda.clases) {
      if (!mapaDias.has(clase.fecha)) mapaDias.set(clase.fecha, []);
      mapaDias.get(clase.fecha).push(clase);
    }
    return [...mapaDias.entries()];
  }, [agenda]);

  return (
    <div className="space-y-12">
      <Encabezado
        titulo="Tu semana"
        descripcion={
          ciclo
            ? `${ciclo.profesor} · ${ciclo.materias.length} materias · ${ciclo.total_grupos} grupos · ${ciclo.total_alumnos} alumnos`
            : "Cargando tu ciclo…"
        }
        acciones={
          <>
            <div className="flex items-center gap-1">
              <button
                className="boton-fantasma"
                onClick={() => setReferencia(desplazar(agenda?.inicio ?? new Date().toISOString().slice(0, 10), -7))}
                disabled={!agenda}
              >
                ← Anterior
              </button>
              <button className="boton-secundario" onClick={() => setReferencia(null)}>
                Esta semana
              </button>
              <button
                className="boton-fantasma"
                onClick={() => setReferencia(desplazar(agenda?.inicio ?? new Date().toISOString().slice(0, 10), 7))}
                disabled={!agenda}
              >
                Siguiente →
              </button>
            </div>
            <input
              ref={archivoRef}
              id="archivo-horario"
              type="file"
              accept="image/*,application/pdf"
              className="hidden"
              onChange={analizarHorario}
            />
            <label htmlFor="archivo-horario" className="boton-primario cursor-pointer">
              {analizando ? "Gemma está leyendo…" : "Cargar horario con foto o PDF"}
            </label>
            {ciclo?.total_grupos > 0 && !propuesta && (
              <button className="boton-peligro" onClick={borrarHorario}>
                Borrar horario
              </button>
            )}
          </>
        }
      />

      {error && <Aviso tipo="error">{error}</Aviso>}
      {aviso && <Aviso tipo="alerta">{aviso}</Aviso>}

      {propuesta && (
        <RevisionHorario
          clases={propuesta}
          editar={editarClase}
          alternarDia={alternarDia}
          eliminar={eliminarClase}
          guardar={guardarHorario}
          cancelar={() => setPropuesta(null)}
          guardando={guardando}
          fuente={fuente}
        />
      )}

      {/* ── Agenda semanal ── */}
      <section>
        <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="text-lg font-semibold text-tinta">
            {agenda ? `${formatoCorto(agenda.inicio)} — ${formatoCorto(agenda.fin)}` : "Agenda"}
          </h2>
          {agenda && (
            <p className="text-sm text-gris">
              {agenda.impartidas} de {agenda.total} clases impartidas
              {agenda.es_semana_actual && " · semana en curso"}
            </p>
          )}
        </div>

        {!agenda ? (
          <Esqueleto filas={3} />
        ) : porDia.length === 0 ? (
          <Aviso>No hay clases programadas en esta semana.</Aviso>
        ) : (
          // Los días de la semana van siempre en una sola fila. En pantallas
          // angostas la fila se desplaza en horizontal en lugar de romperse,
          // para que la semana se lea como una semana y no como una lista.
          <div className="-mx-6 overflow-x-auto px-6 pb-2">
            <div className="grid min-w-full auto-cols-[minmax(215px,1fr)] grid-flow-col gap-4">
              {porDia.map(([fecha, clases], indiceDia) => {
                const esHoy = fecha === agenda.hoy;
                return (
                  <Aparece key={fecha} retraso={indiceDia * 70}>
                    <div
                      className={`h-full rounded-2xl border bg-blanco p-4 transition-colors ${
                        esHoy ? "border-guinda ring-4 ring-nieve" : "border-borde"
                      }`}
                    >
                      <header className="mb-3 flex items-baseline justify-between border-b border-borde pb-2.5">
                        <span
                          className={`text-sm font-semibold ${esHoy ? "text-guinda" : "text-tinta"}`}
                        >
                          {clases[0].dia}
                        </span>
                        <span className="text-xs text-gris">
                          {esHoy ? "Hoy" : formatoCorto(fecha)}
                        </span>
                      </header>

                      <div className="space-y-4">
                        {clases.map((clase) => (
                          <div key={`${clase.grupo_id}-${clase.fecha}`} className="group">
                            <div className="flex items-baseline justify-between gap-2">
                              <span className="font-mono text-xs text-gris">
                                {clase.hora_inicio}
                              </span>
                              <span className={`chip ${ESTADO_CLASE[clase.estado].chip}`}>
                                {ESTADO_CLASE[clase.estado].texto}
                              </span>
                            </div>
                            <p className="mt-1 text-sm font-medium text-tinta">{clase.grupo}</p>
                            <p className="text-xs text-gris">{clase.materia}</p>
                            <p className="mt-1 text-sm leading-snug text-guinda-900">
                              {clase.tema.titulo}
                            </p>
                            {clase.tema.nota && (
                              <p className="mt-0.5 text-xs text-gris">{clase.tema.nota}</p>
                            )}
                            {clase.estado === "planeada" && (
                              <Link
                                to="/profesor/clase"
                                state={{ grupoId: clase.grupo_id }}
                                className="mt-1.5 inline-block text-xs font-medium text-rojo
                                           opacity-0 transition-opacity duration-200
                                           group-hover:opacity-100 focus:opacity-100"
                              >
                                Dar esta clase →
                              </Link>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </Aparece>
                );
              })}
            </div>
          </div>
        )}
      </section>

      {/* ── Qué sigue para cada grupo ── */}
      <section>
        <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
          <div>
            <h2 className="text-lg font-semibold text-tinta">Qué sigue para cada grupo</h2>
            <p className="mt-0.5 text-sm text-gris">
              Gemma 4 compara lo que cubrió cada sección contra lo que falta del plan y las
              sesiones que quedan del ciclo.
            </p>
          </div>
        </div>

        {!ciclo ? (
          <Esqueleto filas={2} />
        ) : (
          <div className="space-y-6">
            {ciclo.materias.map((materia) => (
              <div key={materia.id}>
                <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                  <h3 className="text-sm font-semibold text-guinda">
                    {materia.clave} · {materia.nombre}
                  </h3>
                  <button
                    className="boton-secundario"
                    onClick={() => pedirRecomendaciones(materia.id)}
                    disabled={pensando === materia.id}
                  >
                    {pensando === materia.id ? "Gemma está analizando…" : "Pedir sugerencia"}
                  </button>
                </div>

                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {materia.grupos.map((grupo, indice) => {
                    const recomendacion = recomendaciones[grupo.grupo_id];
                    return (
                      <Aparece key={grupo.grupo_id} retraso={indice * 80}>
                        <article className="tarjeta-interactiva h-full">
                          <header className="flex items-start justify-between gap-2">
                            <div>
                              <p className="font-semibold text-tinta">{grupo.grupo}</p>
                              <p className="text-xs text-gris">{grupo.horario}</p>
                            </div>
                            {recomendacion ? (
                              <ChipRiesgo riesgo={recomendacion.riesgo} />
                            ) : (
                              <span className="chip bg-hueso text-gris">
                                {Math.round(grupo.avance * 100)}%
                              </span>
                            )}
                          </header>

                          <dl className="mt-4 space-y-2.5 text-sm">
                            <div>
                              <dt className="etiqueta">Quedó en</dt>
                              <dd className="text-tinta">
                                {grupo.tema_actual?.titulo || "Sin sesiones aún"}
                              </dd>
                            </div>
                            <div>
                              <dt className="etiqueta">Sigue</dt>
                              <dd className="text-guinda-900">
                                {recomendacion?.siguiente_tema ||
                                  grupo.siguiente_pendiente?.titulo ||
                                  "Plan completo"}
                                {grupo.siguiente_pendiente?.nivel === "introducido" && (
                                  <span className="ml-2 chip bg-nieve text-guinda-900">
                                    quedó a medias
                                  </span>
                                )}
                              </dd>
                            </div>
                          </dl>

                          {recomendacion && (
                            <Aparece className="mt-3 rounded-xl bg-hueso p-3 text-sm">
                              <p className="text-gris">{recomendacion.justificacion}</p>
                              {recomendacion.ajuste_sugerido && (
                                <p className="mt-2 border-t border-borde pt-2 text-tinta">
                                  {recomendacion.ajuste_sugerido}
                                </p>
                              )}
                            </Aparece>
                          )}
                        </article>
                      </Aparece>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* ── Mapa del plan ── */}
      <section>
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-tinta">Mapa del plan de estudios</h2>
            <p className="mt-0.5 text-sm text-gris">
              Cada columna es una sección. El mismo temario, recorridos distintos.
            </p>
          </div>
          {ciclo && ciclo.materias.length > 1 && (
            <div className="flex gap-1 rounded-full border border-borde bg-blanco p-1">
              {ciclo.materias.map((materia) => (
                <button
                  key={materia.id}
                  onClick={() => setMateriaMapa(materia.id)}
                  className={`rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors duration-200 ${
                    materiaMapa === materia.id
                      ? "bg-guinda text-blanco"
                      : "text-gris hover:text-guinda"
                  }`}
                >
                  {materia.nombre}
                </button>
              ))}
            </div>
          )}
        </div>

        {!mapa ? (
          <Esqueleto filas={2} />
        ) : (
          <Aparece>
            {mapa.brecha.temas > 0 && (
              <div className="mb-4 rounded-xl border border-guinda-600/25 bg-nieve px-4 py-3 text-sm text-guinda-900">
                <strong className="font-semibold">{mapa.brecha.adelantado}</strong> va{" "}
                <strong className="font-semibold">
                  {mapa.brecha.temas} {mapa.brecha.temas === 1 ? "tema" : "temas"}
                </strong>{" "}
                por delante de <strong className="font-semibold">{mapa.brecha.rezagado}</strong>.
              </div>
            )}

            <div className="overflow-x-auto rounded-2xl border border-borde bg-blanco">
              <table className="w-full min-w-[560px] text-sm">
                <thead>
                  <tr className="border-b border-borde">
                    <th className="px-4 py-3 text-left font-medium text-gris">Tema</th>
                    {mapa.grupos.map((grupo) => (
                      <th key={grupo.grupo_id} className="w-24 px-3 py-3 font-medium text-guinda">
                        {grupo.grupo}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {mapa.temas.map((tema, indice) => (
                    <tr
                      key={tema.id}
                      className="border-b border-borde transition-colors last:border-0 hover:bg-hueso"
                    >
                      <td className="px-4 py-2.5">
                        <span className="text-tinta">
                          {tema.orden}. {tema.titulo}
                        </span>
                        <span className="ml-2 text-xs text-gris">{tema.unidad}</span>
                      </td>
                      {mapa.grupos.map((grupo) => {
                        const celda = grupo.detalle.find((fila) => fila.tema_id === tema.id);
                        const clase = celda?.nivel ? NIVEL_CELDA[celda.nivel] : "bg-hueso";
                        return (
                          <td key={grupo.grupo_id} className="px-3 py-2.5 text-center">
                            <span
                              title={celda?.nivel || "pendiente"}
                              className={`aparece inline-block h-4 w-10 rounded-md ${clase}`}
                              style={{ animationDelay: `${indice * 35}ms` }}
                            />
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-3 flex flex-wrap gap-4 text-xs text-gris">
              <span className="flex items-center gap-2">
                <span className="inline-block h-3 w-7 rounded-md bg-guinda" /> Cubierto
              </span>
              <span className="flex items-center gap-2">
                <span className="inline-block h-3 w-7 rounded-md bg-nieve ring-1 ring-inset ring-guinda-600/40" />{" "}
                Solo introducido
              </span>
              <span className="flex items-center gap-2">
                <span className="inline-block h-3 w-7 rounded-md bg-hueso ring-1 ring-borde" />{" "}
                Pendiente
              </span>
            </div>
          </Aparece>
        )}
      </section>

      {dialogo}
    </div>
  );
}

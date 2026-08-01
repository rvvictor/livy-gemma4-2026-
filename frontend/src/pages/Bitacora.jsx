// La pantalla del pitch: dónde va cada sección del mismo curso y qué sigue para
// cada una. Es lo que hoy vive solo en la cabeza del profesor.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Aviso, BarraAvance, Cargando, ChipRiesgo, Encabezado } from "../components/ui.jsx";
import { useMateria } from "../estado.jsx";
import { api } from "../lib/api.js";

const NIVEL_CELDA = {
  cubierto: "bg-guinda",
  reforzado: "bg-guinda-900",
  introducido: "bg-nieve border border-guinda-600/40",
};

export default function Bitacora() {
  const { materia } = useMateria();
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);
  const [recomendaciones, setRecomendaciones] = useState(null);
  const [pensando, setPensando] = useState(false);

  useEffect(() => {
    if (!materia) return;
    let vigente = true;
    api
      .bitacora(materia.id)
      .then((respuesta) => vigente && setDatos(respuesta))
      .catch((fallo) => vigente && setError(fallo.message));
    return () => {
      vigente = false;
    };
  }, [materia]);

  async function pedirRecomendaciones() {
    setPensando(true);
    setError(null);
    try {
      const respuesta = await api.recomendaciones(materia.id);
      const porGrupo = {};
      for (const recomendacion of respuesta.recomendaciones) {
        porGrupo[recomendacion.grupo_id] = recomendacion;
      }
      setRecomendaciones({ porGrupo, restantes: respuesta.sesiones_restantes });
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setPensando(false);
    }
  }

  if (error && !datos) return <Aviso tipo="error">{error}</Aviso>;
  if (!datos) return <Cargando texto="Reconstruyendo el avance de cada grupo…" />;

  const { grupos, temas, brecha } = datos;

  return (
    <div className="space-y-8">
      <Encabezado
        titulo={datos.materia.nombre}
        descripcion={`${datos.materia.profesor} · Ciclo ${datos.materia.ciclo} · ${grupos.length} grupos con la misma materia y distinto avance`}
        acciones={
          <button className="boton-primario" onClick={pedirRecomendaciones} disabled={pensando}>
            {pensando ? "Gemma está analizando…" : "¿Qué sigue para cada grupo?"}
          </button>
        }
      />

      {error && <Aviso tipo="error">{error}</Aviso>}

      {brecha.temas > 0 && (
        <Aviso tipo="alerta">
          <strong className="font-semibold">{brecha.adelantado}</strong> va{" "}
          <strong className="font-semibold">
            {brecha.temas} {brecha.temas === 1 ? "tema" : "temas"}
          </strong>{" "}
          por delante de <strong className="font-semibold">{brecha.rezagado}</strong>. Es la
          misma materia, el mismo profesor y el mismo semestre.
        </Aviso>
      )}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {grupos.map((grupo) => {
          const recomendacion = recomendaciones?.porGrupo?.[grupo.grupo_id];
          return (
            <article key={grupo.grupo_id} className="tarjeta flex flex-col gap-4">
              <header className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-tinta">{grupo.grupo}</h2>
                  <p className="text-xs text-gris">{grupo.horario}</p>
                </div>
                {recomendacion ? (
                  <ChipRiesgo riesgo={recomendacion.riesgo} />
                ) : (
                  <span className="chip bg-hueso text-gris">{grupo.alumnos} alumnos</span>
                )}
              </header>

              <div>
                <div className="mb-1.5 flex items-baseline justify-between">
                  <span className="etiqueta">Avance del plan</span>
                  <span className="text-sm font-semibold text-guinda">
                    {Math.round(grupo.avance * 100)}%
                  </span>
                </div>
                <BarraAvance valor={grupo.avance} />
                <p className="mt-1.5 text-xs text-gris">
                  {grupo.temas_cubiertos} de {grupo.temas_totales} temas ·{" "}
                  {grupo.sesiones_impartidas} sesiones impartidas
                </p>
              </div>

              <dl className="space-y-2 border-t border-borde pt-3 text-sm">
                <div>
                  <dt className="etiqueta">Dónde quedó</dt>
                  <dd className="text-tinta">{grupo.tema_actual?.titulo || "Sin sesiones aún"}</dd>
                </div>
                <div>
                  <dt className="etiqueta">Siguiente pendiente</dt>
                  <dd className="text-tinta">
                    {grupo.siguiente_pendiente?.titulo || "Plan completo"}
                    {grupo.siguiente_pendiente?.nivel === "introducido" && (
                      <span className="ml-2 chip bg-nieve text-guinda-900">quedó a medias</span>
                    )}
                  </dd>
                </div>
              </dl>

              {recomendacion && (
                <div className="rounded-md bg-hueso p-3 text-sm">
                  <p className="etiqueta mb-1">Gemma 4 recomienda</p>
                  <p className="font-medium text-guinda-900">{recomendacion.siguiente_tema}</p>
                  <p className="mt-1 text-gris">{recomendacion.justificacion}</p>
                  {recomendacion.ajuste_sugerido && (
                    <p className="mt-2 border-t border-borde pt-2 text-tinta">
                      {recomendacion.ajuste_sugerido}
                    </p>
                  )}
                </div>
              )}

              <Link
                to="/clase"
                className="boton-secundario mt-auto w-full"
                state={{ grupoId: grupo.grupo_id }}
              >
                Dar clase a este grupo
              </Link>
            </article>
          );
        })}
      </section>

      <section>
        <h2 className="mb-1 text-lg font-semibold text-tinta">Mapa del plan de estudios</h2>
        <p className="mb-4 text-sm text-gris">
          Cada columna es una sección. El mismo temario, tres recorridos distintos.
        </p>

        <div className="overflow-x-auto rounded-lg border border-borde bg-blanco">
          <table className="w-full min-w-[560px] text-sm">
            <thead>
              <tr className="border-b border-borde">
                <th className="px-4 py-3 text-left font-medium text-gris">Tema</th>
                {grupos.map((grupo) => (
                  <th key={grupo.grupo_id} className="w-24 px-3 py-3 font-medium text-guinda">
                    {grupo.grupo}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {temas.map((tema) => (
                <tr key={tema.id} className="border-b border-borde last:border-0">
                  <td className="px-4 py-2.5">
                    <span className="text-tinta">
                      {tema.orden}. {tema.titulo}
                    </span>
                    <span className="ml-2 text-xs text-gris">{tema.unidad}</span>
                  </td>
                  {grupos.map((grupo) => {
                    const celda = grupo.detalle.find((fila) => fila.tema_id === tema.id);
                    const clase = celda?.nivel ? NIVEL_CELDA[celda.nivel] : "bg-hueso";
                    return (
                      <td key={grupo.grupo_id} className="px-3 py-2.5 text-center">
                        <span
                          title={celda?.nivel || "pendiente"}
                          className={`inline-block h-4 w-10 rounded-sm ${clase}`}
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
            <span className="inline-block h-3 w-7 rounded-sm bg-guinda" /> Cubierto
          </span>
          <span className="flex items-center gap-2">
            <span className="inline-block h-3 w-7 rounded-sm border border-guinda-600/40 bg-nieve" />{" "}
            Solo introducido
          </span>
          <span className="flex items-center gap-2">
            <span className="inline-block h-3 w-7 rounded-sm bg-hueso ring-1 ring-borde" />{" "}
            Pendiente
          </span>
        </div>
      </section>
    </div>
  );
}

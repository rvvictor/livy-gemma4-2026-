// Datos y limpieza: la salida de todo lo que entra por visión.
//
// Livy acumula. Un horario mal leído, un temario que Gemma inventó a medias, un
// grupo de prueba que quedó del ensayo: sin una pantalla como esta, el primer
// error de lectura se queda para siempre y el profesor termina desconfiando de
// la bitácora completa.
//
// El orden va de menos a más destructivo, y la zona de riesgo está separada por
// una línea para que nadie llegue ahí por accidente.
import { useState } from "react";

import {
  Aparece,
  Aviso,
  BarraAvance,
  Encabezado,
  Esqueleto,
  useConfirmacion,
} from "../../components/ui.jsx";
import { useCiclo } from "../../estado.jsx";
import { api } from "../../lib/api.js";

export default function Datos() {
  const { ciclo, cargando, recargar } = useCiclo();
  const { pedir, dialogo } = useConfirmacion();
  const [aviso, setAviso] = useState(null);
  const [error, setError] = useState(null);

  /** Ejecuta un borrado, cuenta lo que se fue y vuelve a leer el ciclo. */
  function borrar(peticion, llamada) {
    pedir({
      ...peticion,
      accion: async () => {
        setError(null);
        setAviso(null);
        try {
          const respuesta = await llamada();
          setAviso(respuesta.detalle);
          await recargar();
        } catch (fallo) {
          setError(fallo.message);
        }
      },
    });
  }

  if (cargando || !ciclo) return <Esqueleto filas={4} />;

  const grupos = ciclo.materias.flatMap((materia) =>
    materia.grupos.map((grupo) => ({ ...grupo, materia: materia.nombre })),
  );
  const totalClases = grupos.reduce((suma, grupo) => suma + grupo.sesiones_impartidas, 0);

  return (
    <div className="space-y-10">
      <Encabezado
        titulo="Datos y limpieza"
        descripcion={
          ciclo.materias.length
            ? `${ciclo.materias.length} materias · ${ciclo.total_grupos} secciones · ${totalClases} clases grabadas. Nada de lo que se borra aquí se puede recuperar.`
            : "La base está vacía. Carga tu horario desde la bitácora para empezar."
        }
      />

      {error && <Aviso tipo="error">{error}</Aviso>}
      {aviso && <Aviso tipo="alerta">{aviso}</Aviso>}

      {/* ── Materias ── */}
      {ciclo.materias.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-tinta">Materias</h2>
          <p className="mt-0.5 text-sm text-gris">
            Borrar el plan deja las clases en pie pero pone el avance en cero: sin temas no
            hay contra qué medirlo.
          </p>

          <div className="mt-4 grid gap-4 md:grid-cols-2">
            {ciclo.materias.map((materia, indice) => (
              <Aparece key={materia.id} retraso={indice * 80}>
                <article className="tarjeta flex h-full flex-col">
                  <header className="flex items-start justify-between gap-3">
                    <div>
                      <p className="etiqueta">{materia.clave}</p>
                      <h3 className="mt-0.5 font-semibold text-tinta">{materia.nombre}</h3>
                    </div>
                    <span className="chip bg-nieve text-guinda-900">
                      {Math.round(materia.avance_promedio * 100)}%
                    </span>
                  </header>

                  <p className="mt-3 text-sm text-gris">
                    {materia.temas.length} temas · {materia.grupos.length}{" "}
                    {materia.grupos.length === 1 ? "sección" : "secciones"}
                  </p>

                  <div className="mt-4 flex flex-wrap gap-2 border-t border-borde pt-3">
                    <button
                      className="boton-peligro"
                      disabled={materia.temas.length === 0}
                      onClick={() =>
                        borrar(
                          {
                            titulo: `Borrar el plan de ${materia.nombre}`,
                            cuerpo: `Se eliminan los ${materia.temas.length} temas del temario.`,
                            consecuencias: [
                              "El avance de todas sus secciones vuelve a cero",
                              "Habrá que cargar un temario nuevo y volver a cerrar las clases",
                            ],
                            conserva: [
                              "Las clases grabadas y sus resúmenes se quedan",
                              "Las secciones y su horario se quedan",
                            ],
                            confirmar: "Borrar el plan",
                          },
                          () => api.borrarTemario(materia.id),
                        )
                      }
                    >
                      Borrar plan de estudios
                    </button>

                    <button
                      className="boton-peligro"
                      onClick={() =>
                        borrar(
                          {
                            titulo: `Borrar ${materia.nombre}`,
                            cuerpo:
                              "Se elimina la materia completa y todo lo que cuelga de ella.",
                            consecuencias: [
                              `Sus ${materia.grupos.length} secciones desaparecen`,
                              "Se pierden todas las clases grabadas y sus transcripciones",
                              "Se pierde la bitácora de avance de cada sección",
                            ],
                            confirmar: "Borrar la materia",
                          },
                          () => api.borrarMateria(materia.id),
                        )
                      }
                    >
                      Borrar materia
                    </button>
                  </div>
                </article>
              </Aparece>
            ))}
          </div>
        </section>
      )}

      {/* ── Secciones ── */}
      {grupos.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-tinta">Secciones</h2>
          <p className="mt-0.5 text-sm text-gris">
            Borrar las clases de un grupo lo regresa a cero sin tocar a las demás secciones
            de la misma materia.
          </p>

          <div className="mt-4 space-y-3">
            {grupos.map((grupo, indice) => (
              <Aparece key={grupo.grupo_id} retraso={indice * 60}>
                <article className="tarjeta flex flex-wrap items-center justify-between gap-x-6 gap-y-4">
                  <div className="min-w-[220px] flex-1">
                    <div className="flex items-baseline gap-2">
                      <p className="font-semibold text-tinta">{grupo.grupo}</p>
                      <p className="text-sm text-gris">{grupo.materia}</p>
                    </div>
                    <p className="mt-0.5 text-xs text-gris">
                      {grupo.horario || "Sin horario"} · {grupo.sesiones_impartidas}{" "}
                      {grupo.sesiones_impartidas === 1 ? "clase grabada" : "clases grabadas"}
                    </p>
                    <div className="mt-2 max-w-xs">
                      <BarraAvance valor={grupo.avance} alto="h-1.5" animada={false} />
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      className="boton-peligro"
                      disabled={grupo.sesiones_impartidas === 0}
                      onClick={() =>
                        borrar(
                          {
                            titulo: `Borrar las clases de ${grupo.grupo}`,
                            cuerpo: `Se eliminan las ${grupo.sesiones_impartidas} clases grabadas de esta sección.`,
                            consecuencias: [
                              "Se pierden los resúmenes y las transcripciones",
                              "El avance de la sección vuelve a cero",
                              "Los alumnos dejan de ver esas clases en su portal",
                            ],
                            conserva: [
                              "La sección y su horario se quedan",
                              "Las demás secciones no se tocan",
                            ],
                            confirmar: "Borrar las clases",
                          },
                          () => api.borrarClasesDeGrupo(grupo.grupo_id),
                        )
                      }
                    >
                      Borrar clases
                    </button>

                    <button
                      className="boton-peligro"
                      onClick={() =>
                        borrar(
                          {
                            titulo: `Borrar las dudas de ${grupo.grupo}`,
                            cuerpo:
                              "Se elimina todo lo que los alumnos le preguntaron a Livy en esta sección.",
                            consecuencias: [
                              "El panel de dudas del grupo queda vacío",
                              "Se pierde el registro de dónde se estaban atorando",
                            ],
                            confirmar: "Borrar las dudas",
                          },
                          () => api.borrarDudasDeGrupo(grupo.grupo_id),
                        )
                      }
                    >
                      Borrar dudas
                    </button>

                    <button
                      className="boton-peligro"
                      onClick={() =>
                        borrar(
                          {
                            titulo: `Borrar la sección ${grupo.grupo}`,
                            cuerpo: `Se elimina el grupo de ${grupo.materia} por completo.`,
                            consecuencias: [
                              "Desaparece del horario y de la agenda semanal",
                              `Se pierden sus ${grupo.sesiones_impartidas} clases y su bitácora`,
                              "Se pierden las dudas de sus alumnos",
                            ],
                            confirmar: "Borrar la sección",
                          },
                          () => api.borrarGrupo(grupo.grupo_id),
                        )
                      }
                    >
                      Borrar sección
                    </button>
                  </div>
                </article>
              </Aparece>
            ))}
          </div>
        </section>
      )}

      {/* ── Zona de riesgo ── */}
      <section className="rounded-2xl border border-rojo/25 bg-[#FDECEF]/40 p-5">
        <h2 className="text-lg font-semibold text-rojo">Zona de riesgo</h2>
        <p className="mt-0.5 max-w-2xl text-sm text-gris">
          Estas tres acciones son de golpe. La primera sirve para volver a cargar un horario
          desde cero; las otras dos dejan la base como recién instalada.
        </p>

        <div className="mt-5 space-y-4">
          <FilaDeRiesgo
            titulo="Borrar todo el horario"
            texto="Se van todas las secciones con su bitácora. Las materias y sus planes de estudio se quedan, listos para volver a repartirlos en grupos nuevos."
            boton="Borrar el horario"
            desactivado={grupos.length === 0}
            onClic={() =>
              borrar(
                {
                  titulo: "Borrar todo el horario",
                  cuerpo: `Se eliminan las ${grupos.length} secciones registradas.`,
                  consecuencias: [
                    "Se pierden todas las clases grabadas y su avance",
                    "La agenda semanal queda vacía",
                  ],
                  conserva: ["Las materias y sus planes de estudio se quedan"],
                  confirmar: "Borrar el horario",
                },
                () => api.borrarHorario(),
              )
            }
          />

          <FilaDeRiesgo
            titulo="Volver a los datos de demostración"
            texto="Borra todo lo que hayas cargado y vuelve a sembrar el ciclo de ejemplo: dos materias, cinco secciones y su historial. Es la forma de dejar la aplicación lista para enseñarla."
            boton="Restaurar la demostración"
            onClic={() =>
              borrar(
                {
                  titulo: "Volver a los datos de demostración",
                  cuerpo: "Se borra todo lo tuyo y se siembra el ciclo de ejemplo.",
                  consecuencias: [
                    "Se pierden tus materias, tus grupos y tus clases",
                    "Aparecen las dos materias y las cinco secciones de ejemplo",
                  ],
                  confirmar: "Restaurar",
                },
                () => api.reiniciar(true),
              )
            }
          />

          <FilaDeRiesgo
            titulo="Vaciar la base por completo"
            texto="No queda nada: ni materias, ni grupos, ni clases, ni la demostración. La aplicación arranca en blanco y el vaciado se respeta aunque se reinicie el servidor."
            boton="Vaciar todo"
            onClic={() =>
              borrar(
                {
                  titulo: "Vaciar la base por completo",
                  cuerpo: "Livy queda en blanco. Esto no se puede deshacer.",
                  consecuencias: [
                    "Se pierde absolutamente todo el contenido",
                    "Los alumnos dejan de ver cualquier clase en su portal",
                    "Los datos de demostración tampoco vuelven al reiniciar",
                  ],
                  confirmar: "Vaciar todo",
                },
                () => api.reiniciar(false),
              )
            }
          />
        </div>
      </section>

      {dialogo}
    </div>
  );
}

function FilaDeRiesgo({ titulo, texto, boton, onClic, desactivado }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-borde bg-blanco p-4">
      <div className="min-w-[260px] flex-1">
        <p className="font-medium text-tinta">{titulo}</p>
        <p className="mt-1 text-sm leading-relaxed text-gris">{texto}</p>
      </div>
      <button className="boton-peligro" onClick={onClic} disabled={desactivado}>
        {boton}
      </button>
    </div>
  );
}

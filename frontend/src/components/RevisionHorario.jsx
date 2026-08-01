// Pantalla de revisión del horario leído por Gemma 4.
//
// Igual que con el temario, la propuesta del modelo nunca se guarda sola: el
// profesor la corrige y la firma. Aquí importa más todavía, porque un horario
// mal leído desalinea la agenda de toda la semana.
import { Aparece } from "./ui.jsx";

const DIAS = [
  [1, "L"],
  [2, "M"],
  [3, "M"],
  [4, "J"],
  [5, "V"],
  [6, "S"],
];

export default function RevisionHorario({
  clases,
  editar,
  alternarDia,
  eliminar,
  guardar,
  cancelar,
  guardando,
  fuente,
}) {
  const nuevas = clases.filter((clase) => clase.nueva).length;

  return (
    <Aparece className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-tinta">Revisa tu horario</h2>
          <p className="mt-0.5 text-sm text-gris">
            Gemma leyó {clases.length} {clases.length === 1 ? "clase" : "clases"} desde{" "}
            {fuente === "pdf" ? "el PDF" : "la imagen"}
            {nuevas > 0 && `, ${nuevas} de ellas nuevas`}. Corrige lo que haga falta antes de
            guardar.
          </p>
        </div>
        <div className="flex gap-2">
          <button className="boton-secundario" onClick={cancelar}>
            Descartar
          </button>
          <button className="boton-primario" onClick={guardar} disabled={guardando}>
            {guardando ? "Guardando…" : "Confirmar horario"}
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-guinda-600/25 bg-nieve px-4 py-3 text-sm text-guinda-900">
        Guardar solo <strong className="font-semibold">crea y actualiza</strong>. Ningún grupo
        se borra, porque con él se iría su bitácora de avance.
      </div>

      <div className="overflow-x-auto rounded-2xl border border-borde bg-blanco">
        <table className="w-full min-w-[760px] text-sm">
          <thead>
            <tr className="border-b border-borde text-left">
              <th className="px-3 py-2.5 font-medium text-gris">Materia</th>
              <th className="w-28 px-3 py-2.5 font-medium text-gris">Clave</th>
              <th className="w-24 px-3 py-2.5 font-medium text-gris">Grupo</th>
              <th className="w-52 px-3 py-2.5 font-medium text-gris">Días</th>
              <th className="w-24 px-3 py-2.5 font-medium text-gris">Entra</th>
              <th className="w-24 px-3 py-2.5 font-medium text-gris">Sale</th>
              <th className="w-12 px-3 py-2.5" />
            </tr>
          </thead>
          <tbody>
            {clases.map((clase, indice) => (
              <tr key={indice} className="border-b border-borde last:border-0">
                <td className="px-3 py-2">
                  <input
                    className="w-full rounded-lg border border-transparent bg-transparent px-2 py-1
                               font-medium transition-colors hover:border-borde
                               focus:border-guinda focus:outline-none"
                    value={clase.materia}
                    onChange={(e) => editar(indice, "materia", e.target.value)}
                  />
                  {clase.nueva && (
                    <span className="ml-2 chip bg-nieve text-guinda-900">nueva</span>
                  )}
                </td>
                <td className="px-3 py-2">
                  <input
                    className="w-full rounded-lg border border-transparent bg-transparent px-2 py-1
                               text-gris transition-colors hover:border-borde
                               focus:border-guinda focus:outline-none"
                    value={clase.clave}
                    onChange={(e) => editar(indice, "clave", e.target.value)}
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    className="w-full rounded-lg border border-transparent bg-transparent px-2 py-1
                               transition-colors hover:border-borde focus:border-guinda focus:outline-none"
                    value={clase.grupo}
                    onChange={(e) => editar(indice, "grupo", e.target.value)}
                  />
                </td>
                <td className="px-3 py-2">
                  <div className="flex gap-1">
                    {DIAS.map(([numero, letra], posicion) => {
                      const activo = clase.dias.includes(numero);
                      return (
                        <button
                          key={`${numero}-${posicion}`}
                          onClick={() => alternarDia(indice, numero)}
                          title={`Día ${numero}`}
                          className={`h-7 w-7 rounded-full text-xs font-medium transition-colors duration-200 ${
                            activo
                              ? "bg-guinda text-blanco"
                              : "border border-borde text-gris hover:border-guinda hover:text-guinda"
                          }`}
                        >
                          {letra}
                        </button>
                      );
                    })}
                  </div>
                </td>
                <td className="px-3 py-2">
                  <input
                    type="time"
                    className="w-full rounded-lg border border-transparent bg-transparent px-2 py-1
                               transition-colors hover:border-borde focus:border-guinda focus:outline-none"
                    value={clase.hora_inicio}
                    onChange={(e) => editar(indice, "hora_inicio", e.target.value)}
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    type="time"
                    className="w-full rounded-lg border border-transparent bg-transparent px-2 py-1
                               transition-colors hover:border-borde focus:border-guinda focus:outline-none"
                    value={clase.hora_fin}
                    onChange={(e) => editar(indice, "hora_fin", e.target.value)}
                  />
                </td>
                <td className="px-3 py-2 text-center">
                  <button
                    className="text-gris transition-colors hover:text-rojo"
                    onClick={() => eliminar(indice)}
                    title="Quitar esta clase"
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

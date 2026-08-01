// Índice del portal. El alumno ve sus materias; el profesor ve exactamente lo
// mismo, pero enmarcado como la vista de administrador de lo que reciben sus
// grupos.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Aparece, Aviso, Encabezado, Esqueleto } from "../ui.jsx";
import { api } from "../../lib/api.js";

function fechaLegible(iso) {
  if (!iso) return "sin clases";
  return new Date(`${iso}T12:00:00`).toLocaleDateString("es-MX", {
    day: "numeric",
    month: "long",
  });
}

export default function IndiceGrupos({ modo, base }) {
  const [grupos, setGrupos] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.gruposAlumno().then(setGrupos).catch((fallo) => setError(fallo.message));
  }, []);

  const esProfesor = modo === "profesor";

  return (
    <div>
      <Encabezado
        titulo={esProfesor ? "Portal de alumnos" : "Tus clases"}
        descripcion={
          esProfesor
            ? "Esto es exactamente lo que ven tus alumnos de cada sección, más las dudas que le preguntan a Livy."
            : "Todo lo que se vio en tu grupo, en las palabras de tu propio profesor. Si faltaste, aquí está la clase."
        }
      />

      {error && <Aviso tipo="error">{error}</Aviso>}
      {!grupos ? (
        <Esqueleto filas={3} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {grupos.map((grupo, indice) => (
            <Aparece key={grupo.grupo_id} retraso={indice * 80}>
              <Link to={`${base}/${grupo.grupo_id}`} className="tarjeta-interactiva block h-full">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="etiqueta">{grupo.clave}</p>
                    <h2 className="mt-0.5 text-lg font-semibold text-tinta">{grupo.materia}</h2>
                    <p className="mt-0.5 text-sm text-gris">{grupo.profesor}</p>
                  </div>
                  <span className="chip bg-nieve text-guinda-900">{grupo.grupo}</span>
                </div>

                <div className="mt-5 flex items-end justify-between border-t border-borde pt-3">
                  <div>
                    <p className="text-2xl font-semibold text-guinda">{grupo.clases}</p>
                    <p className="text-xs text-gris">
                      {grupo.clases === 1 ? "clase registrada" : "clases registradas"}
                    </p>
                  </div>
                  <p className="text-right text-xs text-gris">
                    {grupo.horario}
                    <br />
                    Última: {fechaLegible(grupo.ultima_clase)}
                  </p>
                </div>
              </Link>
            </Aparece>
          ))}
        </div>
      )}
    </div>
  );
}

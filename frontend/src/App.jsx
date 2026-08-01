import { NavLink, Navigate, Route, Routes } from "react-router-dom";

import { ProveedorMateria } from "./estado.jsx";
import Bitacora from "./pages/Bitacora.jsx";
import ClaseEnVivo from "./pages/ClaseEnVivo.jsx";
import PortalAlumno from "./pages/PortalAlumno.jsx";
import Temario from "./pages/Temario.jsx";

const SECCIONES = [
  { ruta: "/bitacora", nombre: "Bitácora" },
  { ruta: "/clase", nombre: "Clase en vivo" },
  { ruta: "/temario", nombre: "Plan de estudios" },
  { ruta: "/alumno", nombre: "Portal del alumno" },
];

function Enlace({ ruta, nombre }) {
  return (
    <NavLink
      to={ruta}
      className={({ isActive }) =>
        [
          "border-b-2 px-1 pb-3 pt-1 text-sm font-medium transition",
          isActive
            ? "border-guinda text-guinda"
            : "border-transparent text-gris hover:text-guinda-600",
        ].join(" ")
      }
    >
      {nombre}
    </NavLink>
  );
}

export default function App() {
  return (
    <ProveedorMateria>
      <div className="flex min-h-full flex-col">
        <header className="border-b border-borde bg-blanco">
          <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 pt-5">
            <div className="flex items-baseline gap-3">
              <span className="text-xl font-semibold tracking-tight text-guinda">Livy</span>
              <span className="hidden text-sm text-gris sm:inline">
                Continuidad docente, grupo por grupo
              </span>
            </div>
            <span className="chip bg-nieve text-guinda-900">Gemma 4</span>
          </div>
          <nav className="mx-auto flex max-w-6xl gap-6 overflow-x-auto px-6 pt-4">
            {SECCIONES.map((seccion) => (
              <Enlace key={seccion.ruta} {...seccion} />
            ))}
          </nav>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
          <Routes>
            <Route path="/" element={<Navigate to="/bitacora" replace />} />
            <Route path="/bitacora" element={<Bitacora />} />
            <Route path="/clase" element={<ClaseEnVivo />} />
            <Route path="/temario" element={<Temario />} />
            <Route path="/alumno" element={<PortalAlumno />} />
            <Route path="*" element={<Navigate to="/bitacora" replace />} />
          </Routes>
        </main>

        <footer className="border-t border-borde bg-blanco">
          <div className="mx-auto max-w-6xl px-6 py-5 text-xs text-gris">
            El profesor es el autor. Livy solo propone: cada resumen y cada plan queda
            sujeto a su revisión.
          </div>
        </footer>
      </div>
    </ProveedorMateria>
  );
}

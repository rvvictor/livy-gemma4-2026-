import { Link, NavLink, Navigate, Outlet, Route, Routes } from "react-router-dom";

import ClasesDeGrupo from "./components/portal/ClasesDeGrupo.jsx";
import DetalleDeClase from "./components/portal/DetalleDeClase.jsx";
import IndiceGrupos from "./components/portal/IndiceGrupos.jsx";
import { Logo } from "./components/ui.jsx";
import { ProveedorCiclo } from "./estado.jsx";
import Landing from "./pages/Landing.jsx";
import Bitacora from "./pages/profesor/Bitacora.jsx";
import ClaseEnVivo from "./pages/profesor/ClaseEnVivo.jsx";
import Datos from "./pages/profesor/Datos.jsx";
import PlanDeEstudios from "./pages/profesor/PlanDeEstudios.jsx";

const SECCIONES_PROFESOR = [
  { ruta: "/profesor/bitacora", nombre: "Bitácora" },
  { ruta: "/profesor/clase", nombre: "Clase en vivo" },
  { ruta: "/profesor/plan", nombre: "Plan de estudios" },
  { ruta: "/profesor/alumnos", nombre: "Portal de alumnos" },
  { ruta: "/profesor/datos", nombre: "Datos" },
];

function Marca({ sufijo }) {
  return (
    <Link to="/" className="group flex items-center gap-3">
      <Logo className="h-7 transition-opacity group-hover:opacity-70" />
      {sufijo && <span className="hidden text-sm text-gris sm:inline">{sufijo}</span>}
    </Link>
  );
}

function MarcoProfesor() {
  return (
    <ProveedorCiclo>
      <div className="flex min-h-full flex-col">
        <header className="no-imprimir sticky top-0 z-30 border-b border-borde bg-blanco/85 backdrop-blur-md">
          <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 pt-4">
            <Marca sufijo="Continuidad docente, grupo por grupo" />
            <div className="flex items-center gap-2">
              <span className="chip bg-hueso text-gris">Vista del profesor</span>
              <span className="chip bg-nieve text-guinda-900">Gemma 4</span>
            </div>
          </div>
          <nav className="mx-auto flex max-w-6xl gap-7 overflow-x-auto px-6 pt-3.5">
            {SECCIONES_PROFESOR.map((seccion) => (
              <NavLink
                key={seccion.ruta}
                to={seccion.ruta}
                className={({ isActive }) =>
                  [
                    "relative whitespace-nowrap border-b-2 px-0.5 pb-3 pt-1 text-sm font-medium transition-colors duration-200",
                    isActive
                      ? "border-guinda text-guinda"
                      : "border-transparent text-gris hover:text-guinda-600",
                  ].join(" ")
                }
              >
                {seccion.nombre}
              </NavLink>
            ))}
          </nav>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
          <Outlet />
        </main>

        <footer className="no-imprimir border-t border-borde bg-blanco">
          <div className="mx-auto max-w-6xl px-6 py-5 text-xs text-gris">
            El profesor es el autor. Livy solo propone: cada resumen y cada plan queda sujeto
            a su revisión.
          </div>
        </footer>
      </div>
    </ProveedorCiclo>
  );
}

function MarcoAlumno() {
  return (
    <div className="flex min-h-full flex-col">
      <header className="no-imprimir sticky top-0 z-30 border-b border-borde bg-blanco/85 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-6 py-4">
          <div className="flex items-center gap-2.5">
            <Marca />
            <span className="chip bg-nieve text-guinda-900">Portal del alumno</span>
          </div>
          <Link to="/alumno" className="boton-fantasma">
            Mis materias
          </Link>
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-8">
        <Outlet />
      </main>

      <footer className="no-imprimir border-t border-borde bg-blanco">
        <div className="mx-auto max-w-5xl px-6 py-5 text-xs text-gris">
          Las respuestas se basan en las clases que tu profesor impartió a tu grupo. Si algo no
          se vio en clase, Livy te lo dice en vez de inventarlo.
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />

      {/* Vista del profesor */}
      <Route path="/profesor" element={<MarcoProfesor />}>
        <Route index element={<Navigate to="/profesor/bitacora" replace />} />
        <Route path="bitacora" element={<Bitacora />} />
        <Route path="clase" element={<ClaseEnVivo />} />
        <Route path="plan" element={<PlanDeEstudios />} />
        <Route path="datos" element={<Datos />} />
        {/* El portal de alumnos, visto desde la administración */}
        <Route
          path="alumnos"
          element={<IndiceGrupos modo="profesor" base="/profesor/alumnos" />}
        />
        <Route
          path="alumnos/clase/:sesionId"
          element={<DetalleDeClase modo="profesor" base="/profesor/alumnos" />}
        />
        <Route
          path="alumnos/:grupoId"
          element={<ClasesDeGrupo modo="profesor" base="/profesor/alumnos" />}
        />
      </Route>

      {/* Vista del alumno */}
      <Route path="/alumno" element={<MarcoAlumno />}>
        <Route index element={<IndiceGrupos modo="alumno" base="/alumno" />} />
        <Route
          path="clase/:sesionId"
          element={<DetalleDeClase modo="alumno" base="/alumno" />}
        />
        <Route path=":grupoId" element={<ClasesDeGrupo modo="alumno" base="/alumno" />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

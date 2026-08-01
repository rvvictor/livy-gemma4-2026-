// Estado compartido mínimo: la materia del profesor y sus grupos.
// Un solo contexto evita que cada pantalla vuelva a pedir lo mismo, lo que
// importa cuando el tier gratuito de la API limita a 15 solicitudes por minuto.
import { createContext, useCallback, useContext, useEffect, useState } from "react";

import { api } from "./lib/api.js";

const ContextoMateria = createContext(null);

export function ProveedorMateria({ children }) {
  const [materia, setMateria] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  const recargar = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      const materias = await api.materias();
      if (!materias.length) {
        setMateria(null);
        return;
      }
      setMateria(await api.materia(materias[0].id));
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    recargar();
  }, [recargar]);

  return (
    <ContextoMateria.Provider value={{ materia, cargando, error, recargar }}>
      {children}
    </ContextoMateria.Provider>
  );
}

export function useMateria() {
  const contexto = useContext(ContextoMateria);
  if (!contexto) throw new Error("useMateria debe usarse dentro de ProveedorMateria");
  return contexto;
}

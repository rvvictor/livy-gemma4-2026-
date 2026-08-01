// Estado compartido: el ciclo completo del profesor —todas sus materias, sus
// grupos y el avance de cada uno—. Un solo contexto evita que cada pantalla
// vuelva a pedir lo mismo, lo que importa cuando el tier gratuito de la API
// limita a 15 solicitudes por minuto.
import { createContext, useCallback, useContext, useEffect, useState } from "react";

import { api } from "./lib/api.js";

const ContextoCiclo = createContext(null);

export function ProveedorCiclo({ children }) {
  const [ciclo, setCiclo] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  const recargar = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      setCiclo(await api.ciclo());
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
    <ContextoCiclo.Provider value={{ ciclo, cargando, error, recargar }}>
      {children}
    </ContextoCiclo.Provider>
  );
}

export function useCiclo() {
  const contexto = useContext(ContextoCiclo);
  if (!contexto) throw new Error("useCiclo debe usarse dentro de ProveedorCiclo");
  return contexto;
}

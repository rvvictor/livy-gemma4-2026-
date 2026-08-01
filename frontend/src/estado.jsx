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

/**
 * El ciclo cuando puede no haberlo.
 *
 * Las pantallas del portal se montan en dos sitios: dentro de la vista del
 * profesor —donde el ciclo existe y hay que refrescarlo al borrar algo— y en la
 * del alumno, que no lo tiene. Devuelve `null` en lugar de reventar.
 */
export function useCicloOpcional() {
  return useContext(ContextoCiclo);
}

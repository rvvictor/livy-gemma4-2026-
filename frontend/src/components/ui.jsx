// Piezas visuales compartidas. Se mantienen juntas para que la paleta y las
// animaciones se apliquen de forma consistente en todas las pantallas.
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

import iconoLivy from "../img/livy-icono.png";
import marcaLivy from "../img/livy-marca.png";

/**
 * Logotipo completo. Se recortó el fondo del original a transparencia para que
 * se apoye igual de bien sobre el blanco de las cabeceras que sobre el hueso.
 */
export function Logo({ className = "h-7" }) {
  return (
    <img
      src={marcaLivy}
      alt="Livy"
      draggable={false}
      className={`${className} w-auto select-none`}
    />
  );
}

/** Solo las tres barras: para los espacios donde el nombre ya está escrito. */
export function Isotipo({ className = "h-6" }) {
  return (
    <img src={iconoLivy} alt="" aria-hidden draggable={false} className={`${className} w-auto`} />
  );
}

/** Envoltorio que hace aparecer su contenido con un retraso escalonado. */
export function Aparece({ retraso = 0, children, className = "", como: Como = "div", ...resto }) {
  return (
    <Como
      className={`aparece ${className}`}
      style={{ animationDelay: `${retraso}ms` }}
      {...resto}
    >
      {children}
    </Como>
  );
}

export function BarraAvance({ valor, alto = "h-2", animada = true }) {
  const porcentaje = Math.min(100, Math.max(0, Math.round(valor * 100)));
  return (
    <div className={`${alto} w-full overflow-hidden rounded-full bg-nieve`}>
      <div
        className={`h-full rounded-full bg-guinda transition-[width] duration-700 ${
          animada ? "barra-crece" : ""
        }`}
        style={{ width: `${porcentaje}%` }}
      />
    </div>
  );
}

const ESTILOS_RIESGO = {
  al_dia: "bg-nieve text-guinda-900",
  atencion: "bg-[#FDF1E3] text-[#8A5008]",
  rezagado: "bg-rojo text-blanco",
};

const TEXTOS_RIESGO = {
  al_dia: "Al día",
  atencion: "Requiere atención",
  rezagado: "Rezagado",
};

export function ChipRiesgo({ riesgo }) {
  if (!riesgo) return null;
  return (
    <span className={`chip ${ESTILOS_RIESGO[riesgo] || ESTILOS_RIESGO.atencion}`}>
      {TEXTOS_RIESGO[riesgo] || riesgo}
    </span>
  );
}

export function Aviso({ tipo = "info", children }) {
  const estilos = {
    info: "border-borde bg-blanco text-gris",
    alerta: "border-guinda-600/25 bg-nieve text-guinda-900",
    error: "border-rojo/25 bg-[#FDECEF] text-rojo",
  };
  return (
    <div className={`desvanece rounded-xl border px-4 py-3 text-sm ${estilos[tipo]}`}>
      {children}
    </div>
  );
}

export function Cargando({ texto = "Cargando…" }) {
  return (
    <div className="flex items-center gap-2 py-8 text-sm text-gris">
      <span className="latido inline-block h-2 w-2 rounded-full bg-guinda" />
      {texto}
    </div>
  );
}

/** Bloques grises con brillo, para no dejar la pantalla vacía mientras carga. */
export function Esqueleto({ filas = 3, className = "" }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: filas }).map((_, indice) => (
        <div
          key={indice}
          className="esqueleto h-20 rounded-2xl"
          style={{ animationDelay: `${indice * 120}ms` }}
        />
      ))}
    </div>
  );
}

export function Encabezado({ titulo, descripcion, acciones }) {
  return (
    <Aparece className="mb-7 flex flex-wrap items-end justify-between gap-4 border-b border-borde pb-5">
      <div>
        <h1 className="text-[26px] font-semibold leading-tight tracking-tight text-tinta">
          {titulo}
        </h1>
        {descripcion && <p className="mt-1.5 max-w-2xl text-sm text-gris">{descripcion}</p>}
      </div>
      {acciones && <div className="flex flex-wrap gap-2">{acciones}</div>}
    </Aparece>
  );
}

/**
 * Confirmación para todo lo que borra.
 *
 * Ninguna acción destructiva de Livy se ejecuta al primer clic: lo que se pierde
 * —la bitácora de un grupo, la memoria de una clase— no se puede reconstruir sin
 * volver a dar la clase. El diálogo enumera las consecuencias por escrito antes
 * de dejar confirmar.
 *
 * Se usa a través de `useConfirmacion`, que devuelve la función para pedirla y el
 * diálogo ya cableado para colgarlo al final de la pantalla.
 */
export function useConfirmacion() {
  const [peticion, setPeticion] = useState(null);
  const [trabajando, setTrabajando] = useState(false);

  async function confirmar() {
    if (!peticion) return;
    setTrabajando(true);
    try {
      await peticion.accion();
    } finally {
      setTrabajando(false);
      setPeticion(null);
    }
  }

  return {
    pedir: setPeticion,
    dialogo: (
      <DialogoConfirmar
        peticion={peticion}
        trabajando={trabajando}
        onConfirmar={confirmar}
        onCancelar={() => !trabajando && setPeticion(null)}
      />
    ),
  };
}

function DialogoConfirmar({ peticion, trabajando, onConfirmar, onCancelar }) {
  useEffect(() => {
    if (!peticion) return undefined;
    const alTeclear = (evento) => evento.key === "Escape" && onCancelar();
    document.addEventListener("keydown", alTeclear);
    return () => document.removeEventListener("keydown", alTeclear);
  }, [peticion, onCancelar]);

  if (!peticion) return null;

  return createPortal(
    <div
      className="desvanece fixed inset-0 z-50 flex items-center justify-center bg-tinta/40 p-4 backdrop-blur-sm"
      onMouseDown={(evento) => evento.target === evento.currentTarget && onCancelar()}
    >
      <div
        role="alertdialog"
        aria-modal="true"
        aria-label={peticion.titulo}
        className="aparece w-full max-w-md rounded-2xl border border-borde bg-blanco p-6
                   shadow-[0_30px_80px_-30px_rgba(26,20,22,0.55)]"
      >
        <h2 className="text-lg font-semibold tracking-tight text-tinta">{peticion.titulo}</h2>
        {peticion.cuerpo && (
          <p className="mt-2 text-sm leading-relaxed text-gris">{peticion.cuerpo}</p>
        )}

        {peticion.consecuencias?.length > 0 && (
          <ul className="mt-4 space-y-1.5 rounded-xl bg-[#FDECEF] px-4 py-3 text-sm text-rojo">
            {peticion.consecuencias.map((consecuencia) => (
              <li key={consecuencia} className="flex gap-2">
                <span aria-hidden>·</span>
                {consecuencia}
              </li>
            ))}
          </ul>
        )}

        {peticion.conserva?.length > 0 && (
          <ul className="mt-2 space-y-1.5 rounded-xl bg-hueso px-4 py-3 text-sm text-gris">
            {peticion.conserva.map((detalle) => (
              <li key={detalle} className="flex gap-2">
                <span aria-hidden>·</span>
                {detalle}
              </li>
            ))}
          </ul>
        )}

        <div className="mt-6 flex justify-end gap-2">
          <button className="boton-secundario" onClick={onCancelar} disabled={trabajando}>
            Cancelar
          </button>
          <button
            className="boton-peligro-solido"
            onClick={onConfirmar}
            disabled={trabajando}
            autoFocus
          >
            {trabajando ? "Borrando…" : peticion.confirmar || "Borrar"}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}

/** Render mínimo de Markdown: suficiente para las respuestas del modelo. */
export function TextoRico({ contenido, className = "" }) {
  const lineas = (contenido || "").split("\n");
  return (
    <div className={`space-y-2 text-sm leading-relaxed text-tinta ${className}`}>
      {lineas.map((linea, indice) => {
        const limpia = linea.trim();
        if (!limpia) return null;
        if (limpia.startsWith("### ")) {
          return (
            <h3 key={indice} className="pt-2 font-semibold text-guinda">
              {limpia.slice(4)}
            </h3>
          );
        }
        if (limpia.startsWith("## ")) {
          return (
            <h2 key={indice} className="pt-2 text-base font-semibold text-guinda">
              {limpia.slice(3)}
            </h2>
          );
        }
        if (limpia.startsWith("# ")) {
          return (
            <h2 key={indice} className="pt-2 text-base font-semibold text-guinda">
              {limpia.slice(2)}
            </h2>
          );
        }
        if (/^[-*]\s/.test(limpia)) {
          return (
            <div key={indice} className="flex gap-2 pl-1">
              <span className="mt-0.5 text-guinda-600">•</span>
              <span>{enfatizar(limpia.slice(2))}</span>
            </div>
          );
        }
        if (/^\d+\.\s/.test(limpia)) {
          const [numero, ...resto] = limpia.split(/\.\s(.+)/);
          return (
            <div key={indice} className="flex gap-2 pl-1">
              <span className="font-medium text-guinda-600">{numero}.</span>
              <span>{enfatizar(resto.join(""))}</span>
            </div>
          );
        }
        return <p key={indice}>{enfatizar(limpia)}</p>;
      })}
    </div>
  );
}

function enfatizar(texto) {
  return String(texto)
    .split(/(\*\*[^*]+\*\*|`[^`]+`)/g)
    .map((parte, indice) => {
      if (parte.startsWith("**") && parte.endsWith("**")) {
        return (
          <strong key={indice} className="font-semibold text-guinda-900">
            {parte.slice(2, -2)}
          </strong>
        );
      }
      if (parte.startsWith("`") && parte.endsWith("`") && parte.length > 2) {
        return (
          <code key={indice} className="rounded bg-nieve px-1.5 py-0.5 font-mono text-[13px]">
            {parte.slice(1, -1)}
          </code>
        );
      }
      return <span key={indice}>{parte}</span>;
    });
}

/** Burbuja de conversación reutilizada por los tres chats de la aplicación. */
export function Burbuja({ rol, children }) {
  const esPersona = rol === "alumno" || rol === "profesor";
  return (
    <Aparece
      className={
        esPersona
          ? "ml-auto max-w-[85%] rounded-2xl rounded-br-md bg-guinda px-4 py-2.5 text-sm text-blanco"
          : "mr-auto max-w-[92%] rounded-2xl rounded-bl-md bg-hueso px-4 py-3"
      }
    >
      {children}
    </Aparece>
  );
}

/** Tres puntos que respiran mientras el modelo redacta. */
export function Escribiendo({ texto = "Gemma está pensando" }) {
  return (
    <div className="mr-auto flex items-center gap-2 rounded-2xl rounded-bl-md bg-hueso px-4 py-3 text-sm text-gris">
      <span className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="latido inline-block h-1.5 w-1.5 rounded-full bg-guinda-600"
            style={{ animationDelay: `${i * 180}ms` }}
          />
        ))}
      </span>
      {texto}
    </div>
  );
}

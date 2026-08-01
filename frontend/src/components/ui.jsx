// Piezas visuales compartidas. Se mantienen juntas para que la paleta y las
// animaciones se apliquen de forma consistente en todas las pantallas.

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

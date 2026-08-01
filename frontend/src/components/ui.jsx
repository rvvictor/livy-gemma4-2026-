// Piezas visuales compartidas. Se mantienen juntas para que la paleta se aplique
// de forma consistente en las cuatro pantallas sin repetir clases sueltas.

export function BarraAvance({ valor, alto = "h-2" }) {
  const porcentaje = Math.min(100, Math.max(0, Math.round(valor * 100)));
  return (
    <div className={`${alto} w-full overflow-hidden rounded-full bg-nieve`}>
      <div
        className="h-full rounded-full bg-guinda transition-[width] duration-700"
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
    alerta: "border-guinda-600/30 bg-nieve text-guinda-900",
    error: "border-rojo/30 bg-[#FDECEF] text-rojo",
  };
  return (
    <div className={`rounded-md border px-4 py-3 text-sm ${estilos[tipo]}`}>{children}</div>
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

export function Encabezado({ titulo, descripcion, acciones }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4 border-b border-borde pb-5">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-tinta">{titulo}</h1>
        {descripcion && <p className="mt-1 max-w-2xl text-sm text-gris">{descripcion}</p>}
      </div>
      {acciones && <div className="flex flex-wrap gap-2">{acciones}</div>}
    </div>
  );
}

/** Render mínimo de Markdown: suficiente para las respuestas del modelo. */
export function TextoRico({ contenido }) {
  const lineas = (contenido || "").split("\n");
  return (
    <div className="space-y-2 text-sm leading-relaxed text-tinta">
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
        if (limpia.startsWith("- ") || limpia.startsWith("* ")) {
          return (
            <div key={indice} className="flex gap-2 pl-1">
              <span className="text-guinda-600">•</span>
              <span>{enfatizar(limpia.slice(2))}</span>
            </div>
          );
        }
        return <p key={indice}>{enfatizar(limpia)}</p>;
      })}
    </div>
  );
}

function enfatizar(texto) {
  return texto.split(/(\*\*[^*]+\*\*)/g).map((parte, indice) =>
    parte.startsWith("**") && parte.endsWith("**") ? (
      <strong key={indice} className="font-semibold text-guinda-900">
        {parte.slice(2, -2)}
      </strong>
    ) : (
      <span key={indice}>{parte}</span>
    ),
  );
}

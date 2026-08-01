// Piezas compartidas entre el portal del alumno y la vista de administrador que
// el profesor tiene del mismo portal. La única diferencia entre ambos es el
// panel lateral: el alumno pregunta, el profesor lee lo que preguntaron.
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

import {
  Aparece,
  Burbuja,
  Escribiendo,
  TextoRico,
} from "../ui.jsx";

/** Flecha de regreso, presente en todas las vistas anidadas del portal. */
export function Regresar({ a, children }) {
  return (
    <Link
      to={a}
      className="group inline-flex items-center gap-1.5 text-sm text-gris transition-colors hover:text-guinda"
    >
      <span className="transition-transform duration-200 group-hover:-translate-x-0.5">←</span>
      {children}
    </Link>
  );
}

/** Panel de solo lectura con lo que los alumnos preguntaron. */
export function PanelDudas({ dudas, titulo, descripcion }) {
  const [abierta, setAbierta] = useState(null);

  return (
    <div className="tarjeta">
      <p className="etiqueta">{titulo}</p>
      <p className="mt-1 text-xs leading-relaxed text-gris">{descripcion}</p>

      <div className="mt-4 space-y-3">
        {dudas.length === 0 && (
          <p className="text-sm text-gris">Todavía nadie ha preguntado nada por aquí.</p>
        )}

        {dudas.map((duda, indice) => (
          <Aparece
            key={duda.id}
            retraso={indice * 60}
            className="border-l-2 border-nieve pl-3 transition-colors hover:border-guinda"
          >
            <button
              className="w-full text-left"
              onClick={() => setAbierta(abierta === duda.id ? null : duda.id)}
            >
              <p className="text-sm leading-snug text-tinta">{duda.contenido}</p>
              {duda.respuesta && (
                <span className="mt-1 inline-block text-xs text-guinda-600">
                  {abierta === duda.id ? "Ocultar respuesta" : "Ver qué se le respondió"}
                </span>
              )}
            </button>

            {abierta === duda.id && duda.respuesta && (
              <Aparece className="mt-2 rounded-xl bg-hueso p-3">
                <TextoRico contenido={duda.respuesta} />
              </Aparece>
            )}
          </Aparece>
        ))}
      </div>
    </div>
  );
}

/** Chat reutilizado por los dos alcances: todo el curso o una sola clase. */
export function PanelChat({
  titulo,
  descripcion,
  mensajes,
  pensando,
  onEnviar,
  sugerencias = [],
  textoPensando = "Buscando en tus clases",
  marcador = "Escribe tu duda…",
}) {
  const [borrador, setBorrador] = useState("");
  const fin = useRef(null);

  useEffect(() => {
    fin.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [mensajes, pensando]);

  function enviar(evento, texto) {
    evento?.preventDefault();
    const contenido = (texto ?? borrador).trim();
    if (!contenido || pensando) return;
    setBorrador("");
    onEnviar(contenido);
  }

  return (
    <div className="tarjeta flex h-full flex-col">
      <header className="border-b border-borde pb-3">
        <h2 className="font-semibold text-tinta">{titulo}</h2>
        <p className="mt-1 text-xs leading-relaxed text-gris">{descripcion}</p>
      </header>

      <div className="flex-1 space-y-3 overflow-y-auto py-4">
        {mensajes.length === 0 && (
          <div className="space-y-3">
            <p className="text-sm text-gris">Puedes empezar por aquí:</p>
            <div className="flex flex-wrap gap-2">
              {sugerencias.map((sugerencia, indice) => (
                <Aparece key={sugerencia} retraso={indice * 80} como="span">
                  <button
                    className="boton-secundario text-xs"
                    onClick={(evento) => enviar(evento, sugerencia)}
                  >
                    {sugerencia}
                  </button>
                </Aparece>
              ))}
            </div>
          </div>
        )}

        {mensajes.map((mensaje, indice) => (
          <Burbuja key={indice} rol={mensaje.rol}>
            {mensaje.rol === "alumno" ? (
              mensaje.contenido
            ) : (
              <TextoRico contenido={mensaje.contenido} />
            )}
          </Burbuja>
        ))}

        {pensando && <Escribiendo texto={textoPensando} />}
        <div ref={fin} />
      </div>

      <form onSubmit={enviar} className="flex items-end gap-2 border-t border-borde pt-3">
        <input
          className="campo rounded-full"
          placeholder={marcador}
          value={borrador}
          onChange={(evento) => setBorrador(evento.target.value)}
        />
        <button
          className="boton-primario h-10 w-10 shrink-0 rounded-full p-0"
          disabled={pensando || !borrador.trim()}
          aria-label="Enviar"
        >
          ↑
        </button>
      </form>
    </div>
  );
}

/**
 * Guía de estudio a pantalla completa dentro de la misma página.
 *
 * El botón de descarga usa el diálogo de impresión del navegador contra una hoja
 * de estilos dedicada: el PDF resultante conserva el texto seleccionable y se
 * pagina solo, sin arrastrar una librería de generación de PDF al paquete.
 */
export function VistaGuia({ guia, materia, grupo, profesor, onCerrar }) {
  const fecha = new Date().toLocaleDateString("es-MX", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <Aparece>
      <div className="no-imprimir mb-5 flex flex-wrap items-center justify-between gap-3">
        <button className="boton-fantasma" onClick={onCerrar}>
          ← Volver a las clases
        </button>
        <button className="boton-primario" onClick={() => window.print()}>
          Descargar en PDF
        </button>
      </div>

      <article className="imprimible tarjeta">
        <header className="mb-6 border-b border-borde pb-4">
          <p className="etiqueta">Guía de estudio</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-tinta">{materia}</h1>
          <p className="mt-1 text-sm text-gris">
            Grupo {grupo} · {profesor} · Generada el {fecha}
          </p>
          <p className="mt-3 text-xs text-gris">
            Construida con Gemma 4 a partir de las clases que este grupo realmente recibió. No
            incluye temas que la sección todavía no ha visto.
          </p>
        </header>

        <TextoRico contenido={guia} className="text-[15px] leading-[1.8]" />
      </article>
    </Aparece>
  );
}

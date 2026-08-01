// Portada. Cuenta el problema antes que el producto: el jurado y cualquier
// profesor deben entender en diez segundos qué se rompe hoy y qué arregla Livy.
import { Link } from "react-router-dom";

import { Aparece, Isotipo, Logo } from "../components/ui.jsx";

const GRUPOS_DEMO = [
  { nombre: "1CV1", avance: 0.58, nota: "Cálculo de límites", tono: "bg-guinda" },
  { nombre: "2CV2", avance: 0.42, nota: "Perdió una sesión por el puente", tono: "bg-guinda-600" },
  { nombre: "3CV3", avance: 0.53, nota: "Tema a medias por el simulacro", tono: "bg-guinda-300" },
];

const CIFRAS = [
  { dato: "52%", texto: "del tiempo docente se dedica realmente a enseñar", fuente: "OECD TALIS 2024" },
  { dato: "44%", texto: "de los maestros reporta desgaste constante", fuente: "K-12, 2024" },
  { dato: "5.9 h", texto: "por semana recupera quien usa IA de forma habitual", fuente: "Gallup 2025" },
];

const PASOS = [
  {
    numero: "01",
    titulo: "Da tu clase como siempre",
    texto:
      "Livy escucha en segundo plano. No hay que cambiar la forma de enseñar ni preparar nada distinto.",
  },
  {
    numero: "02",
    titulo: "La sesión se vuelve memoria",
    texto:
      "Al cerrar, Gemma 4 convierte lo dicho en un resumen estructurado y marca qué temas del plan se cubrieron.",
  },
  {
    numero: "03",
    titulo: "Cada grupo avanza por separado",
    texto:
      "La bitácora de esa sección se mueve sola. Las demás no se tocan, porque no vieron lo mismo.",
  },
];

const USOS_GEMMA = [
  ["Visión", "Lee el temario de una foto o un PDF y lo vuelve un plan ordenado"],
  ["Razonamiento", "Convierte la transcripción cruda en memoria estructurada"],
  ["Salida estructurada", "Marca cada tema como introducido, cubierto o reforzado"],
  ["Contexto de 256K", "El semestre completo del grupo cabe entero: sin RAG ni vectores"],
];

export default function Landing() {
  return (
    <div className="min-h-full bg-blanco">
      <header className="sticky top-0 z-30 border-b border-borde bg-blanco/85 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Logo className="h-7" />
          <nav className="flex items-center gap-2">
            <Link to="/alumno" className="boton-fantasma">
              Soy alumno
            </Link>
            <Link to="/profesor" className="boton-primario">
              Entrar como profesor
            </Link>
          </nav>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="relative overflow-hidden border-b border-borde">
        <div
          aria-hidden
          className="pointer-events-none absolute -right-40 -top-40 h-[520px] w-[520px] rounded-full
                     bg-[radial-gradient(circle,rgba(109,26,54,0.08),transparent_65%)]"
        />
        <div className="mx-auto grid max-w-6xl gap-14 px-6 py-20 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:py-28">
          <div>
            <Aparece
              como="span"
              className="chip border border-borde bg-hueso text-guinda-900"
              retraso={0}
            >
              Hackday Gemma 4 · GDG CDMX
            </Aparece>

            <Aparece retraso={80}>
              <h1 className="mt-5 text-[42px] font-semibold leading-[1.08] tracking-tight text-tinta sm:text-[56px]">
                Das la misma clase
                <br />
                <span className="text-guinda">a seis grupos distintos.</span>
                <br />
                ¿En cuál ibas?
              </h1>
            </Aparece>

            <Aparece retraso={160}>
              <p className="mt-6 max-w-xl text-lg leading-relaxed text-gris">
                Livy convierte cada sesión en memoria estructurada y lleva la bitácora de
                avance <strong className="font-semibold text-tinta">de cada sección por
                separado</strong> contra tu plan de estudios. Si faltas un día, el hilo no se
                pierde.
              </p>
            </Aparece>

            <Aparece retraso={240} className="mt-9 flex flex-wrap gap-3">
              <Link to="/profesor" className="boton-primario px-6 py-3">
                Ver la bitácora en acción
              </Link>
              <Link to="/alumno" className="boton-secundario px-6 py-3">
                Entrar como alumno
              </Link>
            </Aparece>

            <Aparece retraso={320}>
              <p className="mt-5 text-xs text-gris">
                Prototipo con datos de demostración · Construido sobre los modelos abiertos
                Gemma 4
              </p>
            </Aparece>
          </div>

          {/* Retrato del problema: tres secciones, tres puntos distintos del plan. */}
          <Aparece retraso={200}>
            <div className="tarjeta shadow-[0_24px_70px_-40px_rgba(26,20,22,0.45)]">
              <div className="mb-5 flex items-baseline justify-between">
                <div>
                  <p className="etiqueta">Cálculo Diferencial</p>
                  <p className="text-sm text-gris">Un profesor · tres secciones</p>
                </div>
                <span className="chip bg-nieve text-guinda-900">Ciclo 2026/1</span>
              </div>

              <div className="space-y-5">
                {GRUPOS_DEMO.map((grupo, indice) => (
                  <Aparece key={grupo.nombre} retraso={360 + indice * 110}>
                    <div className="flex items-baseline justify-between text-sm">
                      <span className="font-medium text-tinta">{grupo.nombre}</span>
                      <span className="font-semibold text-guinda">
                        {Math.round(grupo.avance * 100)}%
                      </span>
                    </div>
                    <div className="mt-1.5 h-2.5 w-full overflow-hidden rounded-full bg-nieve">
                      <div
                        className={`barra-crece h-full rounded-full ${grupo.tono}`}
                        style={{
                          width: `${grupo.avance * 100}%`,
                          animationDelay: `${500 + indice * 140}ms`,
                        }}
                      />
                    </div>
                    <p className="mt-1.5 text-xs text-gris">{grupo.nota}</p>
                  </Aparece>
                ))}
              </div>

              <Aparece retraso={800}>
                <p className="mt-6 border-t border-borde pt-4 text-sm text-guinda-900">
                  <strong className="font-semibold">Dos temas de diferencia</strong> entre la
                  sección más adelantada y la más atrasada. Misma materia, mismo semestre.
                </p>
              </Aparece>
            </div>
          </Aparece>
        </div>
      </section>

      {/* ── El problema en cifras ── */}
      <section className="border-b border-borde bg-hueso">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <Aparece>
            <h2 className="max-w-2xl text-2xl font-semibold tracking-tight text-tinta sm:text-3xl">
              El tiempo del profesor se consume en todo menos en enseñar
            </h2>
          </Aparece>

          <div className="mt-10 grid gap-5 sm:grid-cols-3">
            {CIFRAS.map((cifra, indice) => (
              <Aparece key={cifra.dato} retraso={indice * 100}>
                <div className="tarjeta h-full">
                  <p className="text-4xl font-semibold tracking-tight text-guinda">{cifra.dato}</p>
                  <p className="mt-2 text-sm leading-relaxed text-tinta">{cifra.texto}</p>
                  <p className="mt-3 text-xs text-gris">{cifra.fuente}</p>
                </div>
              </Aparece>
            ))}
          </div>

          <Aparece retraso={340}>
            <p className="mt-10 max-w-3xl text-base leading-relaxed text-gris">
              Pero el hueco que nadie resuelve es otro. Las herramientas que ya existen
              documentan clases <em>aisladas</em>. Ninguna lleva la continuidad{" "}
              <strong className="font-semibold text-tinta">
                entre secciones paralelas a lo largo del tiempo
              </strong>
              . Ese seguimiento vive hoy en la cabeza del profesor, en una libreta, o
              simplemente se pierde.
            </p>
          </Aparece>
        </div>
      </section>

      {/* ── Cómo funciona ── */}
      <section className="border-b border-borde">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <Aparece>
            <p className="etiqueta">Cómo funciona</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-tinta sm:text-3xl">
              Tres pasos, ninguno extra para el profesor
            </h2>
          </Aparece>

          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {PASOS.map((paso, indice) => (
              <Aparece key={paso.numero} retraso={indice * 110}>
                <div className="tarjeta-interactiva h-full">
                  <span className="font-mono text-sm text-guinda-300">{paso.numero}</span>
                  <h3 className="mt-3 text-lg font-semibold text-tinta">{paso.titulo}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-gris">{paso.texto}</p>
                </div>
              </Aparece>
            ))}
          </div>
        </div>
      </section>

      {/* ── Gemma 4 ── */}
      <section className="border-b border-borde bg-hueso">
        <div className="mx-auto grid max-w-6xl gap-10 px-6 py-16 lg:grid-cols-[0.9fr_1.1fr]">
          <Aparece>
            <p className="etiqueta">El motor</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-tinta sm:text-3xl">
              Gemma 4 hace el trabajo cognitivo completo
            </h2>
            <p className="mt-4 text-base leading-relaxed text-gris">
              No es un accesorio conectado al final. Cada función del producto —leer el
              temario, entender la clase, ubicarla en el plan, recomendar qué sigue por
              sección— depende del modelo.
            </p>
          </Aparece>

          <div className="grid gap-4 sm:grid-cols-2">
            {USOS_GEMMA.map(([capacidad, uso], indice) => (
              <Aparece key={capacidad} retraso={indice * 90}>
                <div className="tarjeta h-full">
                  <p className="text-sm font-semibold text-guinda">{capacidad}</p>
                  <p className="mt-1.5 text-sm leading-relaxed text-gris">{uso}</p>
                </div>
              </Aparece>
            ))}
          </div>
        </div>
      </section>

      {/* ── Cierre ── */}
      <section>
        <div className="mx-auto max-w-6xl px-6 py-20 text-center">
          <Aparece>
            <h2 className="mx-auto max-w-2xl text-3xl font-semibold leading-tight tracking-tight text-tinta">
              La clase ocurre una vez.
              <br />
              <span className="text-guinda">Con Livy, queda.</span>
            </h2>
          </Aparece>
          <Aparece retraso={120} className="mt-8 flex flex-wrap justify-center gap-3">
            <Link to="/profesor" className="boton-primario px-6 py-3">
              Entrar como profesor
            </Link>
            <Link to="/alumno" className="boton-secundario px-6 py-3">
              Entrar como alumno
            </Link>
          </Aparece>
        </div>
      </section>

      <footer className="border-t border-borde bg-blanco">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6 py-6 text-xs text-gris">
          <span className="flex items-center gap-2.5">
            <Isotipo className="h-4" />
            Livy · Hackday Gemma 4 · Google Developer Group CDMX 2026
          </span>
          <span>El profesor siempre es el autor y el validador.</span>
        </div>
      </footer>
    </div>
  );
}

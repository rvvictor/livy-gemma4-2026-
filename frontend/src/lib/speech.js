// Transcripción en vivo con la Web Speech API del navegador.
//
// Por qué el navegador y no Gemma: los Gemma 4 hospedados en la Gemini API
// aceptan texto, imagen y video pero NO audio; el audio nativo vive en las
// variantes E2B/E4B/12B, que hay que autohospedar con GPU. Dictar en el
// navegador nos da transcripción en español gratis y sin infraestructura, y deja
// a Gemma 4 haciendo lo que sí es insustituible: entender la clase.
// El audio nativo de Gemma 4 se demuestra aparte, en el notebook de Kaggle.

const Reconocimiento =
  typeof window !== "undefined" &&
  (window.SpeechRecognition || window.webkitSpeechRecognition);

export function soportaDictado() {
  return Boolean(Reconocimiento);
}

/**
 * Crea un dictado continuo en español de México.
 *
 * Chrome corta el reconocimiento cada pocos segundos de silencio y dispara
 * `onend`; para una clase de 90 minutos hay que reiniciarlo solo, por eso
 * llevamos la bandera `activo` en vez de confiar en el estado interno.
 */
export function crearDictado({ onParcial, onFinal, onError, idioma = "es-MX" }) {
  if (!Reconocimiento) {
    throw new Error("Este navegador no soporta dictado. Usa Chrome o Edge.");
  }

  const motor = new Reconocimiento();
  motor.lang = idioma;
  motor.continuous = true;
  motor.interimResults = true;
  motor.maxAlternatives = 1;

  let activo = false;

  motor.onresult = (evento) => {
    let parcial = "";
    for (let i = evento.resultIndex; i < evento.results.length; i += 1) {
      const resultado = evento.results[i];
      const texto = resultado[0].transcript.trim();
      if (!texto) continue;
      if (resultado.isFinal) {
        onFinal?.(texto);
      } else {
        parcial += ` ${texto}`;
      }
    }
    onParcial?.(parcial.trim());
  };

  motor.onerror = (evento) => {
    // "no-speech" y "aborted" son ruido normal en una clase con pausas.
    if (evento.error === "no-speech" || evento.error === "aborted") return;
    onError?.(evento.error);
  };

  motor.onend = () => {
    if (!activo) return;
    try {
      motor.start();
    } catch {
      // Si Chrome todavía no libera el micrófono, reintentamos en un instante.
      setTimeout(() => {
        if (activo) {
          try {
            motor.start();
          } catch {
            /* se abandona el reinicio; el profesor puede volver a iniciar */
          }
        }
      }, 400);
    }
  };

  return {
    iniciar() {
      if (activo) return;
      activo = true;
      motor.start();
    },
    detener() {
      activo = false;
      motor.stop();
    },
  };
}

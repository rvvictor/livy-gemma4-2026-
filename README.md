# Livy — asistente de continuidad docente

**Hackday Gemma 4 · Google Developer Group CDMX · 2026**
**Categoría:** El futuro de la educación

Livy convierte cada clase en memoria estructurada y lleva, de forma automática e
independiente, **la bitácora de avance de cada grupo** contra el plan de estudios.

---

## El problema

Un profesor rara vez da una sola clase: imparte la misma materia a varios grupos y
cada uno avanza a distinto ritmo. El 1CV1 ya vio cálculo de límites; el 2CV2 se
quedó en composición de funciones porque hubo puente; el 3CV3 perdió media sesión
por un simulacro y dejó un tema a medias.

Hoy ese seguimiento vive en la cabeza del profesor, en una libreta, o se pierde.
Cuando falta un día o cierra una semana de seis grupos distintos, **pierde el hilo
de dónde quedó exactamente cada sección** y qué le falta a cada una para cumplir el
programa.

Las herramientas de IA para docentes que ya existen —generadores de planes de
clase, analizadores de participación— documentan clases *aisladas*. Ninguna
resuelve la **continuidad a lo largo del tiempo y entre secciones paralelas**.
Ese hueco es lo que Livy ataca.

El contexto lo hace urgente: según el informe OECD TALIS 2024, apenas el 52% del
tiempo docente se dedica realmente a enseñar, y el trabajo administrativo excesivo
es la principal fuente de estrés laboral docente a nivel global. Los profesores que
usan IA de forma semanal recuperan alrededor de 5.9 horas por semana —unas 6
semanas por ciclo escolar (Gallup / Walton Family Foundation, 2025)—.

## Qué hace

La aplicación tiene dos caras con rutas separadas: `/profesor` y `/alumno`.

### Lado del profesor

| Pantalla | Ruta | Qué resuelve |
| :--- | :--- | :--- |
| **Bitácora** | `/profesor/bitacora` | Agenda de la semana en una sola fila con el tema que toca en cada clase, el siguiente paso sugerido por sección, y el mapa comparativo del plan |
| **Clase en vivo** | `/profesor/clase` | Hilo de conversación: transcribe la sesión, permite preguntarle a Livy en medio de la clase y al cerrar genera la memoria estructurada |
| **Plan de estudios** | `/profesor/plan` | El ciclo completo —todas las materias, sus secciones y su avance— y la carga del temario por visión |
| **Portal de alumnos** | `/profesor/alumnos` | Vista de administrador de lo que reciben sus grupos, con el registro de lo que preguntaron |
| **Datos** | `/profesor/datos` | La salida de todo lo que entró por visión: borrar materias, planes, secciones, clases grabadas y dudas, o dejar la base en blanco |

### Lado del alumno

| Pantalla | Ruta | Qué resuelve |
| :--- | :--- | :--- |
| **Mis materias** | `/alumno` | Todas las secciones a las que pertenece |
| **Clases del grupo** | `/alumno/:grupoId` | Listado de sesiones y chat de dudas sobre todo el curso |
| **Una clase** | `/alumno/clase/:sesionId` | Liga propia por sesión: resumen extenso, transcripción completa y chat acotado a esa clase |

### La misma página, dos lecturas

Las tres vistas del portal son **el mismo componente** con un parámetro de modo.
Lo único que cambia es el panel lateral, y ese detalle es lo que le da su valor a
cada rol:

- El **alumno** tiene un chat. En el listado del grupo pregunta sobre todo el
  curso; dentro de una clase, sobre esa sesión únicamente.
- El **profesor** ve el reverso: en el listado, las dudas generales de su grupo;
  dentro de una clase, lo que se preguntó de esa sesión. Es un diagnóstico de
  dónde falló la explicación, sin tener que encuestar a nadie.

Las **guías de estudio** las genera cualquiera de los dos roles con el mismo
endpoint. Se abren como un cambio de vista dentro de la misma página y se
descargan en PDF a través del diálogo de impresión, contra una hoja de estilos
dedicada: el archivo conserva texto seleccionable y se pagina solo, sin arrastrar
una librería de generación de PDF al paquete.

---

## Cómo se usa Gemma 4

Gemma 4 no es un accesorio del proyecto: es el motor de todo el trabajo cognitivo.
Cada llamada pasa por [`backend/app/gemma.py`](backend/app/gemma.py), y todos los
prompts viven juntos en [`backend/app/prompts.py`](backend/app/prompts.py) para que
sea auditable qué se le pide al modelo en cada función.

| Función del producto | Capacidad de Gemma 4 | Dónde |
| :--- | :--- | :--- |
| Leer el temario de una foto o un PDF | **Visión** → JSON estructurado | `routers/temario.py` |
| Resumir la clase en memoria estructurada | **Razonamiento** sobre transcripción cruda | `routers/sesiones.py` |
| Mapear lo dicho contra el plan de estudios | **Salida estructurada** con nivel de cobertura por tema | `routers/sesiones.py` |
| Recomendar el siguiente tema **por sección** | **Razonamiento comparativo** entre grupos y sesiones restantes | `routers/bitacora.py` |
| Consulta del profesor en medio de la clase | **Razonamiento** sobre la transcripción parcial en curso | `routers/sesiones.py` |
| Chat del alumno anclado a sus clases | **Contexto de 256K** con el historial completo del grupo | `routers/alumno.py` |
| Chat acotado a una sola sesión | Contexto reducido a esa clase para no mezclar el semestre | `routers/alumno.py` |
| Guía de estudio a demanda | Síntesis de las clases reales del grupo | `routers/alumno.py` |
| **Transcripción de audio** | **Audio nativo de Gemma 4 E2B** | [`notebook/gemma4_audio_asr.ipynb`](notebook/gemma4_audio_asr.ipynb) |

### La restricción que definió la arquitectura

Las variantes de Gemma 4 hospedadas gratis en la Gemini API (`gemma-4-31b-it`,
`gemma-4-26b-a4b-it`) aceptan **texto, imagen y video, pero no audio**. El audio
nativo existe solo en E2B, E4B y 12B, que hay que autohospedar con GPU.

El equipo con el que se construyó este proyecto es un Ryzen 7 4700U sin GPU
dedicada. Ante eso:

- **La app transcribe con la Web Speech API del navegador** (`es-MX`, gratis, sin
  infraestructura). La demo en vivo no depende de inferencia local y no se cae.
- **Todo el razonamiento corre sobre `gemma-4-31b-it`.**
- **El audio nativo de Gemma 4 se demuestra de verdad** en el notebook de Kaggle,
  con `gemma-4-E2B-it` sobre GPU gratuita, transcribiendo español sin ningún ASR
  externo y produciendo la misma memoria estructurada que consume la app.

Es una decisión de ingeniería documentada, no una omisión.

### Dos decisiones técnicas que vale la pena defender

**Sin RAG y sin base vectorial.** El historial completo de un grupo en un semestre
cabe holgadamente en los 256K tokens de contexto de Gemma 4, así que el chat del
alumno recibe el corpus íntegro en vez de fragmentos recuperados. Elimina
embeddings, una base vectorial entera y —sobre todo— el fallo de recuperación.
Ver `historial_de_clases()` en [`backend/app/avance.py`](backend/app/avance.py).

**SQLite en vez de PostgreSQL.** Mismo SQL, cero operación durante un sprint de un
día, y el disco del tier gratuito de Render es efímero de todos modos. Migrar a
Postgres es cambiar `DATABASE_URL`.

---

## Arquitectura

```
Navegador (React + Tailwind · Vercel)
   │  Web Speech API es-MX ──► transcripción en vivo
   ▼
FastAPI (Render) ──► gemma.py ──► Gemini API · gemma-4-31b-it
   │
   └──► SQLite · avance por grupo, sesiones, temario

Kaggle Notebook (GPU) ──► gemma-4-E2B-it ──► ASR nativo de Gemma 4
```

### El modelo de datos, en una línea

La pieza que define al producto es `Cobertura`: cada sesión deja registros de qué
temas se tocaron **y en qué grupo**, con un nivel (`introducido`, `cubierto`,
`reforzado`). El avance se calcula siempre por sección, nunca por materia.

### Control del tier gratuito

La Gemini API permite 15 solicitudes por minuto sobre Gemma 4. `gemma.py`
implementa un limitador de ventana deslizante que **permite ráfagas cortas** —para
que la interfaz se sienta ágil— sin rebasar nunca el límite, y degrada solo si el
endpoint rechaza `system_instruction` o la salida JSON nativa.

---

## Correr el proyecto en local

Necesitas una clave gratuita de [Google AI Studio](https://aistudio.google.com/apikey).

### Backend

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

En Linux o macOS, activa con `source .venv/bin/activate`. Pon tu `GEMINI_API_KEY`
dentro del `.env` recién copiado.

La base se crea y se siembra sola al arrancar: una materia con tres grupos
deliberadamente desfasados. La API queda documentada en `http://localhost:8000/docs`.

Sin clave, el backend arranca en **modo simulado** y devuelve respuestas de relleno:
sirve para trabajar la interfaz sin gastar cuota (`LIVY_FAKE_GEMMA=1`).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. Para la clase en vivo usa **Chrome o Edge**: la Web
Speech API no está disponible en todos los navegadores.

---

## Despliegue

**Backend en Render** — el repositorio incluye [`backend/render.yaml`](backend/render.yaml).
Crea el servicio apuntando a este repo con `rootDir: backend` y captura
`GEMINI_API_KEY` en el panel (nunca en el archivo).

**Frontend en Vercel** — importa el repo con **Root Directory `frontend`** y define
la variable `VITE_API_URL` con la URL pública del servicio de Render.

---

## Estructura

```
backend/
  app/
    gemma.py        Único punto de contacto con Gemma 4
    prompts.py      Todos los prompts, juntos y auditables
    avance.py       Cálculo del avance por sección
    borrado.py      Cascadas de borrado, para no dejar registros huérfanos
    models.py       Materia · Tema · Grupo · Sesion · Cobertura · MensajeChat
    seed.py         Dos materias conectadas y cinco grupos desfasados
    routers/
      temario.py       Lectura del plan por visión
      sesiones.py      Clase en vivo, consulta al vuelo y cierre
      bitacora.py      Avance comparativo y recomendaciones
      profesor.py      Agenda semanal y vista del ciclo completo
      alumno.py        Clases, dudas y los dos alcances de chat
      mantenimiento.py Todo lo que borra, junto y auditable de una sentada
frontend/
  public/           favicon.png · livy-og.png
  src/
    theme.css       Paleta guinda y animaciones
    img/            livy.png (original) y las versiones sin fondo que usa la app
    lib/speech.js   Dictado continuo en es-MX
    lib/api.js      Cliente HTTP
    pages/
      Landing.jsx
      profesor/     Bitacora · ClaseEnVivo · PlanDeEstudios · Datos
      alumno/       Indice · Grupo · Clase · ChatGeneral
notebook/
  gemma4_audio_asr.ipynb   Audio nativo de Gemma 4 E2B sobre GPU
```

### Los datos de demostración cuentan la historia

Una profesora con **dos materias conectadas** —Cálculo Diferencial y Geometría
Analítica, donde el grupo 1CV1 lleva las dos— y **cinco secciones en cinco puntos
distintos del plan**: una al corriente, una que perdió una sesión por un puente y
otra que dejó un tema a medias por un simulacro de evacuación.

Las fechas se generan relativas al día en que se ejecuta, de modo que la agenda
semanal siempre tiene clases ya impartidas y clases pendientes.

---

## Límites conocidos

- El dictado del navegador depende de Chrome/Edge y de conexión a internet.
- No hay autenticación: es un prototipo de hackday con datos de demostración.
- El disco de Render es efímero en el tier gratuito; los datos se resiembran al
  reiniciar el servicio, salvo que se haya vaciado la base a propósito desde
  `/profesor/datos` —esa decisión sí queda marcada y se respeta al arrancar.
- Los borrados no piden autenticación, como el resto de la API: se protegen con
  un diálogo de confirmación en la interfaz, no con permisos.
- El troceo de audio del notebook pierde el contexto entre tramos consecutivos.

## Licencia

MIT. Gemma 4 se distribuye bajo Apache 2.0.

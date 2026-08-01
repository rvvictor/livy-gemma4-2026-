"""Datos de demostración.

La siembra cuenta la historia del producto: **una misma materia, tres grupos,
tres puntos distintos del temario**. El 1CV1 va al corriente, el 2CV2 perdió una
sesión por un puente y el 3CV3 se quedó a medias de un tema por un simulacro.
Ese desfase es exactamente lo que hoy vive solo en la cabeza del profesor.

En Render el disco es efímero, así que esto se ejecuta en cada arranque si la base
está vacía.
"""

from __future__ import annotations

import json
from datetime import date

from sqlmodel import Session, select

from .db import motor
from .models import Cobertura, Grupo, Materia, Sesion, Tema

TEMARIO: list[tuple[str, str, list[str]]] = [
    ("Unidad 1. Números reales", "Los números reales y desigualdades",
     ["Propiedades de orden", "Intervalos", "Desigualdades lineales y cuadráticas"]),
    ("Unidad 1. Números reales", "Valor absoluto",
     ["Definición y propiedades", "Desigualdades con valor absoluto", "Distancia en la recta"]),
    ("Unidad 2. Funciones", "Concepto de función",
     ["Dominio y rango", "Notación funcional", "Gráfica de una función"]),
    ("Unidad 2. Funciones", "Tipos de funciones y transformaciones",
     ["Algebraicas y trascendentes", "Funciones par e impar", "Traslaciones y reflexiones"]),
    ("Unidad 2. Funciones", "Álgebra de funciones y composición",
     ["Suma, producto y cociente", "Composición", "Función inversa"]),
    ("Unidad 3. Límites", "Noción intuitiva de límite",
     ["Aproximación numérica", "Límite por tablas y gráficas", "Notación de límite"]),
    ("Unidad 3. Límites", "Cálculo de límites",
     ["Leyes de los límites", "Indeterminación 0/0", "Factorización y racionalización"]),
    ("Unidad 3. Límites", "Límites laterales e infinitos",
     ["Límites laterales", "Asíntotas verticales", "Límites al infinito"]),
    ("Unidad 3. Límites", "Continuidad",
     ["Definición de continuidad", "Tipos de discontinuidad", "Teorema del valor intermedio"]),
    ("Unidad 4. La derivada", "La derivada",
     ["Razón de cambio", "Definición por límite", "Interpretación geométrica"]),
    ("Unidad 4. La derivada", "Reglas de derivación",
     ["Potencia, producto y cociente", "Regla de la cadena", "Derivadas de orden superior"]),
    ("Unidad 5. Aplicaciones", "Aplicaciones de la derivada",
     ["Máximos y mínimos", "Criterio de la primera derivada", "Optimización"]),
]

# (fecha, título, [(orden_tema, nivel)], resumen, puntos_clave, dónde_quedó, pendientes, transcripción)
Clase = tuple[str, str, list[tuple[int, str]], str, list[str], str, list[str], str]

CLASES: dict[str, list[Clase]] = {
    "1CV1": [
        ("2026-07-06", "Desigualdades y notación de intervalos", [(1, "cubierto")],
         "Arrancamos el curso con las propiedades de orden de los números reales y la "
         "notación de intervalos. Se resolvieron desigualdades lineales y una cuadrática "
         "por el método de la recta numérica con puntos críticos.",
         ["Al multiplicar por un negativo se invierte el sentido de la desigualdad",
          "La solución de una desigualdad es un conjunto, no un número",
          "Los puntos críticos parten la recta en regiones de signo constante"],
         "Terminamos con la desigualdad cuadrática x²-5x+6>0 resuelta por regiones.",
         ["Traer ejercicios 1 a 15 de la guía"],
         "Buenos días. Vamos a empezar Cálculo con algo que ya vieron en el propedéutico pero "
         "que aquí usamos todo el semestre: desigualdades. Si a es menor que b y multiplico "
         "ambos lados por menos dos, el sentido se invierte, eso es lo que más se les olvida. "
         "La notación de intervalo abierto usa paréntesis, el cerrado usa corchete. Ahora "
         "x cuadrada menos cinco x más seis mayor que cero. Factorizo: x menos dos por x menos "
         "tres. Los puntos críticos son dos y tres. Pruebo un valor en cada región y me quedo "
         "con las que dan positivo: menos infinito a dos, unión, tres a infinito."),
        ("2026-07-08", "Valor absoluto y distancia", [(2, "cubierto")],
         "Se definió el valor absoluto como distancia al origen y se resolvieron "
         "desigualdades del tipo |x-a|<r interpretándolas geométricamente.",
         ["|x| es la distancia de x al cero, nunca es negativo",
          "|x-a|<r equivale a que x esté a menos de r unidades de a",
          "|x|>r se parte en dos casos"],
         "Quedamos en la interpretación geométrica de |x-3|<2 como el intervalo (1,5).",
         [],
         "El valor absoluto no es quitar el signo, es la distancia al origen. Si les digo "
         "valor absoluto de x menos tres menor que dos, no memoricen la fórmula: pregúntense "
         "qué números están a menos de dos unidades del tres. Del uno al cinco. Ya está, ese "
         "es el intervalo. Cuando es mayor que, es al revés, se van para afuera y son dos "
         "intervalos separados."),
        ("2026-07-13", "Concepto de función, dominio y rango", [(3, "cubierto")],
         "Definición de función como regla de correspondencia, criterio de la recta vertical, "
         "y cálculo de dominio para funciones con radical y con denominador.",
         ["Una función asigna a cada entrada exactamente una salida",
          "El dominio se restringe donde el denominador se anula o el radicando es negativo",
          "El criterio de la recta vertical decide si una gráfica es función"],
         "Terminamos calculando el dominio de f(x)=√(x-4)/(x-7).",
         ["Repasar dominios con radical par"],
         "Una función es una regla que a cada entrada le asigna una y solo una salida. Si "
         "trazo una recta vertical y toca la gráfica dos veces, no es función. Para el dominio "
         "hay dos preguntas: qué anula el denominador y qué hace negativo lo de adentro de una "
         "raíz par. En raíz de x menos cuatro sobre x menos siete, necesito x mayor o igual "
         "que cuatro, pero además x distinto de siete. El dominio es de cuatro a siete, unión, "
         "siete a infinito."),
        ("2026-07-15", "Tipos de funciones y transformaciones", [(4, "cubierto")],
         "Clasificación entre funciones algebraicas y trascendentes, paridad, y el efecto de "
         "las traslaciones y reflexiones sobre la gráfica.",
         ["f(x)+c sube la gráfica, f(x+c) la mueve a la izquierda",
          "Una función par es simétrica respecto al eje y; una impar, respecto al origen",
          "El signo menos por fuera refleja sobre el eje x"],
         "Quedamos graficando f(x)=-(x+2)²+3 por transformaciones sucesivas.",
         [],
         "Fíjense en lo contraintuitivo: el más c por dentro mueve la gráfica a la izquierda, "
         "no a la derecha. Con la parábola menos x más dos al cuadrado más tres: parto de x "
         "cuadrada, la corro dos a la izquierda, la reflejo porque hay un menos, y la subo "
         "tres. El vértice queda en menos dos, tres, y abre hacia abajo."),
        ("2026-07-20", "Álgebra de funciones y composición", [(5, "cubierto")],
         "Operaciones entre funciones, composición y su dominio, e introducción a la función "
         "inversa a partir del criterio de la recta horizontal.",
         ["El dominio de f∘g exige que g(x) esté en el dominio de f",
          "La composición no es conmutativa",
          "Solo las funciones inyectivas tienen inversa"],
         "Cerramos con f∘g y g∘f para f(x)=√x y g(x)=x-3, comparando dominios.",
         ["Ejercicios de composición de la guía"],
         "Componer no es multiplicar. F de g de x significa que primero aplico g y el "
         "resultado se lo doy a f. Con f igual a raíz de x y g igual a x menos tres, f de g "
         "de x es raíz de x menos tres, y su dominio es x mayor o igual que tres. Al revés, "
         "g de f de x es raíz de x menos tres, con dominio x mayor o igual que cero. Distinto "
         "resultado y distinto dominio: por eso el orden importa."),
        ("2026-07-22", "Noción intuitiva de límite", [(6, "cubierto")],
         "Aproximación numérica por tablas y lectura gráfica del límite. Se insistió en que "
         "el límite describe la tendencia, no el valor de la función en el punto.",
         ["El límite no exige que la función esté definida en el punto",
          "Se puede aproximar por tablas desde ambos lados",
          "Si los lados no coinciden, el límite no existe"],
         "Terminamos con la tabla de (x²-1)/(x-1) acercándose a 1 desde ambos lados.",
         [],
         "El límite pregunta a dónde tiende la función cuando x se acerca, no cuánto vale "
         "cuando llega. En x cuadrada menos uno sobre x menos uno, si sustituyo uno me da cero "
         "sobre cero, indefinido. Pero hago la tabla: con nueve décimos me da uno punto nueve, "
         "con noventa y nueve centésimos me da uno punto noventa y nueve. Por arriba, igual. "
         "La función tiende a dos aunque en el uno tenga un hoyo."),
        ("2026-07-27", "Leyes de los límites e indeterminación 0/0", [(7, "cubierto")],
         "Se enunciaron las leyes de los límites y se trabajó la indeterminación 0/0 con "
         "factorización y con racionalización del numerador.",
         ["0/0 no es un resultado, es una señal de que hay que transformar la expresión",
          "Factorizar y cancelar el factor problemático resuelve la mayoría de los casos",
          "Con raíces se multiplica por el conjugado"],
         "Cerramos con lím(x→0) (√(x+9)-3)/x resuelto por conjugado, que da 1/6.",
         ["Estudiar racionalización para la próxima"],
         "Cuando sustituyen y les sale cero sobre cero, eso no es la respuesta, es un aviso: "
         "hay un factor común escondido. En raíz de x más nueve menos tres, sobre x, multiplico "
         "arriba y abajo por el conjugado, raíz de x más nueve más tres. Arriba me queda x más "
         "nueve menos nueve, o sea x, y se cancela con la x de abajo. Queda uno sobre raíz de "
         "x más nueve más tres, sustituyo cero y da uno sobre seis. La próxima clase vemos "
         "límites laterales, que es donde se decide si el límite existe o no."),
    ],
    "2CV2": [
        ("2026-07-07", "Desigualdades y notación de intervalos", [(1, "cubierto")],
         "Propiedades de orden, intervalos y desigualdades lineales y cuadráticas resueltas "
         "por regiones en la recta numérica.",
         ["Multiplicar por un negativo invierte la desigualdad",
          "La solución es un conjunto de números",
          "Los puntos críticos definen las regiones de prueba"],
         "Terminamos con desigualdades cuadráticas por el método de regiones.",
         [],
         "Propiedades de orden primero. Si multiplican por un número negativo, el símbolo se "
         "voltea. Notación de intervalos: paréntesis para abierto, corchete para cerrado. Con "
         "la cuadrática factorizo, saco puntos críticos y pruebo signos por región."),
        ("2026-07-09", "Valor absoluto", [(2, "cubierto")],
         "Valor absoluto como distancia, propiedades y desigualdades con valor absoluto.",
         ["|x| es distancia al origen", "|x-a|<r es un intervalo centrado en a",
          "El caso 'mayor que' produce dos intervalos"],
         "Quedamos resolviendo |2x-1|≥5.",
         [],
         "Valor absoluto es distancia, no es quitar signos. Menor que se convierte en un "
         "intervalo centrado; mayor que se abre en dos. En dos x menos uno, mayor o igual que "
         "cinco, planteo los dos casos y me quedan dos rayos."),
        ("2026-07-14", "Concepto de función, dominio y rango", [(3, "cubierto")],
         "Definición de función, criterio de la recta vertical y cálculo de dominios con "
         "radicales y denominadores.",
         ["Cada entrada tiene exactamente una salida",
          "Denominador distinto de cero y radicando no negativo",
          "El rango se lee en el eje vertical"],
         "Terminamos con el dominio de funciones racionales con radical.",
         ["Repasar factorización para dominios"],
         "Función es una regla que asigna una sola salida a cada entrada. Recta vertical para "
         "verificar. Para el dominio, dos preguntas: qué anula el denominador y qué vuelve "
         "negativo el radicando de una raíz par."),
        ("2026-07-16", "Tipos de funciones y transformaciones", [(4, "cubierto")],
         "Clasificación de funciones, paridad y transformaciones de la gráfica.",
         ["f(x)+c traslada verticalmente", "f(x+c) traslada horizontalmente en sentido opuesto",
          "Par es simétrica al eje y, impar al origen"],
         "Cerramos graficando parábolas por transformaciones.",
         [],
         "El más c por dentro mueve a la izquierda, es lo que siempre confunde. Par significa "
         "simetría respecto al eje y; impar, respecto al origen. Practiquen graficando "
         "parábolas corridas y reflejadas."),
        ("2026-07-23", "Álgebra de funciones y composición", [(5, "cubierto")],
         "Operaciones entre funciones y composición, con énfasis en el dominio del resultado. "
         "La sesión del 21 se perdió por el puente, así que se retomó con un repaso breve de "
         "dominios antes de entrar al tema.",
         ["f∘g exige que g(x) caiga en el dominio de f",
          "La composición no es conmutativa",
          "El dominio de la composición puede ser más chico que el de ambas"],
         "Terminamos con el dominio de f∘g para f(x)=1/x y g(x)=x-2. Falta la función inversa.",
         ["Ver función inversa la próxima sesión", "Recuperar el ritmo perdido por el puente"],
         "Perdimos la del martes por el puente, así que vamos a apretar un poco. Repaso "
         "rápido de dominios y entramos a composición. F de g de x quiere decir que primero "
         "aplico g. Con f igual a uno sobre x y g igual a x menos dos, la composición es uno "
         "sobre x menos dos, y el dominio excluye el dos. Nos faltó función inversa, la vemos "
         "la próxima clase antes de entrar a límites."),
    ],
    "3CV3": [
        ("2026-07-06", "Desigualdades y notación de intervalos", [(1, "cubierto")],
         "Propiedades de orden, intervalos y desigualdades resueltas por regiones.",
         ["El sentido se invierte al multiplicar por negativos",
          "La solución es un conjunto", "Puntos críticos y prueba de signos"],
         "Terminamos con desigualdades cuadráticas.",
         [],
         "Orden en los reales, notación de intervalos y desigualdades. Con la cuadrática, "
         "factorizo, ubico puntos críticos y pruebo el signo en cada región."),
        ("2026-07-10", "Valor absoluto y distancia", [(2, "cubierto")],
         "Valor absoluto como distancia al origen y desigualdades asociadas.",
         ["|x| nunca es negativo", "|x-a|<r es un intervalo centrado",
          "Mayor que abre dos intervalos"],
         "Quedamos en la interpretación geométrica de las desigualdades.",
         [],
         "Piénsenlo como distancia. Valor absoluto de x menos tres menor que dos son los "
         "números a menos de dos unidades del tres, o sea del uno al cinco."),
        ("2026-07-13", "Concepto de función, dominio y rango", [(3, "cubierto")],
         "Definición de función, recta vertical y cálculo de dominios.",
         ["Una salida por entrada", "Denominador no nulo, radicando no negativo",
          "Rango en el eje vertical"],
         "Terminamos con dominios de funciones con radical.",
         [],
         "Función, dominio y rango. Recta vertical para verificar si una gráfica lo es. "
         "Dominio: cuidado con denominadores y con raíces pares."),
        ("2026-07-17", "Transformaciones y álgebra de funciones", [(4, "cubierto"), (5, "cubierto")],
         "Se juntaron transformaciones y álgebra de funciones en una sola sesión para "
         "compensar el ritmo. Se cubrió composición y su dominio.",
         ["f(x+c) traslada en sentido contrario al signo",
          "La composición no es conmutativa",
          "El dominio de la composición se hereda de ambas funciones"],
         "Cerramos con composiciones y sus dominios; la función inversa quedó apenas mencionada.",
         ["Retomar función inversa con calma"],
         "Vamos a ver dos temas hoy porque traemos el calendario apretado. Transformaciones: "
         "el más c por dentro corre a la izquierda. Y componer no es multiplicar: f de g de x "
         "significa aplicar primero g. Con raíz de x y x menos tres, la composición es raíz de "
         "x menos tres con dominio x mayor o igual que tres. De inversa solo les adelanto que "
         "necesita que la función sea inyectiva, lo vemos bien después."),
        ("2026-07-20", "Noción intuitiva de límite", [(6, "cubierto")],
         "Aproximación numérica y gráfica al concepto de límite, con tablas desde ambos lados.",
         ["El límite es tendencia, no el valor en el punto",
          "Se aproxima desde la izquierda y desde la derecha",
          "Si los lados difieren, el límite no existe"],
         "Terminamos con la tabla de (x²-1)/(x-1) cerca de x=1.",
         [],
         "El límite pregunta hacia dónde va la función, no cuánto vale al llegar. En x "
         "cuadrada menos uno sobre x menos uno, sustituir uno da cero sobre cero. Pero la "
         "tabla muestra que se acerca a dos por los dos lados. Hay un hueco en la gráfica, "
         "pero el límite existe y vale dos."),
        ("2026-07-24", "Inicio de leyes de los límites (sesión interrumpida)", [(7, "introducido")],
         "La sesión se cortó a los veinte minutos por el simulacro de evacuación. Solo alcanzó "
         "a enunciarse la lista de leyes de los límites y a plantearse la indeterminación 0/0, "
         "sin resolver ningún ejercicio completo.",
         ["Las leyes permiten separar límites de sumas, productos y cocientes",
          "0/0 es una indeterminación, no un resultado"],
         "Quedamos justo en el planteamiento de 0/0, sin alcanzar a resolver ejemplos.",
         ["Retomar cálculo de límites desde el principio",
          "Falta por completo factorización y racionalización"],
         "Antes de que suene la alarma del simulacro les dejo planteadas las leyes de los "
         "límites: el límite de una suma es la suma de los límites, y lo mismo con producto y "
         "cociente, siempre que el de abajo no sea cero. Cuando al sustituir les salga cero "
         "sobre cero, eso es una indeterminación, no una respuesta. Ahí es donde entra "
         "factorizar o racionalizar, pero eso ya no nos va a dar tiempo... ahí está la alarma. "
         "Salgan en orden por la puerta de atrás, seguimos la próxima clase."),
    ],
}

GRUPOS = [
    ("1CV1", "Lunes y miércoles, 07:00–08:30", 42),
    ("2CV2", "Martes y jueves, 12:30–14:00", 38),
    ("3CV3", "Lunes y viernes, 18:00–19:30", 45),
]


def sembrar_si_esta_vacia() -> None:
    """Crea la materia de demostración solo si no hay nada en la base."""
    with Session(motor) as db:
        if db.exec(select(Materia)).first():
            return

        materia = Materia(
            nombre="Cálculo Diferencial",
            profesor="Ing. Leticia Ramírez",
            ciclo="2026/1",
            sesiones_planeadas=32,
        )
        db.add(materia)
        db.commit()
        db.refresh(materia)

        temas_por_orden: dict[int, Tema] = {}
        for indice, (unidad, titulo, subtemas) in enumerate(TEMARIO, start=1):
            tema = Tema(
                materia_id=materia.id,
                orden=indice,
                unidad=unidad,
                titulo=titulo,
                subtemas_json=json.dumps(subtemas, ensure_ascii=False),
            )
            db.add(tema)
            temas_por_orden[indice] = tema
        db.commit()
        for tema in temas_por_orden.values():
            db.refresh(tema)

        for nombre, horario, alumnos in GRUPOS:
            grupo = Grupo(
                materia_id=materia.id, nombre=nombre, horario=horario, alumnos=alumnos
            )
            db.add(grupo)
            db.commit()
            db.refresh(grupo)

            for clase in CLASES.get(nombre, []):
                (
                    fecha,
                    titulo,
                    coberturas,
                    resumen,
                    puntos,
                    donde_quedo,
                    pendientes,
                    transcripcion,
                ) = clase

                sesion = Sesion(
                    grupo_id=grupo.id,
                    fecha=date.fromisoformat(fecha),
                    estado="cerrada",
                    titulo=titulo,
                    transcripcion=transcripcion,
                    duracion_min=90,
                    resumen_json=json.dumps(
                        {
                            "titulo": titulo,
                            "resumen": resumen,
                            "puntos_clave": puntos,
                            "donde_quedo": donde_quedo,
                            "pendientes": pendientes,
                            "dudas_detectadas": [],
                        },
                        ensure_ascii=False,
                    ),
                )
                db.add(sesion)
                db.commit()
                db.refresh(sesion)

                for orden, nivel in coberturas:
                    db.add(
                        Cobertura(
                            sesion_id=sesion.id,
                            grupo_id=grupo.id,
                            tema_id=temas_por_orden[orden].id,
                            nivel=nivel,
                            evidencia=transcripcion[:200],
                        )
                    )
                db.commit()
